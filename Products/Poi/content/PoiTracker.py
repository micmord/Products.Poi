# -*- coding: utf-8 -*-
#
# File: PoiTracker.py
#
# Copyright (c) 2006 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Martin Aspeli <optilude@gmx.net>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *
from Products.Poi.config import PROJECTNAME

from Products.DataGridField.DataGridField import DataGridField
from Products.Poi import permissions
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from Products.Poi.interfaces import ITracker
from Products.Poi.utils import linkSvn
from Products.Poi.utils import linkBugs

schema = Schema((

    StringField(
        name='title',
        widget=StringWidget(
            label="Tracker name",
            description="Enter a descriptive name for this tracker",
            label_msgid="Poi_label_tracker_title",
            description_msgid="Poi_help_tracker_title",
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title",
        searchable=True
    ),

    TextField(
        name='description',
        widget=TextAreaWidget(
            label="Tracker description",
            description="Describe the purpose of this tracker",
            label_msgid='Poi_label_description',
            description_msgid='Poi_help_description',
            i18n_domain='Poi',
        ),
        use_portal_factory="1",
        accessor="Description",
        searchable=True
    ),

    TextField(
        name='helpText',
        allowable_content_types=('text/plain', 'text/structured', 'text/html',
                                 'application/msword'),
        widget=RichWidget(
            label="Help text",
            description="Enter any introductory help text you'd like to display on the tracker front page.",
            label_msgid='Poi_label_helpText',
            description_msgid='Poi_help_helpText',
            i18n_domain='Poi',
        ),
        default_output_type='text/html',
        searchable=True
    ),

    DataGridField(
        name='availableAreas',
        default=({'id' : 'ui', 'title' : 'User interface', 'description' : 'User interface issues'}, {'id' : 'functionality', 'title' : 'Functionality', 'description' : 'Issues with the basic functionality'}, {'id' : 'process', 'title' : 'Process', 'description' : 'Issues relating to the development process itself'}),
        widget=DataGridWidget(
            label="Areas",
            description="Enter the issue topics/areas for this tracker.",
            column_names=('Short name', 'Title', 'Description'),
            label_msgid='Poi_label_availableAreas',
            description_msgid='Poi_help_availableAreas',
            i18n_domain='Poi',
        ),
        allow_empty_rows=False,
        required=True,
        validators=('isDataGridFilled', ),
        columns=('id', 'title', 'description',)
    ),

    DataGridField(
        name='availableIssueTypes',
        default=({'id' : 'bug', 'title' : 'Bug', 'description' : 'Functionality bugs in the software'}, {'id' : 'feature', 'title' : 'Feature', 'description' : 'Suggested features'}, {'id' : 'patch', 'title' : 'Patch', 'description' : 'Patches to the software'}),
        widget=DataGridWidget(
            label="Issue types",
            description="Enter the issue types for this tracker.",
            column_names=('Short name', 'Title', 'Description',),
            label_msgid='Poi_label_availableIssueTypes',
            description_msgid='Poi_help_availableIssueTypes',
            i18n_domain='Poi',
        ),
        allow_empty_rows=False,
        required=True,
        validators=('isDataGridFilled',),
        columns=('id', 'title', 'description')
    ),

    LinesField(
        name='availableSeverities',
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

    StringField(
        name='defaultSeverity',
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

    LinesField(
        name='availableReleases',
        widget=LinesWidget(
            label="Available releases",
            description="Enter the releases which issues can be assigned to, one per line. If no releases are entered, issues will not be organised by release.",
            label_msgid='Poi_label_availableReleases',
            description_msgid='Poi_help_availableReleases',
            i18n_domain='Poi',
        ),
        required=False
    ),

    LinesField(
        name='managers',
        widget=LinesWidget(
            label="Tracker managers",
            description="Enter the user ids of the users who will be allowed to manage this tracker, one per line.",
            label_msgid='Poi_label_managers',
            description_msgid='Poi_help_managers',
            i18n_domain='Poi',
        ),
        default_method="getDefaultManagers"
    ),

    BooleanField(
        name='sendNotificationEmails',
        default=True,
        widget=BooleanWidget(
            label="Send notification emails",
            description="If selected, tracker managers will receive an email each time a new issue or response is posted, and issue submitters will receive an email when there is a new response and when an issue has been resolved, awaiting confirmation.",
            label_msgid='Poi_label_sendNotificationEmails',
            description_msgid='Poi_help_sendNotificationEmails',
            i18n_domain='Poi',
        )
    ),

    StringField(
        name='mailingList',
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
    StringField(
        name='svnUrl',
        widget=StringWidget(
            label="URL to SVN",
            description="""Please enter the Url to the related SVN repository, e.g.: http://dev.plone.org/collective/changeset/%(rev)s for products in the Plone collective.""",
            label_msgid='Poi_label_svnurl',
            description_msgid='Poi_help_svnurl',
            i18n_domain='Poi',
            size = '90',
        ),
        required=False,
    ),

),
)

PoiTracker_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()


class PoiTracker(BaseBTreeFolder, BrowserDefaultMixin):
    """The default tracker
    """
    _at_rename_after_creation = True
    archetype_name = 'Issue Tracker'
    implements(ITracker)
    meta_type = 'PoiTracker'
    portal_type = 'PoiTracker'
    schema = PoiTracker_schema
    security = ClassSecurityInfo()

    # Methods

    security.declarePrivate('linkDetection')
    def linkDetection(self, text):
        """
        Detects issues and svn revision tags and creates links.
        """
        # In case we get something not string like, we just return
        # text without change
        if not isinstance(text, basestring):
            return text
        catalog = getToolByName(self, 'portal_catalog')
        issuefolder = self.restrictedTraverse('@@issuefolder')
        issues = catalog.searchResults(issuefolder.buildIssueSearchQuery(None))
        ids = frozenset([issue.id for issue in issues])

        # XXX/TODO: should these patterns live in the config file?
        text = linkBugs(text, ids,
                        ['#[1-9][0-9]*', 'issue:[1-9][0-9]*',
                         'ticket:[1-9][0-9]*', 'bug:[1-9][0-9]*'])
        svnUrl = self.getSvnUrl()
        text = linkSvn(text, svnUrl,
                       ['r[0-9]+', 'changeset:[0-9]+', '\[[0-9]+\]'])

        return text

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

    security.declareProtected(permissions.View, 'getTagsInUse')
    def getTagsInUse(self):
        """Get a list of the issue tags in use in this tracker."""
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

    security.declareProtected(permissions.View, 'getExternalTitle')
    def getExternalTitle(self):
        """ Get the external title of this tracker.

        This will be the name used in outgoing emails, for example.
        """
        return self.Title()

    # Manually created methods

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
        toKeep = [m for m in managers if m in currentManagers]
        for userId in toRemove:
            local_roles = list(self.get_local_roles_for_userid(userId))
            if 'TrackerManager' in local_roles:
                local_roles.remove('TrackerManager')
                if local_roles:
                    # One or more roles must be given
                    self.manage_setLocalRoles(userId, local_roles)
                else:
                    self.manage_delLocalRoles(toRemove)
        for userId in toAdd:
            local_roles = list(self.get_local_roles_for_userid(userId))
            local_roles.append('TrackerManager')
            self.manage_setLocalRoles(userId, local_roles)
        # When creating a tracker as non-manager you used to become
        # only Owner and not Manager, which is not what we want.
        for userId in toKeep:
            local_roles = list(self.get_local_roles_for_userid(userId))
            if not 'TrackerManager' in local_roles:
                local_roles.append('TrackerManager')
                self.manage_setLocalRoles(userId, local_roles)

    security.declarePublic('getIssueWorkflowStates')
    def getIssueWorkflowStates(self):
        """Get a DisplayList of the workflow states available on issues."""
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
            return "The following user ids could not be found: %s" % \
                ','.join(notFound)
        else:
            return None

    def getDefaultManagers(self):
        """The default list of managers should include the tracker owner"""
        return (self.Creator(), )

    def _getMemberEmail(self, username, portal_membership=None):
        """Query portal_membership to figure out the specified email address
        for the given user (via the username parameter) or return None if none
        is present.
        """

        if portal_membership is None:
            portal_membership = getToolByName(self, 'portal_membership')

        member = portal_membership.getMemberById(username)
        if member is None:
            return None

        try:
            email = member.getProperty('email')
        except Unauthorized:
            # this will happen if CMFMember is installed and the email
            # property is protected via AT security
            email = member.getField('email').getAccessor(member)()
        return email


registerType(PoiTracker, PROJECTNAME)
# end of class PoiTracker
