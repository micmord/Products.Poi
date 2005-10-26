# File: PoiTracker.py
# 
# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.4.0-beta2 devel 
#            http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''Martin Aspeli <optilude@gmx.net>'''
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *

from Products.Poi.interfaces.Tracker import Tracker
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder


# additional imports from tagged value 'import'
from Products.ArchAddOn.Fields import SimpleDataGridField
from Products.Poi import permissions
from Products.ArchAddOn.Widgets import SimpleDataGridWidget
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import log_exc, log
##/code-section module-header

schema=Schema((
    StringField('title',
        widget=StringWidget(
            label="Tracker name",
            description="Enter a descriptive name for this tracker",
            label_msgid='Poi_label_title',
            description_msgid='Poi_help_title',
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title"
    ),

    TextField('description',
        widget=TextAreaWidget(
            label="Tracker description",
            description="Describe the purpose of this tracker",
            label_msgid='Poi_label_description',
            description_msgid='Poi_help_description',
            i18n_domain='Poi',
        ),
        use_portal_factory="1",
        accessor="Description"
    ),

    SimpleDataGridField('availableAreas',
        default=['ui | User interface | User interface issues', 'functionality | Functionality| Issues with the basic functionality', 'process | Process | Issues relating to the development process itself'],
        widget=SimpleDataGridWidget(
            label="Areas",
            description="""Enter the issue topics/areas for this tracker, one specification per line. The format is "Short name | Title | Description".""",
            label_msgid='Poi_label_availableAreas',
            description_msgid='Poi_help_availableAreas',
            i18n_domain='Poi',
        ),
        column_names=('id', 'title', 'description',),
        columns=3,
        required=True
    ),

    SimpleDataGridField('availableIssueTypes',
        default=['bug | Bug | Functionality bugs in the software', 'feature | Feature | Suggested features', 'patch | Patch | Patches to the software'],
        widget=SimpleDataGridWidget(
            label="Issue types",
            description="""Enter the issue types for this tracker, one specification per line. The format is "Short name | Title | Description".""",
            label_msgid='Poi_label_availableIssueTypes',
            description_msgid='Poi_help_availableIssueTypes',
            i18n_domain='Poi',
        ),
        column_names=('id', 'title', 'description'),
        columns=3,
        required=True
    ),

    LinesField('availableSeverities',
        default=['Critical', 'Important', 'Medium', 'Low'],
        widget=LinesWidget(
            label="Available severities",
            description="Enter the different type of issue severities that should be available, one per line.",
            label_msgid='Poi_label_availableSeverities',
            description_msgid='Poi_help_availableSeverities',
            i18n_domain='Poi',
        ),
        required=True
    ),

    StringField('defaultSeverity',
        default='Medium',
        widget=SelectionWidget(
            label="Default severity",
            description="Select the default severity for new issues.",
            label_msgid='Poi_label_defaultSeverity',
            description_msgid='Poi_help_defaultSeverity',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        vocabulary='getAvailableSeverities',
        required=True
    ),

    LinesField('availableReleases',
        widget=LinesWidget(
            label="Available releases",
            description="Enter the releases which issues can be assigned to, one per line. If no releases are entered, issues will not be organised by release.",
            label_msgid='Poi_label_availableReleases',
            description_msgid='Poi_help_availableReleases',
            i18n_domain='Poi',
        ),
        required=False
    ),

    LinesField('managers',
        widget=LinesWidget(
            label="Tracker managers",
            description="Enter the user ids of the users who will be allowed to manage this tracker, one per line.",
            label_msgid='Poi_label_managers',
            description_msgid='Poi_help_managers',
            i18n_domain='Poi',
        )
    ),

    BooleanField('sendNotificationEmails',
        default=True,
        widget=BooleanWidget(
            label="Send notification emails",
            description="If selected, tracker managers will receive an email each time a new issue or response is posted, and issue submitters will receive an email when there is a new response and when an issue has been resolved, awaiting confirmation.",
            label_msgid='Poi_label_sendNotificationEmails',
            description_msgid='Poi_help_sendNotificationEmails',
            i18n_domain='Poi',
        )
    ),

    StringField('mailingList',
        widget=StringWidget(
            label="Mailing list",
            description="""If given, and if "Send notification emails" is selected, an email will be sent to this address each time a new issue or response is posted. If no mailing list address is given, managers will receive individual emails.""",
            label_msgid='Poi_label_mailingList',
            description_msgid='Poi_help_mailingList',
            i18n_domain='Poi',
        ),
        required=False,
        validators=('isEmail',)
    ),

),
)


##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiTracker(BrowserDefaultMixin,BaseBTreeFolder):
    """
    The default tracker
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BrowserDefaultMixin,'__implements__',()),) + (getattr(BaseBTreeFolder,'__implements__',()),) + (Tracker,INonStructuralFolder,)


    # This name appears in the 'add' box
    archetype_name             = 'Issue Tracker'

    meta_type                  = 'PoiTracker'
    portal_type                = 'PoiTracker'
    allowed_content_types      = ['PoiIssue']
    filter_content_types       = 1
    global_allow               = 1
    allow_discussion           = 0
    content_icon               = 'PoiTracker.gif'
    immediate_view             = 'base_view'
    default_view               = 'poi_tracker_view'
    suppl_views                = ()
    typeDescription            = "An issue tracker"
    typeDescMsgId              = 'description_edit_poitracker'

    actions =  (


       {'action':      "string:${object_url}",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': (permissions.View,),
        'condition'  : 'python:1'
       },


       {'action':      "string:${object_url}/edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': (permissions.ModifyPortalContent,),
        'condition'  : 'python:1'
       },


    )

    _at_rename_after_creation  = True

    schema = BaseFolderSchema + \
             schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

    security.declareProtected(permissions.View, 'getFilteredIssues')
    def getFilteredIssues(self, criteria=None, **kwargs):
        """
        Get the contained issues in the given criteria.
        """

        if criteria is None:
            criteria = kwargs

        catalog = getToolByName(self, 'portal_catalog')

        query                = {}
        query['path']        = '/'.join(self.getPhysicalPath())
        query['portal_type'] = ['PoiIssue']

        if criteria.has_key('release'):
            query['getRelease'] = criteria.get('release')
        if criteria.has_key('area'):
            query['getArea'] = criteria.get('area')
        if criteria.has_key('issueType'):
            query['getIssueType'] = criteria.get('issueType')
        if criteria.has_key('severity'):
            query['getSeverity'] = criteria.get('severity')
        if criteria.has_key('state'):
            query['review_state'] = criteria.get('state')
        if criteria.has_key('tags'):
            query['Subject'] = criteria.get('tags')
        if criteria.has_key('responsible'):
            query['getResponsibleManager'] = criteria.get('responsible')
        if criteria.has_key('creator'):
            query['Creator'] = criteria.get('creator')
        if criteria.has_key('text'):
            query['SearchableText'] = criteria.get('text')

        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')

        return catalog.searchResults(query)



    security.declareProtected(permissions.View, 'isUsingReleases')
    def isUsingReleases(self):
        """Return a boolean indicating whether this tracker is using releases.
        """
        return len(self.getAvailableReleases()) > 0



    security.declareProtected(permissions.View, 'getReleasesVocab')
    def getReleasesVocab(self):
        """
        Get the releases available to the tracker as a DisplayList.
        """
        items = self.getAvailableReleases()
        vocab = DisplayList()
        for item in items:
            vocab.add(item, item)
        return vocab



    security.declarePrivate('getNotificationEmailAddresses')
    def getNotificationEmailAddresses(self, issue=None):
        """
        Upon activity for the given issue, get the list of email
        addresses to which notifications should be sent. May return an 
        empty list if notification is turned off. If issue is given, the 
        issue poster and any watchers will also be included.
        """

        if not self.getSendNotificationEmails():
            return []
        
        addresses = []
            
        portal_membership = getToolByName(self, 'portal_membership')
        mailingList = self.getMailingList()
        
        if mailingList:
            addresses.append(mailingList)
        else:
            managers = self.getManagers()
            for manager in managers:
                managerUser = portal_membership.getMemberById(manager)
                if managerUser is not None:
                    managerEmail = managerUser.getProperty('email')
                    if managerEmail and managerEmail not in addresses:
                        addresses.append(managerEmail)
        
        if issue is not None:
            issueEmail = issue.getContactEmail()
            if issueEmail and issueEmail not in addresses:
                addresses.append(issueEmail)
            watchers = issue.getWatchers()
            for watcher in watchers:
                watcherUser = portal_membership.getMemberById(watcher)
                if watcherUser is not None:
                    watcherEmail = watcherUser.getProperty('email')
                    if watcherUser and watcherEmail not in addresses:
                        addresses.append(watcherEmail)

        return addresses
        


    security.declarePrivate('sendNotificationEmail')
    def sendNotificationEmail(self, addresses, subject, text, subtype='html'):
        """
        Send a notification email to the list of addresses
        """
        
        if not self.getSendNotificationEmails() or not addresses:
            return
        
        portal_url  = getToolByName(self, 'portal_url')
        plone_utils = getToolByName(self, 'plone_utils')

        portal      = portal_url.getPortalObject()
        mailHost    = plone_utils.getMailHost()
        fromAddress = portal.getProperty('email_from_address', None)
        
        if fromAddress is None:
            log('Cannot send notification email: email sender address or name not set')
            return
        
        for address in addresses:
            try:
                mailHost.secureSend(message = text,
                                    mto = address,
                                    mfrom = fromAddress,
                                    subject = subject,
                                    subtype = subtype)
            except ConflictError:
                raise
            except:
                log_exc('Could not send email from %s to %s regarding issue in tracker %s' % (fromAddress, address, self.absolute_url(),))



    security.declareProtected(permissions.View, 'getTagsInUse')
    def getTagsInUse(self):
        """
        Get a list of the issue tags in use in this tracker.
        """
        catalog = getToolByName(self, 'portal_catalog')
        issues = catalog.searchResults(portal_type = 'PoiIssue',
                                       path = '/'.join(self.getPhysicalPath()))
        tags = {}
        for i in issues:
            for s in i.Subject:
                tags[s] = 1
        keys = tags.keys()
        keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
        return keys
        


    #manually created methods

    def canSelectDefaultPage(self):
        """Explicitly disallow selection of a default-page."""
        return False


    security.declareProtected(permissions.ModifyPortalContent, 'setManagers')
    def setManagers(self, managers):
        """
        Set the list of tracker managers, and give them the Manager local role.
        """
        field = self.getField('managers')
        currentManagers = field.get(self)
        field.set(self, managers)

        toRemove = [m for m in currentManagers if m not in managers]
        toAdd = [m for m in managers if m not in currentManagers]
        if toRemove:
            self.manage_delLocalRoles(toRemove)
        for userId in toAdd:
            self.manage_setLocalRoles(userId, ['Manager'])


    security.declarePublic('getIssueWorkflowStates')
    def getIssueWorkflowStates(self):
        """Get a DisplayList of the workflow states available on issues"""
        portal_workflow = getToolByName(self, 'portal_workflow')
        chain = portal_workflow.getChainForPortalType('PoiIssue')
        workflow = getattr(portal_workflow, chain[0])
        states = getattr(workflow, 'states')
        vocab = DisplayList()
        for id, state in states.items():
            vocab.add(id, state.title)
        return vocab.sortedByValue()


    def validate_managers(self, value):
        """Make sure issue tracker managers are actual user ids"""
        membership = getToolByName(self, 'portal_membership')
        notFound = []
        for userId in value:
            member = membership.getMemberById(userId)
            if member is None:
                notFound.append(userId)
        if notFound:
            return "The following user ids could not be found: %s" % ','.join(notFound)
        else:
            return None


def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiTracker,PROJECTNAME)
# end of class PoiTracker

##code-section module-footer #fill in your manual code here
##/code-section module-footer


