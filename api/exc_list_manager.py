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


def exc_list_find_umid(umid):
    entry = _exc_list_search(umid, ou='Admin')

    if entry:
        logger.debug('Found dn={}'.format(entry.entry_dn))
    else:
        raise ExcListError('not_found')

    return entry.entry_attributes_as_dict            


def exc_list_find_key(key, ou='IDProof'):
    entry = _exc_list_search(key, ou)

    if entry:
        logger.debug('Found dn={}'.format(entry.entry_dn))
    else:
        raise ExcListError('not_found')

    return entry.entry_attributes_as_dict


def exc_list_add_key(key, ou='IDProof'):

    # Check if an entry already exists
    entry = _exc_list_search(key, ou)
    logger.debug('entry={}'.format(entry))

    # If we have an entry then increment umichExcListBadAttempts
    if entry:
        logger.debug('Found dn={}'.format(entry.entry_dn))
        bad_attempts = int(entry['umichExcListBadAttempts'][0]) + 1
        mod_attrs = {
            'umichExcListBadAttempts': [(MODIFY_REPLACE, [bad_attempts])],
        }
        # Connection context manager
        with Connection(
            Server(settings.LDAP_URI),
            settings.LDAP_USERNAME,
            settings.LDAP_PW,
            auto_bind=True,
            check_names=False,    # Do not check attr format from schema (for time formatting)
        ) as conn:
            conn.modify(entry.entry_dn, mod_attrs)
        entry = _exc_list_search(key, ou)
        logger.debug('entry={}'.format(entry))
    # Else create a new entry
    else:
        new_dn = 'umichExcListName={},ou={},ou=ExclusionList,dc=umich,dc=edu'.format(key, ou)
        objectClasses = {'Top', 'umichExcListText'}
        attrs = {
            'umichExcListBadAttempts': 1,
            'umichExcListTimestamp': time.strftime('%Y%m%d%H%M%SZ', time.gmtime()),
        }
        # Connection context manager
        with Connection(
            Server(settings.LDAP_URI),
            settings.LDAP_USERNAME,
            settings.LDAP_PW,
            auto_bind=True,
            check_names=False,    # Do not check attr format from schema (for time formatting)
        ) as conn:
            conn.add(new_dn, objectClasses, attrs)
        logger.debug('Created new_dn={}'.format(new_dn))
        entry = _exc_list_search(key, ou)

    return entry.entry_attributes_as_dict


def exc_list_delete_key(key, ou='IDProof'):
    delete_dn = 'umichExcListName={},ou={},ou=ExclusionList,dc=umich,dc=edu'.format(key, ou)
    logger.debug('delete_dn={}'.format(delete_dn))
    # Connection context manager
    with Connection(
        Server(settings.LDAP_URI),
        settings.LDAP_USERNAME,
        settings.LDAP_PW,
        auto_bind=True,
        check_names=False,    # Do not check attr format from schema (for time formatting)
    ) as conn:
        conn.delete(delete_dn)
        message = conn.result['description']
    return {'message': message}


def _exc_list_search(umichExcListName, ou='IDProof'):
    entry = ''
    base = 'ou={},ou=ExclusionList,dc=umich,dc=edu'.format(ou)
    logger.debug('Searching for umichExcListName={},{}'.format(umichExcListName, base))

    # Connection context manager
    with Connection(
        Server(settings.LDAP_URI),
        settings.LDAP_USERNAME,
        settings.LDAP_PW,
        auto_bind=True,
        check_names=False,    # Do not check attr format from schema (for time formatting)
    ) as conn:
        conn.search(
            base,
            '(umichExcListName={})'.format(umichExcListName),
            attributes=['*'],
            time_limit=settings.LDAP_TIME_LIMIT,
        )

        if len(conn.entries) == 1:
            entry = conn.entries[0]
            #logger.debug('Found dn={}'.format(entry.entry_dn))
        elif len(conn.entries) == 0:
            pass
        else:    # pragma: no cover
            logger.debug('multiple results found')
            raise ExcListError(message='multiple_results_found')

    return entry

