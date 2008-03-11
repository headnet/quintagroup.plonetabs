
/* Use onDOMLoad event to initialize kukit
   earlier then the document is fully loaded,
   but after the DOM is at its place already.

   This functionality is missing from Plone 2.1,
   the script is present in >=2.5, but it is not
   always added to RR - it needs to be added manually.

   If it's present we use it.
*/

kukit.plonetabs = {};

/* Base kukit plugins for plonetabs */

kukit.actionsGlobalRegistry.register('plonetabs-redirectTo', function(oper) {
;;; oper.componentName = '[plonetabs-redirectTo] action';
    var wl = window.location;
    oper.evaluateParameters([], {'protocol' : wl.protocol,
                                 'host'     : wl.host,
                                 'pathname' : wl.pathname,
                                 'search'   : wl.search,
                                 'hash'     : wl.hash});

    // normalize parameters
    var protocol = oper.parms.protocol + (oper.parms.protocol[oper.parms.protocol.length - 1] == ":") ?  "" : ":";
    var host = oper.parms.host;
    var pathname = oper.parms.pathname;
    var search = (oper.parms.search.substr(0, 1) == "?") ? "" : "?" + oper.parms.search;
    var hash = (oper.parms.hash.length > 1) ? ((oper.parms.hash.substr(0, 1) == "#" ? "" : "#") + oper.parms.hash) : "";

    url = protocol + "//" + host + pathname + search + hash;
    window.location.replace(url);

});
kukit.commandsGlobalRegistry.registerFromAction('plonetabs-redirectTo',
    kukit.cr.makeSelectorCommand);

