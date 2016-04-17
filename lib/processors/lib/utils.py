from tornado import gen

from .exhibit_permissions import ExhibitPermissions
from ...rfidb import RFIDB
from ...basehandler import BaseHandler
from ...user import User


def auth(val):
    """
    Decorate a processor's handler function with an explicit authorization
    value to override the class default
    """
    def auth(fxn):
        fxn.auth = False
        return fxn
    return auth


def process_api_handler(get_handlers):
    def _(self):
        handlers = get_handlers(self)
        result = []
        checkauth = self.auth
        result.append(('/{}'.format(self.name),
                       make_permcheck(self.name, checkauth)))
        for path, handler in handlers:
            auth = getattr(handler, 'auth', checkauth)
            route = ("/{}/{}".format(self.name, path),
                     make_handler(self.name, handler, auth))
            result.append(route)
        return result
    return _


def make_handler(name, handler, checkauth):
    class ProcAPIHandler(BaseHandler):
        @gen.coroutine
        def process_request(self):
            userid = self.get_argument('userid', None)
            rfid = self.get_argument('rfid', None)
            if checkauth and not (userid is None) ^ (rfid is None):
                return self.error(400, 'userid or rfid required')

            privatekey_pem = self.get_argument('privatekey', None)
            publickey_pem = self.get_argument('publickey', None)
            user = None
            if userid:
                user = User(userid, publickey_pem=publickey_pem,
                            privatekey_pem=privatekey_pem)
            elif rfid:
                rfidb = yield RFIDB.get_global()
                user = yield rfidb.rfid_to_user(rfid)
                userid = user.userid
            if checkauth:
                exibperm = yield ExhibitPermissions.get_global()
                permission = yield exibperm.has_permission(userid, name)
                if permission is not True:
                    return self.error(403, "NO_ACCESS: {}".format(userid))
            data = yield handler(user, self)
            return self.api_response(data)

        @gen.coroutine
        def get(self):
            yield self.process_request()

        @gen.coroutine
        def post(self):
            yield self.process_request()

    return ProcAPIHandler


def make_permcheck(name, checkauth):
    class CheckPermissionHandler(BaseHandler):
        @gen.coroutine
        def get(self):
            userids = self.get_arguments('userid')
            if not checkauth:
                return [{'userid': uid, 'permission': True} for uid in userids]
            exibperm = yield ExhibitPermissions.get_global()
            result = []
            for userid in userids:
                permission = yield exibperm.has_permission(userid, name)
                result.apend({"userid": userid, "permission": permission})
            return result
    return CheckPermissionHandler
