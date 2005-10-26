#
# Skeleton ContextHelpTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import newSecurityManager

from Testing import ZopeTestCase
from Products.Poi.tests import ptc

ZopeTestCase.installProduct('PloneSoftwareCenter')

class TestPscTracker(ptc.PoiTestCase):
    """Test psc tracker functionality"""

    def reinstallProduct(self, name):
        """Re-installs a product into the Plone site."""
        sm = getSecurityManager()
        self.loginAsPortalOwner()
        try:
            qi = self.portal.portal_quickinstaller
            if qi.isProductInstalled(name):
                qi.reinstallProducts(name)
                self._refreshSkinData()
        finally:
            setSecurityManager(sm)

    def afterSetUp(self):
        self.addProduct('PloneSoftwareCenter')
        self.reinstallProduct('Poi')
        
        self.setRoles(['Manager'])
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.psc = self.portal.psc
        self.psc.invokeFactory('PSCProject', 'project')
        self.project = self.psc.project

    def testTrackedAllowedInProject(self):
        try:
            self.project.invokeFactory('PoiPscTracker', 'issues')
        except Unauthorized:
            self.fail()

    def testNoReleasesInSchema(self):
        self.project.invokeFactory('PoiPscTracker', 'issues')
        self.failIf(self.project.issues.Schema().has_key('releases'))

    def testReleasesVocab(self):
        self.project.invokeFactory('PoiPscTracker', 'issues')
        self.project.releases.invokeFactory('PSCRelease', '1.0')
        self.project.releases.invokeFactory('PSCRelease', '2.0')
        self.failUnless(self.project.issues.isUsingReleases())
        releasesVocab = self.project.issues.getReleasesVocab()
        self.assertEqual(len(releasesVocab), 2)
        self.assertEqual(releasesVocab.values(), ['1.0', '2.0'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPscTracker))
    return suite

if __name__ == '__main__':
    framework()