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

    def find_umid(self, umid):
        entry = self._search(umid, ou='Admin')

        if entry:
            logger.debug('Found dn={}'.format(entry.entry_dn))
        else:
            raise ExcListError('not_found')

        return entry.entry_attributes_as_dict            


    def find_key(self, key, ou='IDProof'):
        entry = self._search(key, ou)

        if entry:
            logger.debug('Found dn={}'.format(entry.entry_dn))
        else:
            raise ExcListError('not_found')

        return entry.entry_attributes_as_dict


    def add_key(self, key, ou='IDProof'):

        # Check if an entry already exists
        entry = self._search(key, ou)
        logger.debug('entry={}'.format(entry))

        # If we have an entry then increment umichExcListBadAttempts
        if entry:
            logger.debug('Found dn={}'.format(entry.entry_dn))
            bad_attempts = int(entry['umichExcListBadAttempts'][0]) + 1
            mod_attrs = {
                'umichExcListBadAttempts': [(MODIFY_REPLACE, [bad_attempts])],
            }
            self.conn.modify(entry.entry_dn, mod_attrs)
            entry = self._search(key, ou)
            logger.debug('entry={}'.format(entry))
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
            logger.debug('Created new_dn={}'.format(new_dn))
            entry = self._search(key, ou)

        return entry.entry_attributes_as_dict


    def delete_key(self, key, ou='IDProof'):
        delete_dn = 'umichExcListName={},ou={},ou=ExclusionList,dc=umich,dc=edu'.format(key, ou)
        logger.debug('delete_dn={}'.format(delete_dn))
        self.conn.delete(delete_dn)
        return {'message': self.conn.result['description']}


    def _search(self, umichExcListName, ou='IDProof'):
        entry = ''
        base = 'ou={},ou=ExclusionList,dc=umich,dc=edu'.format(ou)
        logger.debug('Searching for umichExcListName={},{}'.format(umichExcListName, base))
        self.conn.search(
            base,
            '(umichExcListName={})'.format(umichExcListName),
            attributes=['*'],
            time_limit=settings.LDAP_TIME_LIMIT,
        )

        if len(self.conn.entries) == 1:
            entry = self.conn.entries[0]
            logger.debug('Found dn={}'.format(entry.entry_dn))
        elif len(self.conn.entries) == 0:
            pass
        else:    # pragma: no cover
            logger.debug('multiple results found')
            raise ExcListError(message='multiple_results_found')

        return entry

