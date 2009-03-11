from  Products.Five import zcml
from  Products.Five import fiveconfigure
from  Testing import ZopeTestCase as ztc
from  Products.PloneTestCase import PloneTestCase as ptc
from  Products.PloneTestCase.layer import onsetup

#ztc.installProduct('Zope2Product')

@onsetup
def setup_package():
     import quintagroup.plonetabs
     zcml.load_config('configure.zcml', quintagroup.plonetabs)
     #ztc.installPackage('some.other.package')
     ztc.installPackage('quintagroup.plonetabs')

setup_package()
ptc.setupPloneSite(products=['quintagroup.plonetabs'])

class PloneTabsTestCase(ptc.PloneTestCase):
     """Common test base class
     """
