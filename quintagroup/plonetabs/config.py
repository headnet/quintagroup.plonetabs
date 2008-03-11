PROPERTY_SHEET = "tabs_properties"
FIELD_NAME     = "titles"

""" Example javascript
{"id"          : "test.js",
 "expression"  : "python: member is not None",
 "inline"      : False,
 "enabled"     : True,
 "cookable"    : True,
 "compression" : "safe",
 "cacheable"   : True}
"""

JAVASCRIPTS = [{"id"          : "++resource++prototype.js",
                "expression"  : "python:request['URL'].find('/prefs_tabs_form') > 0",
                "inline"      : False,
                "enabled"     : True,
                "cookable"    : True,
                "compression" : "safe",
                "cacheable"   : True},
               {"id"          : "++resource++effects.js",
                "expression"  : "python:request['URL'].find('/prefs_tabs_form') > 0",
                "inline"      : False,
                "enabled"     : True,
                "cookable"    : True,
                "compression" : "safe",
                "cacheable"   : True}]

""" Example css
{"id"          : "test.css",
 "expression"  : "python: member is not None",
 "media"       : "screen",
 "rel"         : "stylesheet",
 "title"       : "example styles",
 "rendering"   : "import",
 "enabled":    : True,
 "cookable"    : True,
 "compression" : "safe",
 "cacheable"   : True}
"""

CSSES = [{"id"          : "qplonetabs.css",
          "expression"  : "python:request['URL'].find('/prefs_tabs_form') > 0",
          "media"       : "screen",
          "rel"         : "stylesheet",
          "title"       : "qPloneTabs styles",
          "rendering"   : "import",
          "enabled"     : True,
          "cookable"    : True,
          "compression" : "safe",
          "cacheable"   : True}]

""" Example kss
{"id"          : "test.kss",
 "expression"  : "python: member is not None",
 "enabled":    : True,
 "cookable"    : True,
 "compression" : "safe",
 "cacheable"   : True}
"""

KSSES = [{"id"          : "qplonetabs.kss",
          "expression"  : "python:request['URL'].find('/prefs_tabs_form') > 0",
          "enabled"     : True,
          "cookable"    : True,
          "compression" : "safe",
          "cacheable"   : True},]

