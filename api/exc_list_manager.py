from django.conf import settings
import logging
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE

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


# Search the mcomm ExclusionList branch on the provided key
# Default ou is IDProof
def exc_list_find(data, ou='IDProof'):

    # Search the admin ou for blacklisted umid
    umid = data['umid']
    base = 'ou=Admin,ou=ExclusionList,dc=umich,dc=edu'
    entry = _mcomm_exclist_search(umid, base)

    # If we have an entry, the id is blacklisted and should not be allowed to proceed
    if entry:
        logger.debug('Found dn={}'.format(entry.entry_dn))
    else:
        logger.debug('No entry in ou=Admin, checking ou={}'.format(ou))

        # Search the specified ou for the given key
        key = data['key']
        base = 'ou={},ou=ExclusionList,dc=umich,dc=edu'.format(ou)
        entry = _mcomm_exclist_search(key, base)

        if entry:
            logger.debug('Found dn={}'.format(entry.entry_dn))
        else:
            logger.debug('No entry found')


    return entry


def exc_list_add(data, ou='IDProof'):

    key = data['key']
    base = 'ou={},ou=ExclusionList,dc=umich,dc=edu'.format(ou)
    entry = _mcomm_exclist_search(key, base)

    print('entry={}'.format(entry))

    # TODO: check for more than one result returned
    if entry:
        entry = conn.entries[0]
        logger.debug('Found dn={}'.format(entry.entry_dn))
    else:
        new_dn = 'umichExcListName={},ou={},ou=ExclusionList,dc=umich,dc=edu'.format(key, ou)
        objectClasses = {'Top', 'umichExcListText'}
        attrs = {'umichExcListBadAttempts': 1}
        server = Server(settings.LDAP_URI)
        conn = Connection(server, settings.LDAP_USERNAME, settings.LDAP_PW, auto_bind=True)
        conn.add(
            new_dn,
            objectClasses,
            attrs,
        )
        entry = _mcomm_exclist_search(key, base)
        logger.debug('Created new_dn={}'.format(new_dn))

    return entry


def exc_list_delete(data, ou='IDProof'):

    key = data['key']
    delete_dn = 'umichExcListName={},ou={},ou=ExclusionList,dc=umich,dc=edu'.format(key, ou)
    print('delete_dn={}'.format(delete_dn))

    server = Server(settings.LDAP_URI)
    conn = Connection(server, settings.LDAP_USERNAME, settings.LDAP_PW, auto_bind=True)
    conn.delete(delete_dn)

    # Return the result description as message
    # 'success' if the object was deleted
    # 'noSuchObject' if the object did not exist
    return conn.result['description']


def _mcomm_exclist_search(key, base):
    entry = ''
    logger.debug('Searching for umichExcListName={}'.format(key))
    server = Server(settings.LDAP_URI)
    conn = Connection(server, settings.LDAP_USERNAME, settings.LDAP_PW, auto_bind=True)
    conn.search(
        base,
        '(umichExcListName={})'.format(key),
        attributes=['*'],
        time_limit=settings.LDAP_TIME_LIMIT,
    )

    # TODO: check for more than one result returned
    if len(conn.entries) == 1:
        entry = conn.entries[0]
        logger.debug('Found dn={}'.format(entry.entry_dn))
    elif len(conn.entries) == 0:
        pass
    else:
        logger.error('multiple results found')
        raise ExcListError(message='multiple_results_found')

    return entry
