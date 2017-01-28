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
from foo.admin import work_sheet


def map():

    config = [

        (r'/', getattr(work_sheet, 'AdminIndexHandler')),

        (r'/admin/auth/email/login', getattr(auth_email, 'AuthEmailLoginHandler')),
        (r'/admin/auth/email/register', getattr(auth_email, 'AuthEmailRegisterHandler')),
        (r'/admin/auth/email/forgot-pwd', getattr(auth_email, 'AuthEmailForgotPwdHandler')),
        (r'/admin/auth/email/reset-pwd', getattr(auth_email, 'AuthEmailResetPwdHandler')),
        (r'/admin/auth/welcome', getattr(auth_email, 'AuthWelcomeHandler')),
        (r'/admin/auth/logout', getattr(auth_email, 'AuthLogoutHandler')),
        (r'/admin/auth/phone/login', getattr(auth_phone, 'AuthPhoneLoginHandler')),
        (r'/admin/auth/phone/register', getattr(auth_phone, 'AuthPhoneRegisterHandler')),
        (r'/admin/auth/phone/verify-code', getattr(auth_phone, 'AuthPhoneVerifyCodeHandler')),
        (r'/admin/auth/phone/lost-pwd', getattr(auth_phone, 'AuthPhoneLostPwdHandler')),

        (r'/admin', getattr(work_sheet, 'AdminIndexHandler')),
        (r'/admin/profile/edit', getattr(work_sheet, 'ProfileEditHandler')),
        (r'/admin/administrators', getattr(work_sheet, 'AdministratorsHandler')),
        (r'/admin/todo-list', getattr(work_sheet, 'TodoListHandler')),

        # comm
        ('.*', getattr(comm, 'PageNotFoundHandler'))

    ]

    return config
