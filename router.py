# _*_ coding: utf-8_*_
#
# genral application route config:
# simplify the router config by dinamic load class
# by lwz7512
# @2016/05/17

import tornado.web

from foo import comm
from foo.auth import auth_email
from foo.auth import auth_phone


def map():

    config = [

        (r'/', getattr(auth_email, 'AuthWelcomeHandler')),
        
        (r'/auth/email/login', getattr(auth_email, 'AuthEmailLoginHandler')),
        (r'/auth/email/register', getattr(auth_email, 'AuthEmailRegisterHandler')),
        (r'/auth/email/forgot-pwd', getattr(auth_email, 'AuthEmailForgotPwdHandler')),
        (r'/auth/email/reset-pwd', getattr(auth_email, 'AuthEmailResetPwdHandler')),
        (r'/auth/welcome', getattr(auth_email, 'AuthWelcomeHandler')),
        (r'/auth/logout', getattr(auth_email, 'AuthLogoutHandler')),
        (r'/auth/phone/login', getattr(auth_phone, 'AuthPhoneLoginHandler')),
        (r'/auth/phone/register', getattr(auth_phone, 'AuthPhoneRegisterHandler')),
        (r'/auth/phone/verify-code', getattr(auth_phone, 'AuthPhoneVerifyCodeHandler')),
        (r'/auth/phone/lost-pwd', getattr(auth_phone, 'AuthPhoneLostPwdHandler')),

        # comm
        ('.*', getattr(comm, 'PageNotFoundHandler'))

    ]

    return config
