
kukit.plonetabs = {};

/* Base kukit plugins for plonetabs */

kukit.actionsGlobalRegistry.register("plonetabs-redirectTo", function(oper) {
;;; oper.componentName = "[plonetabs-redirectTo] action";
    var wl = window.location;
    oper.evaluateParameters([], {"protocol"     : wl.protocol,
                                 "host"         : wl.host,
                                 "pathname"     : wl.pathname,
                                 "search"       : wl.search,
                                 "searchparams" : "",
                                 "searchvalues" : "",
                                 "hash"         : wl.hash});

    // normalize parameters
    var protocol = oper.parms.protocol + (oper.parms.protocol[oper.parms.protocol.length - 1] == ":") ?  "" : ":";
    var host = oper.parms.host;
    var pathname = oper.parms.pathname;
    if ((params = oper.parms.searchparams) && (values = oper.parms.searchvalues)) {
        search = "?";
        params = params.split(",");
        values = values.split(",");
        for (var i = 0; i < params.length; i++) {
            search += params[i] + '=' + values[i] + '&';
        }
        search = (search.slice(search.length - 1) == '&') ? search.slice(0, search.length - 1) : search;
    } else {
        search = oper.parms.search;
        search = (search && search.substr(0, 1) == "?") ? search : (search ? "?" + search : "");
    }
    var hash = (oper.parms.hash.length > 1) ? ((oper.parms.hash.substr(0, 1) == "#" ? "" : "#") + oper.parms.hash) : "";

    url = protocol + "//" + host + pathname + search + hash;
    window.location.replace(url);

});

kukit.commandsGlobalRegistry.registerFromAction("plonetabs-redirectTo", kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register("plonetabs-toggleCollapsible", function(oper) {
;;; oper.componentName = "[plonetabs-toggleCollapsible] action";
    oper.evaluateParameters([], {"collapsed" : "collapsedBlock",
                                 "expanded" : "expandedBlock",
                                 "collapse": "none"});

    var node = oper.node.parentNode;  // collapsible section

    if (oper.parms.collapse != "none") {
        if (oper.parms.collapse == "true") {
            removeClassName(node, oper.parms.expanded);
            addClassName(node, oper.parms.collapsed);
        } else {
            removeClassName(node, oper.parms.collapsed);
            addClassName(node, oper.parms.expanded);
        }
    } else {
        if (hasClassName(node, oper.parms.collapsed)) {
            removeClassName(node, oper.parms.collapsed);
            addClassName(node, oper.parms.expanded);
        } else {
            removeClassName(node, oper.parms.expanded);
            addClassName(node, oper.parms.collapsed);
        }
    }

});

kukit.commandsGlobalRegistry.registerFromAction("plonetabs-toggleCollapsible", kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register("plonetabs-resetForm", function(oper) {
;;; oper.componentName = "[plonetabs-resetForm] action";
    oper.evaluateParameters([], {});

    if (typeof(oper.node.reset) == "function") {
        oper.node.reset();
    } else {
        kukit.logWarning("plonetabs-resetForm: reset could only be executed on form element");
    }

});

kukit.commandsGlobalRegistry.registerFromAction("plonetabs-resetForm", kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register("plonetabs-handleServerError", function(oper) {
    oper.componentName = "[plonetabs-handleServerError] action";
    oper.evaluateParameters([], {"message" : kukit.E});
    alert(oper.parms.message);
});

var PLONETABS_ADD_PATTERN = new RegExp('[^a-zA-Z0-9-_~,.\\$\\(\\)# ]','g');

kukit.actionsGlobalRegistry.register("plonetabs-generateId", function(oper) {
    oper.componentName = "[plonetabs-generateId] action";
    oper.evaluateParameters(["target"], {});

    var source = oper.node;
    var target = document.getElementById(oper.parms.target);

    if (target == null) {
        kukit.logWarning("plonetabs-generateId: target element ('" + oper.parms.target + "') not found");
        return ;
    }

    if (target.value == kukit.engine.stateVariables['plonetabs-addingTitle'].replace(PLONETABS_ADD_PATTERN, '')) {
        target.value = source.value.replace(PLONETABS_ADD_PATTERN, '');
    }
    kukit.engine.stateVariables['plonetabs-addingTitle'] = source.value;

});
