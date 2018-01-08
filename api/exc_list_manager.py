from django.conf import settings
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE

import time
import logging

logger = logging.getLogger(__name__)

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ExcListError(Error):
    """
    Exception raised on exclusion list error.
    Attributes:
        message: explanation of the error
    """

    def __init__(self, message):
        self.message = message


class ExcList:
    """
    Interact with the Exclusion List - find, add, delete
    """

    server = Server(settings.LDAP_URI)
    conn = Connection(
        server,
        settings.LDAP_USERNAME,
        settings.LDAP_PW,
        auto_bind=True,
        check_names=False,    # Do not check attr format from schema (for time formatting)
    )

    def find(self, data, ou='IDProof'):
        umid = data['umid']
        key = data['key']

        # Default values for response
        response = {
            'excluded': False,
            'umid_blacklisted': False,
            'max_attempts_exceeded': False,
        }

        # Search the admin ou for blacklisted umid
        entry = self._search(umid, ou='Admin')

        if entry:
            print('Found dn={}'.format(entry.entry_dn))
            response['excluded'] = True
            response['umid_blacklisted'] = True
        else:
            print('No entry in ou=Admin, checking ou={}'.format(ou))

        # Search the specified ou for the given key
        base = 'ou={},ou=ExclusionList,dc=umich,dc=edu'.format(ou)
        entry = self._search(key, ou)

        if entry:
            print('Found dn={}'.format(entry.entry_dn))
            response['entry'] = entry.entry_attributes_as_dict
            print('entry={}'.format(entry))
        else:
            print('no entry found')

        if response == {}:
            raise ExcListError('not_found')

        print('response={}'.format(response))
        return response


    def add(self, data, ou='IDProof'):
        key = data['key']

        # Check if an entry already exists
        entry = self._search(key, ou)
        print('entry={}'.format(entry))

        # If we have an entry then increment umichExcListBadAttempts
        if entry:
            print('Found dn={}'.format(entry.entry_dn))
            bad_attempts = int(entry['umichExcListBadAttempts'][0]) + 1
            mod_attrs = {
                'umichExcListBadAttempts': [(MODIFY_REPLACE, [bad_attempts])],
            }
            self.conn.modify(entry.entry_dn, mod_attrs)
            entry = self._search(key, ou)
            print('entry={}'.format(entry))
        # Else create a new entry
        else:
            new_dn = 'umichExcListName={},ou={},ou=ExclusionList,dc=umich,dc=edu'.format(key, ou)
            objectClasses = {'Top', 'umichExcListText'}
            attrs = {
                'umichExcListBadAttempts': 1,
                'umichExcListTimestamp': time.strftime('%Y%m%d%H%M%SZ', time.gmtime()),
            }
            self.conn.add(
                new_dn,
                objectClasses,
                attrs,
            )
            print('Created new_dn={}'.format(new_dn))
            entry = self._search(key, ou)

        return {'entry': entry.entry_attributes_as_dict}


    def delete(self, data, ou='IDProof'):
        key = data['key']
        delete_dn = 'umichExcListName={},ou={},ou=ExclusionList,dc=umich,dc=edu'.format(key, ou)
        print('delete_dn={}'.format(delete_dn))
        self.conn.delete(delete_dn)
        return {'message': self.conn.result['description']}


    def _search(self, umichExcListName, ou='IDProof'):
        entry = ''
        base = 'ou={},ou=ExclusionList,dc=umich,dc=edu'.format(ou)
        print('Searching for umichExcListName={}'.format(umichExcListName))
        self.conn.search(
            base,
            '(umichExcListName={})'.format(umichExcListName),
            attributes=['*'],
            time_limit=settings.LDAP_TIME_LIMIT,
        )

        if len(self.conn.entries) == 1:
            entry = self.conn.entries[0]
            print('Found dn={}'.format(entry.entry_dn))
        elif len(self.conn.entries) == 0:
            pass
        else:
            print('multiple results found')
            raise ExcListError(message='multiple_results_found')

        return entry

