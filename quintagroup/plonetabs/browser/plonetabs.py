import copy, sys
from Acquisition import aq_inner
from OFS.CopySupport import CopyError

from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory
from zope.exceptions import UserError
from zope.app.container.interfaces import INameChooser

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IAction, IActionCategory
from Products.CMFCore.ActionInformation import Action, ActionCategory
from Products.CMFCore.Expression import Expression
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import get_view_url
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.workflow.remap import remap_workflow
from plone.memoize.instance import memoize
from kss.core import kssaction, KSSExplicitError

from quintagroup.plonetabs.config import *
from interfaces import IPloneTabsControlPanel

ACTION_ATTRS = ["id", "title", "url_expr", "available_expr", "visible"]

class PloneTabsControlPanel(PloneKSSView):
    
    implements(IPloneTabsControlPanel)
    
    template = ViewPageTemplateFile("templates/plonetabs.pt")
    actionslist_template = ViewPageTemplateFile("templates/actionslist.pt")
    autogenerated_template = ViewPageTemplateFile("templates/autogenerated.pt")
    
    # custom templates used to update page sections
    sections_template = ViewPageTemplateFile("templates/sections.pt")
    
    def __call__(self):
        """ Perform the update and redirect if necessary, or render the page """
        postback = True
        errors = {}
        context = aq_inner(self.context)
        
        form = self.request.form
        action = form.get("action", "")
        submitted = form.get('form.submitted', False)
        
        # action handler def handler(self, form)
        if submitted:
            if form.has_key('add.add'):
                postback = self.manage_addAction(form, errors)
            elif form.has_key("edit.save"):
                postback = self.manage_editAction(form, errors)
            elif form.has_key("edit.delete"):
                postback = self.manage_deleteAction(form, errors)
            elif form.has_key("edit.moveup"):
                postback = self.manage_moveUpAction(form, errors)
            elif form.has_key("edit.movedown"):
                postback = self.manage_moveDownAction(form, errors)
            elif form.has_key("autogenerated.save"):
                postback = self.manage_setAutogeneration(form, errors)
            else:
                postback = True
        
        if postback:
            return self.template(errors=errors)
    
    ########################################
    # Methods for processing configlet posts
    ########################################
    
    def manage_setAutogeneration(self, form, errors):
        """ Process managing autogeneration settings """
        
        # set excludeFromNav property for root objects
        portal = getMultiAdapter((aq_inner(self.context), self.request), name='plone_portal_state').portal()
        generated_tabs = form.get("generated_tabs", '0')
        nonfolderish_tabs = form.get("nonfolderish_tabs", '0')
        
        for item in self.getRootTabs():
            obj = getattr(portal, item['id'], None)
            if obj is not None:
                checked = form.get(item['id'], None)
                if checked == '1':
                    obj.update(excludeFromNav=False)
                else:
                    obj.update(excludeFromNav=True)

        # set disable_folder_sections property
        if int(generated_tabs) == 1:
            self.setSiteProperties(disable_folder_sections=False)
        else:
            self.setSiteProperties(disable_folder_sections=True)
        
        # set disable_nonfolderish_sections property
        if int(nonfolderish_tabs) == 1:
            self.setSiteProperties(disable_nonfolderish_sections=False)
        else:
            self.setSiteProperties(disable_nonfolderish_sections=True)
        
        # after successfull form processing make redirect with good message
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved!"), type="info")
        self.redirect()
        return False
    
    def manage_addAction(self, form, errs):
        """ Manage method to add a new action to given category,
            if category doesn't exist, create it """
        # extract posted data
        id, cat_name, data = self.parseAddForm(form)
        
        # validate posted data
        errors = self.validateActionFields(cat_name, data)
        
        # if not errors find (or create) category and set action to it
        if not errors:
            action = self.addAction(cat_name, form)
            IStatusMessage(self.request).addStatusMessage(_(u"'%s' action successfully added." % action.id), type="info")
            self.redirect(search="category=%s" % cat_name)
            return False
        else:
            errs.update(errors)
            IStatusMessage(self.request).addStatusMessage(_(u"Please correct the indicated errors."), type="error")
            return True
    
    def manage_editAction(self, form, errs):
        """ Manage Method to update action """
        # extract posted data
        id, cat_name, data = self.parseEditForm(form)
        
        # get category and action to edit
        category = self.getActionCategory(cat_name)
        action = category[id]
        
        # validate posted data
        errors = self.validateActionFields(cat_name, data, allow_dup=True)
        
        if not errors:
            action = self.updateAction(id, cat_name, data)
            IStatusMessage(self.request).addStatusMessage(_(u"'%s' action saved." % action.id), type="info")
            self.redirect(search="category=%s" % cat_name)
            return False
        else:
            errs.update(self.processErrors(errors, sufix='_%s' % id)) # add edit form sufix to error ids
            IStatusMessage(self.request).addStatusMessage(_(u"Please correct the indicated errors."), type="error")
            return True
    
    def manage_deleteAction(self, form, errs):
        """ Manage Method to delete action """
        # extract posted data
        id, cat_name, data = self.parseEditForm(form)
        
        # get category and action to delete
        category = self.getActionCategory(cat_name)
        if id in category.objectIds():
            self.deleteAction(id, cat_name)
            IStatusMessage(self.request).addStatusMessage(_(u"'%s' action deleted." % id), type="info")
            self.redirect(search="category=%s" % cat_name)
            return False
        else:
            IStatusMessage(self.request).addStatusMessage(_(u"No '%s' action in '%s' category." % (id, cat_name)), type="error")
            return True
    
    def manage_moveUpAction(self, form, errs):
        """ Manage Method for moving up given action by one position """
        # extract posted data
        id, cat_name, data = self.parseEditForm(form)
        
        # get category and action to move
        category = self.getActionCategory(cat_name)
        if id in category.objectIds():
            self.moveAction(id, cat_name, steps=1)
            IStatusMessage(self.request).addStatusMessage(_(u"'%s' action moved up." % id), type="info")
            self.redirect(search="category=%s" % cat_name)
            return False
        else:
            IStatusMessage(self.request).addStatusMessage(_(u"No '%s' action in '%s' category." % (id, cat_name)), type="error")
            return True
    
    def manage_moveDownAction(self, form, errs):
        """ Manage Method for moving down given action by one position """
        # extract posted data
        id, cat_name, data = self.parseEditForm(form)
        
        # get category and action to move
        category = self.getActionCategory(cat_name)
        if id in category.objectIds():
            self.moveAction(id, cat_name, steps=-1)
            IStatusMessage(self.request).addStatusMessage(_(u"'%s' action moved down." % id), type="info")
            self.redirect(search="category=%s" % cat_name)
            return False
        else:
            IStatusMessage(self.request).addStatusMessage(_(u"No '%s' action in '%s' category." % (id, cat_name)), type="error")
            return True
    
    def redirect(self, url="", search="", url_hash=""):
        """ Redirect to @@plonetabs-controlpanel configlet """
        portal_url =  getMultiAdapter((self.context, self.request), name=u"plone_portal_state").portal_url()
        url = (url == "") and "%s/%s" % (portal_url, "@@plonetabs-controlpanel") or url
        search = (search != "") and "?%s" % search or search
        url_hash = (url_hash != "") and "#%s" % url_hash or url_hash
        self.request.response.redirect("%s%s%s" % (url, search, url_hash))
    
    ###################################
    #
    #  Methods - providers for templates
    #
    ###################################
    
    def getPageTitle(self, category="portal_tabs"):
        """ See interface """
        portal_props = getToolByName(self.context, "portal_properties")
        default_title = "Plone '%s' Configuration" % category
        
        if not hasattr(portal_props, PROPERTY_SHEET):
            return default_title
        
        sheet = getattr(portal_props, PROPERTY_SHEET)
        if not hasattr(sheet, FIELD_NAME):
            return default_title
        
        field = sheet.getProperty(FIELD_NAME)
        dict = {}
        for line in field:
            cat, title = line.split("|", 2)
            dict[cat] = title
        
        return dict.get(category, None) or default_title
    
    def hasActions(self, category="portal_tabs"):
        """ See interface """
        return len(getToolByName(self.context, "portal_actions").listActions(categories=[category,])) > 0
    
    def getPortalActions(self, category="portal_tabs"):
        """ See interface """
        portal_actions = getToolByName(self.context, "portal_actions")
        
        if category not in portal_actions.objectIds():
            return []
        
        actions = []
        for item in portal_actions[category].objectValues():
            if IAction.providedBy(item):
                actions.append(item)
        
        return actions
    
    def isGeneratedTabs(self):
        """ See interface """
        site_properties = getToolByName(self.context, "portal_properties").site_properties
        return not site_properties.getProperty("disable_folder_sections", False)
    
    def isNotFoldersGenerated(self):
        """ See interface """
        site_properties = getToolByName(self.context, "portal_properties").site_properties
        return not site_properties.getProperty("disable_nonfolderish_sections", False)
    
    def getActionsList(self, category="portal_tabs", errors={}):
        """ See interface """
        return self.actionslist_template(category=category, errors=errors)
    
    def getGeneratedTabs(self):
        """ See interface """
        return self.autogenerated_template()
    
    def getRootTabs(self):
        """ See interface """
        context = aq_inner(self.context)
        
        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        
        # Build result dict
        result = []
        
        # check whether tabs autogeneration is turned on
        if not self.isGeneratedTabs():
            return result
        
        query = {}
        rootPath = getNavigationRoot(context)
        query['path'] = {'query' : rootPath, 'depth' : 1}
        query['portal_type'] = utils.typesToList(context)
        
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder
        
        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', [])
        
        query['is_default_page'] = False

        if not self.isNotFoldersGenerated():
            query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        idsNotToList = navtree_properties.getProperty('idsNotToList', ())
        excludedIds = {}
        for id in idsNotToList:
            excludedIds[id]=1

        rawresult = portal_catalog.searchResults(**query)

        # now add the content to results
        for item in rawresult:
            if not excludedIds.has_key(item.getId):
                id, item_url = get_view_url(item)
                data = {'name'       : utils.pretty_title_or_id(context, item),
                        'id'         : id,
                        'url'        : item_url,
                        'description': item.Description,
                        'exclude_from_nav' : item.exclude_from_nav}
                result.append(data)
        
        return result
    
    def getCategories(self):
        """ See interface """
        portal_actions = getToolByName(self.context, "portal_actions")
        return portal_actions.objectIds()
    
    #
    # Methods to make this class looks like global sections viewlet
    #
    
    def test(self, condition, ifTrue, ifFalse):
        """ See interface """
        if condition:
            return ifTrue
        else:
            return ifFalse
    
    # methods for rendering global-sections viewlet via kss,
    # due to bug in macroContent when global-section list is empty,
    # ul have condition
    def portal_tabs(self):
        """ See global-sections viewlet """
        actions = context_state = getMultiAdapter((self.context, self.request), name=u"plone_context_state").actions()
        portal_tabs_view = getMultiAdapter((self.context, self.request), name="portal_tabs_view")
        
        return portal_tabs_view.topLevelTabs(actions=actions)
    
    def selected_portal_tab(self):
        """ See global-sections viewlet """
        selectedTabs = self.context.restrictedTraverse('selectedTabs')
        selected_tabs = selectedTabs('index_html', self.context, self.portal_tabs())
        
        return selected_tabs['portal']
    
    ##########################
    #
    # KSS Server Actions
    #
    ##########################
    
    def validateAction(self, id, category, prefix="tabslist_"):
        """ If action with given id and category doesn't exist - raise kss exception """
        portal_actions = getToolByName(self.context, "portal_actions")
        
        # remove prefix, added for making ids on configlet unique ("tabslist_")
        act_id = id[len("tabslist_"):]
        
        if category not in portal_actions.objectIds():
            raise KSSExplicitError, "Unexistent root portal actions category %s" % category
        
        cat_container = portal_actions[category]
        if act_id not in map(lambda x: x.id, filter(lambda x: IAction.providedBy(x), cat_container.objectValues())):
            raise KSSExplicitError, "%s action does not exist in %s category" % (act_id, category)
        
        return (cat_container, act_id)
    
    @kssaction
    def toggleGeneratedTabs(self, field, checked='0'):
        """ Toggle autogenaration setting on configlet """
        
        changeProperties = getToolByName(self.context, "portal_properties").site_properties.manage_changeProperties
        if checked == '1':
            changeProperties(**{field : False})
        else:
            changeProperties(**{field : True})
        
        ksscore = self.getCommandSet("core")
        replace_id = "roottabs"
        content = self.getGeneratedTabs()
        
        ksscore.replaceInnerHTML(ksscore.getHtmlIdSelector(replace_id), content, withKssSetup="True")
        
        # update global-sections viewlet
        self.updatePortalTabs()
    
    @kssaction
    def toggleActionsVisibility(self, id, checked='0', category=None):
        """ Toggle visibility for portal actions """
        portal_actions = getToolByName(self.context, "portal_actions")
        cat_container, act_id = self.validateAction(id, category)
        
        if checked == '1':
            checked = True
        else:
            checked = False
        
        cat_container[act_id].visible = checked
        
        ksscore = self.getCommandSet("core")
        if checked:
            ksscore.removeClass(ksscore.getHtmlIdSelector(id), value="invisible")
        else:
            ksscore.addClass(ksscore.getHtmlIdSelector(id), value="invisible")
        
        self.updatePage(category)
    
    @kssaction
    def toggleRootsVisibility(self, id, checked='0'):
        """ Toggle visibility for portal root objects (exclude_from_nav) """
        portal = getMultiAdapter((aq_inner(self.context), self.request), name='plone_portal_state').portal()
        
        # remove prefix, added for making ids on configlet unique ("roottabs_")
        obj_id = id[len("roottabs_"):]
        
        if obj_id not in portal.objectIds():
            raise KSSExplicitError, "Object with %s id doesn't exist in portal root" % obj_id
        
        if checked == '1':
            checked = True
        else:
            checked = False
        
        portal[obj_id].update(excludeFromNav=not checked)
        
        ksscore = self.getCommandSet("core")
        if checked:
            ksscore.removeClass(ksscore.getHtmlIdSelector(id), value="invisible")
        else:
            ksscore.addClass(ksscore.getHtmlIdSelector(id), value="invisible")
        
        # update global-sections viewlet
        self.updatePortalTabs()
    
    @kssaction
    def kss_deleteAction(self, id, category):
        """ Delete portal action with given id & category """
        portal_actions = getToolByName(self.context, "portal_actions")
        cat_container, act_id = self.validateAction(id, category)
        
        cat_container.manage_delObjects(ids=[act_id,])
        
        # update action list on client
        ksscore = self.getCommandSet("core")
        
        ksscore.deleteNode(ksscore.getHtmlIdSelector(id))
        
        # add "noitems" class to Reorder controls to hide it
        if not filter(lambda x: IAction.providedBy(x), cat_container.objectValues()):
            ksscore.addClass(ksscore.getHtmlIdSelector("reorder"), value="noitems")
        
        # XXX TODO: fade effect during removing, for this kukit js action/command plugin needed
        
        self.updatePage(category)
    
    @kssaction
    def oldAddAction(self, id, name, action='', category='portal_tabs', condition='', visible=False):
        pass
    
    @kssaction
    def editAction(self, id, category):
        """ Show edit form for given action """
        cat_container, act_id = self.validateAction(id, category)
        
        # collect data
        action_info = self.copyAction(cat_container[act_id])
        action_info["editing"] = True
        
        ksscore = self.getCommandSet("core")
        content = self.actionslist_template(tabs=[action_info,])
        replace_id = id
        
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(replace_id), content)
        
        # focus name field
        ksscore.focus(ksscore.getCssSelector("#%s input[name=name_%s]" % (id, act_id)))
    
    @kssaction
    def editCancel(self, id, category):
        """ Hide edit form for given action """
        cat_container, act_id = self.validateAction(id, category)
        
        ksscore = self.getCommandSet("core")
        content = self.actionslist_template(tabs=[cat_container[act_id],])
        replace_id = id
        
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(replace_id), content)
    
    #
    # Utility Methods
    #
    
    def copyAction(self, action):
        """ Copyt action to dictionary """
        action_info = {}
        for attr in ACTION_ATTRS:
            action_info[attr] = getattr(action, attr)
        return action_info
    
    def validateActionFields(self, cat_name, data, allow_dup=False):
        """ Check action fields on validity """
        errors = {}
        
        if allow_dup:
            category = ActionCategory(cat_name)           # create dummy category to avoid id duplication during action update
        else:
            category = self.getOrCreateCategory(cat_name) # get or create (if necessary) actions category
        
        # validate action id
        chooser = INameChooser(category)
        try:
            chooser.checkName(data['id'], self.context)
        except Exception, e:
            errors['id'] = "%s" % str(e)
        
        # validate action name
        if not data['title'].strip():
            errors['title'] = 'Empty or invalid title specified'
        
        # validate condition expression
        if data['available_expr']:
            try:
                Expression(data['available_expr'])
            except Exception, e:
                errors["available_expr"] = "%s" % str(e)
        
        # validate action expression
        if data['url_expr']:
            try:
                Expression(data['url_expr'])
            except Exception, e:
                errors["url_expr"] = "%s" % str(e)
        
        return errors
    
    def processErrors(self, errors, prefix='', sufix=''):
        """ Add prefixes, sufixes to error ids 
            This is necessary during edit form validation,
            because every edit form on the page has it's own sufix (id) """
        if not (prefix or sufix):
            return errors
        
        result = {}
        for key, value in errors.items():
            result['%s%s%s' % (prefix, key, sufix)] = value
        
        return result
    
    def parseEditForm(self, form):
        """ Extract all needed fields from edit form """
        # get original id and category
        info = {}
        id = form['orig_id']
        category = form['category']
        
        # preprocess 'visible' field (checkbox needs special checking)
        if form.has_key('visible_%s' % id):
            form['visible_%s' % id] = True
        else:
            form['visible_%s' % id] = False
        
        # collect all action fields
        for attr in ACTION_ATTRS:
            info[attr] = form['%s_%s' % (attr, id)]
        
        return (id, category, info)
    
    def parseAddForm(self, form):
        """ Extract all needed fields from add form """
        info = {}
        id = form['id']
        category = form['category']
        
        # preprocess 'visible' field (checkbox needs special checking)
        if form.has_key('visible'):
            form['visible'] = True
        else:
            form['visible'] = False
        
        # collect all action fields
        for attr in ACTION_ATTRS:
            info[attr] = form[attr]
        
        return (id, category, info)
    
    def getActionCategory(self, name):
        portal_actions = getToolByName(self.context, 'portal_actions')
        return portal_actions[name]
    
    def getOrCreateCategory(self, name):
        """ Get or create (if necessary) category """
        portal_actions = getToolByName(self.context, 'portal_actions')
        if name not in map(lambda x: x.id, filter(lambda x: IActionCategory.providedBy(x), portal_actions.objectValues())):
            portal_actions._setObject(name, ActionCategory(name))
        return self.getActionCategory(name)
    
    def setSiteProperties(self, **kw):
        """ Change site_properties """
        site_properties = getToolByName(self.context, "portal_properties").site_properties
        site_properties.manage_changeProperties(**kw)
        return True
    
    #
    # Basic API to work with portal actions tool in a more pleasent way
    #
    
    def addAction(self, cat_name, data):
        """ Create and add new action to category with given name """
        id = data.pop('id')
        category = self.getOrCreateCategory(cat_name)
        action = Action(id, **data)
        category._setObject(id, action)
        return action
    
    def updateAction(self, id, cat_name, data):
        """ Update action with given id and category """
        new_id = data.pop('id')
        category = self.getActionCategory(cat_name)
        
        # rename action if necessary
        if id != new_id:
            category.manage_renameObject(id, new_id)
        
        # get action
        action = category[new_id]
        
        # update action properties
        for attr in ACTION_ATTRS:
            if data.has_key(attr):
                action._setPropValue(attr, data[attr])
        
        return action
    
    def deleteAction(self, id, cat_name):
        """ Delete action with given id from given category """
        category = self.getActionCategory(cat_name)
        category.manage_delObjects(ids=[id,])
        return True
    
    def moveAction(self, id, cat_name, steps=0):
        """ Move action by a given steps """
        if steps != 0:
            category = self.getActionCategory(cat_name)
            if steps > 0:
                category.moveObjectsUp([id,], steps)
            else:
                category.moveObjectsDown([id,], abs(steps))
            return True
        return False
    
    #
    # KSS Methods that are used to update different parts of the page
    # accordingly to category
    #
    
    def updatePage(self, category):
        """ Seek for according method in class and calls it if found
            Example of making up method's name:
                portal_tabs => updatePortalTabs """
        method_name = 'update%sPageSection' % ''.join(map(lambda x: x.capitalize(), category.split('_')))
        if hasattr(self, method_name):
            getattr(self, method_name)()
    
    def updatePortalTabsPageSection(self):
        """ Method for updating global-sections on client """
        ksscore = self.getCommandSet("core")
        ksscore.replaceHTML(
            ksscore.getHtmlIdSelector("portal-globalnav"),
            self.sections_template(),
            withKssSetup="False")
    
    def updateSiteActionsPageSection(self):
        """ Method for updating site action on client """
        ksszope = self.getCommandSet("zope")
        ksszope.refreshViewlet(
            self.getCommandSet("core").getHtmlIdSelector("portal-siteactions"),
            "plone.portalheader",
            "plone.site_actions")
    
    def updateUserPageSection(self):
        """ Method for updating site action on client """
        ksszope = self.getCommandSet("zope")
        ksszope.refreshViewlet(
            self.getCommandSet("core").getHtmlIdSelector("portal-personaltools-wrapper"),
            "plone.portaltop",
            "plone.personal_bar")


