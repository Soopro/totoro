# coding=utf-8
from __future__ import absolute_import


class OPError(Exception):

    base_message = 'WECHAT_ERROR'

    errcode = 0
    errmsg = u''

    def __init__(self, error):
        if isinstance(error, dict):
            self.errcode = error.get('errcode', 0)
            self.errmsg = error.get('errmsg', u'')
            message = u'({}) {}'.format(self.errcode, self.errmsg)
        elif isinstance(error, Exception):
            if hasattr(error, 'message'):
                message = unicode(error.message)
            if hasattr(error, 'errcode'):
                self.errcode = error.errcode
            if hasattr(error, 'errmsg'):
                self.errmsg = error.errmsg
        elif isinstance(error, basestring):
            self.errmsg = error
            message = error
        else:
            message = u''
        super(OPError, self).__init__(message)

    def __str__(self):
        if self.message:
            return u'{}: <{}>'.format(self.base_message, self.message)
        else:
            return self.base_message


class APIOverrun(OPError):
    base_message = 'WECHAT_API_OVERRUN'


class APIBusy(OPError):
    base_message = 'WECHAT_API_IS_BUSY'


class APIUnauthorized(OPError):
    base_message = 'WECHAT_API_UNAUTHORIZED'


class APINotIPWhitelist(OPError):
    base_message = 'WECHAT_API_NOT_IN_WHITELIST'


class ParameterStructureError(OPError):
    base_message = 'WECHAT_API_PARAMETER_STRUCTURE_ERROR'


class ReceiveError(OPError):
    base_message = 'WECHAT_API_RECEIVE_ERROR'


class ResponseError(OPError):
    base_message = 'WECHAT_API_RESPONSE_ERROR'


class MerchantError(OPError):
    base_message = 'WECHAT_API_MERCHANT_ERROR'
