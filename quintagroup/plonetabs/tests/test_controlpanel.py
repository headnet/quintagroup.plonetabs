import unittest

from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ActionInformation import Action, ActionCategory

from quintagroup.plonetabs.browser.interfaces import IPloneTabsControlPanel
from quintagroup.plonetabs.browser.plonetabs import PloneTabsControlPanel as ptp
from quintagroup.plonetabs.tests.base import PloneTabsTestCase
from quintagroup.plonetabs.tests.data import PORTAL_ACTIONS


class TestControlPanelHelperMethods(PloneTabsTestCase):
    """Test here configlet helper methods"""
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
        # TODO: investigate why I can't work with it but
        # have to traverse my view
        #self.panel = getMultiAdapter((self.portal, self.portal.REQUEST),
            #name='plonetabs-controlpanel')
        self.panel = self.portal.restrictedTraverse('plonetabs-controlpanel')
        self.tool = getToolByName(self.portal, 'portal_actions')
    
    def test_redirect(self):
        response = self.portal.REQUEST.RESPONSE
        method = self.panel.redirect
        portal_url =  getMultiAdapter((self.portal, self.portal.REQUEST),
                                      name=u"plone_portal_state").portal_url()
        url = '%s/%s' % (portal_url, "@@plonetabs-controlpanel")
        method()
        self.assertEquals(response.headers.get('location', ''), url,
            'Redirect method is not working properly.')
        
        # check query string and anchor hash
        method('http://quintagroup.com', 'q=test', 'hash_code')
        self.assertEquals(response.headers.get('location', ''),
            'http://quintagroup.com?q=test#hash_code',
            'Redirect method is not working properly.')
    
    def test_fixExpression(self):
        method = self.panel.fixExpression
        self.assertEquals(method('/slash'), 'string:${portal_url}/slash')
        self.assertEquals(method('https://test.com'), 'string:https://test.com')
        self.assertEquals(method('python:True'), 'python:True')
        self.assertEquals(method('hello'), 'string:${object_url}/hello')
    
    def test_copyAction(self):
        data = PORTAL_ACTIONS[0][1]['children'][0][1]
        action = Action('act1', **data)
        info = self.panel.copyAction(action)
        self.assertEquals(len(info.keys()), 6)
        self.assertEquals(info['description'], 'The most important place')
    
    def test_validateActionFields(self):
        method = self.panel.validateActionFields
        good_data = PORTAL_ACTIONS[0][1]['children'][0][1].copy()
        good_data['id'] = 'new_one'
        errors = method('new_category', good_data)
        self.assertEquals(errors, {},
            'There should be no errors for valid data.')
        
        bad_data = {'id':'',
                    'title': ' ',
                    'available_expr': 'bad_type:test',
                    'url_expr': 'bad_type:test'}
        errors = method('new_category', bad_data)
        # this test won't pass because PloneTestCase change initial behaviour
        # of CMFCore's Expression object, it doesn't compile expressions
        # on creation anymore
        self.assertEquals(len(errors.keys()), 4,
            'This test is not supposed to be passed because of difference '
            'between real and test environments.')
    
    def test_processErrors(self):
        pass
    
    def test_parseEditForm(self):
        pass
    
    def test_parseAddForm(self):
        pass
    
    def test_getActionCategory(self):
        pass
    
    def test_getOrCreateCategory(self):
        pass
    
    def test_setSiteProperties(self):
        pass
    
    def test_renderViewlet(self):
        pass
    
    def test_addAction(self):
        pass
    
    def test_updateAction(self):
        pass
    
    def test_deleteAction(self):
        pass
    
    def test_moveAction(self):
        pass


class TestControlPanelAPI(PloneTabsTestCase):
    """Test here interface methods of control panel class"""
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.panel = self.portal.restrictedTraverse('plonetabs-controlpanel')
        self.tool = getToolByName(self.portal, 'portal_actions')
    
    def test_interface(self):
        self.failUnless(IPloneTabsControlPanel.implementedBy(ptp),
            'PloneTabs control panel does not implement required interface.')
        self.failUnless(verifyClass(IPloneTabsControlPanel, ptp),
            'PloneTabs control panel does not implement required interface.')
    
    def test_getPageTitle(self):
        self.assertEquals(self.panel.getPageTitle(),
            'Portal Tabs Configuration',
            'getPageTitle method is broken')
        self.assertEquals(self.panel.getPageTitle(category='notexists'),
            "Plone '%s' Configuration" % 'notexists',
            'getPageTitle method is broken')
    
    def test_hasActions(self):
        method = self.panel.hasActions
        # purge any default portal actions
        self.purgeActions()
        self.failIf(method(),
            'There should be no portal_tab actions in portal')
        
        # setup our own actions
        self.setupActions(self.tool)
        self.failUnless(method(),
            'There should be portal_tab actions in portal')
    
    def test_getPortalActions(self):
        method = self.panel.getPortalActions
        # purge any default portal actions
        self.purgeActions()
        self.assertEquals(len(method()), 0,
            'There should be no actions in portal_tabs category.')
        
        # setup our own actions
        self.setupActions(self.tool)
        self.assertEquals(len(method()), 2,
            'There should be 2 actions in portal_tabs category.')
        
        # marginal arguments
        self.assertEquals(len(method('notexistent_category')), 0,
            'There should be no actions for not existed category.')
    
    def test_isGeneratedTabs(self):
        method = self.panel.isGeneratedTabs
        # prepare value
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        sp.manage_changeProperties(disable_folder_sections=True)
        self.failIf(method(), 'But folder sections are disabled...')
    
    def test_isNotFoldersGenerated(self):
        method = self.panel.isNotFoldersGenerated
        # prepare value
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        sp.manage_changeProperties(disable_nonfolderish_sections=True)
        self.failIf(method(), 'But non folderish sections are disabled...')
    
    def test_getActionsList(self):
        method = self.panel.getActionsList
        # purge any default portal actions
        self.purgeActions()
        self.failIf('class="editform"' in method(),
            'There should no be actions in actions list template.')
        self.setupActions(self.tool)
        self.failUnless('class="editform"' in method(),
            'There are no actions in actions list template.')
    
    def test_getAutoGenereatedSection(self):
        method = self.panel.getAutoGenereatedSection
        self.failIf('<form' in method('user'),
            'There should be no form in autogenerated tabs template '
            'for category other than portal_tabs.')
        self.failUnless('<form' in method('portal_tabs'),
            'There should be form in autogenerated tabs template '
            'for portal_tabs category.')
    
    def test_getGeneratedTabs(self):
        self.panel.getGeneratedTabs()
        # check expiration header set by generated tabs template
        self.assertEquals(
            self.portal.REQUEST.RESPONSE.headers.get('expires', ''),
            'Mon, 26 Jul 1996 05:00:00 GMT',
            'Expiration header is not set properly.')
    
    def test_getRootTabs(self):
        method = self.panel.getRootTabs
        # make sure we don't depend on external settings
        self.purgeContent()
        self.assertEquals(len(method()), 0,
            'There should be no root elements for navigation.')
        
        # now add some testing content
        self.setupContent(self.portal)
        self.assertEquals(len(method()), 2,
            'There should be 2 elements in portal root for navigation.')
        
        # now switch off autogeneration
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        sp.manage_changeProperties(disable_folder_sections=True)
        self.assertEquals(len(method()), 0,
            'There should be no root elements for navigation when '
            'tabs autogeneration is switched off.')
    
    def test_getCategories(self):
        method = self.panel.getCategories
        # purge any default portal actions
        self.purgeActions()
        self.assertEquals(len(method()), 0,
            'There should be no categories in portal_actions tool.')
        
        # now setup actions
        self.setupActions(self.tool)
        self.assertEquals(method(), ['portal_tabs', 'new_category'],
            'There should be exactly 2 categories in portal_actions tool.')
    
    def test_portal_tabs(self):
        method = self.panel.portal_tabs
        self.purgeContent()
        self.purgeActions()
        self.assertEquals(len(method()), 0,
            'There should be no portal tabs.')
        
        # cleanup memoize cache
        # cause actions method of portal context state is caching it's
        # results in request and we have the same request for every call
        self.purgeCache(self.portal.REQUEST)
        
        # add actions
        self.setupActions(self.tool)
        self.assertEquals(len(method()), 2,
            'There should be 2 portal tabs.')
        
        # add content
        self.setupContent(self.portal)
        self.assertEquals(len(method()), 4,
            'There should be 4 portal tabs.')
    
    def test_selected_portal_tab(self):
        self.assertEquals(self.panel.selected_portal_tab(), 'index_html',
            'index_html is not selected tab while being on configlet.')

    def test_test(self):
        self.assertEquals(self.panel.test(True, 'true', 'false'), 'true',
            'Test function does not work propertly.')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestControlPanelHelperMethods))
    suite.addTest(unittest.makeSuite(TestControlPanelAPI))
    #suite.addTest(unittest.makeSuite(TestControlPanelManageMethods))
    #suite.addTest(unittest.makeSuite(TestControlPanelKSSMethods))
    return suite
