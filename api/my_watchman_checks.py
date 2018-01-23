from django.conf import settings
from watchman.decorators import check

from ldap3 import Server, Connection
import traceback

@check
def ldap():
    """
    Custom watchman check to make sure we can contact the ldap server
    """

    response = {
        'ok': True,
    }

    try:
        # Just test the connection
        server = Server(settings.LDAP_URI)
        conn = Connection(
            server,
            settings.LDAP_USERNAME,
            settings.LDAP_PW,
            auto_bind=True,
        )
        conn.unbind()
    except Exception as e:    # pragma: no cover
        response = {
            'ok': False,
            'error': str(e),
            'stacktrace': traceback.format_exc(),
        }


    return {
        'ldap': response,
    }
