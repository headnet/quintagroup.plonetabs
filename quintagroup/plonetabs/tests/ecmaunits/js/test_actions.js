if (typeof(qpt) == "undefined") {
    var qpt = {};
}

qpt.ActionsTestCase = function() {
    this.name = 'qpt.ActionsTestCase';

    this.setUp = function() {
//         this.dom = new global.dommer.DOM();
//         this.doc = this.dom.createDocument();
//         this.html = this.doc.createElement('html');
//         this.doc.appendChild(this.html);
//         this.body = this.doc.createElement('body');
//         this.html.appendChild(this.body);
    };

    this.tearDown = function() {
//         this.body.className = '';
    };

    this._action = function(actName) {
        return kukit.actionsGlobalRegistry.get(actName);
    };

    this._oper = function(node, parms) {
        oper = new kukit.op.Oper({'node': node, 'parms': parms});
        return oper;
    };

    this.ddtestRedirectTo = function() {
        // we aren't able to test this action entirely
        // because it's impossible to override window object
        // by dummy, thus we will navigate off from test page
        // in case testing new urls
        var act = this._action('plonetabs-redirectTo');
        var url_holder = window.location.href;
        if (window.location.hash != '#quintagroup.com') {
            if (window.location.hash) {
                url_holder = url_holder.slice(0, -window.location.hash.length);
            };
            url_holder = url_holder + '#quintagroup.com';
        };

        act(this._oper(null, {'hash':'#quintagroup.com'}));
        this.assertEquals(url_holder, window.location.href);
    };

    this.testToggleCollapsible = function() {
        var act = this._action('plonetabs-toggleCollapsible');

        // create test content
        var section = document.createElement('div');
        section.id = 'collabsibleSection';
        var handle = document.createElement('span');
        handle.appendChild(document.createTextNode('handle'));
        section.appendChild(handle);

        // first check default parameters
        act(this._oper(handle, {}));
        this.assertEquals(section.className, 'collapsedBlock');

        // now check expansion
        act(this._oper(handle, {'collapsed' : 'collapsedBlock',
                                 'expanded' : 'exp',
                                 'collapse': 'false'}));
        this.assertEquals(section.className, 'exp');
    };

    this.testResetForm = function() {
        var act = this._action('plonetabs-resetForm');

        // create test form
        var _form = document.createElement('form');
        var state_var;
        _form.reset = function() {state_var='reset';};
        var _input = document.createElement('input');
        _form.appendChild(_input);
        _input.type = 'text';
        _input.name = 'test';
        _input.value = 'test value';

        // first check default behavior
        act(this._oper(_form, {}));
        this.assertEquals(state_var, 'reset');

        // and now pass it something invalid
        state_var = 'invalid data';
        act(this._oper(_input, {}));
        this.assertEquals(state_var, 'invalid data');
    };

    this.testBlur = function() {
        var act = this._action('plonetabs-blur');

        // create blurrable element
        var _input = document.createElement('input');
        _input.type = 'text';
        _input.name = 'test';
        _input.value = 'test value';
        var state_var;
        _input.blur = function() {state_var='blur';};

        // first check good behavior
        act(this._oper(_input, {}));
        this.assertEquals(state_var, 'blur');

        // now check with bad input element
        state_var = 'invalid data';
        act(this._oper(document.body, {}));
        this.assertEquals(state_var, 'invalid data');
    };

    this.testHandleServerError = function() {
        var act = this._action('plonetabs-handleServerError');

        // patch global alert function to be able test something
        var _orig_alert = window.alert;
        var message;
        window.alert = function(m){message=m;};

        // first pass some message explicitly
        act(this._oper(null, {'message':'Hi there!'}));
        this.assertEquals('Hi there!', message);

        // now check some deeper behavior, don't pass message,
        // insteas set kukit.E error message
        kukit.E = 'client_reason="invalid KSS response"';
        act(this._oper(null, {}));
        this.assertNotEquals(message.indexOf('Check your portal error log.'), -1);

        // revert patch
        window.alert = _orig_alert;
    };

    this.testGenerateId = function() {
        var act = this._action('plonetabs-generateId');

        // create test content
        var _target = document.createElement('input');
        _target.id = 'tabstest-target';
        _target.style.display = 'none';
        _target.type = 'text';
        _target.value = '';
        document.body.appendChild(_target);
        var _source = document.createElement('input');
        _source.type = 'text';
        _source.value = 'title';

        // check default behavior
        act(this._oper(_source, {'target':'tabstest-target', 'var_name':'initialValue'}));
        this.assertEquals(kukit.engine.stateVariables['initialValue'], 'title');

        // set some invalid for id characters into source field
        _source.value = '"bad title"';
        act(this._oper(_source, {'target':'tabstest-target', 'var_name':'initialValue'}));
        this.assertEquals(_target.value, 'bad title');

        // cleanup test trash
        document.body.removeChild(_target);
        delete kukit.engine.stateVariables['initialValue'];
    };

    this.testReplaceOrInsert = function() {
        var act = this._action('plonetabs-replaceOrInsert');

        // create test content
        var container = document.createElement('div');
        container.id = 'plonetabs-test-container';
        container.style.display = 'none';
        document.body.appendChild(container);
        var span1 = document.createElement('span');
        span1.id = 'plonetabs-span1';
        span1.appendChild(document.createTextNode('span #1'));
        container.appendChild(span1);
        var span2 = document.createElement('span');
        span2.appendChild(document.createTextNode('span #2'));
        container.appendChild(span2);

        // first check simpler behavior
        act(this._oper(document.body,
                       {'selector': 'plonetabs-span1',
                        'selectorType': 'htmlid',
                        'html': '<span id="plonetabs-newspan">hi</div>',
                        'withKssSetup': false}));
        this.assertEquals(document.getElementById('plonetabs-newspan').innerHTML, 'hi')

        // then check some more complicated behavior
        

        // cleanup document body from test content
        document.body.removeChild(container);
    };

};

qpt.ActionsTestCase.prototype = new TestCase;


if (typeof(testcase_registry) != 'undefined') {
    testcase_registry.registerTestCase(qpt.ActionsTestCase, 'qpt.ActionsTestCase');
}
