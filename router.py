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
from foo.admin import category
from foo.api import api_point


def map():

    config = [

        (r'/', getattr(work_sheet, 'FranchisesHandler')),

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
        (r'/admin/setup/binding-wx', getattr(work_sheet, 'VendorBindingWxHandler')),
        (r'/admin/administrators', getattr(work_sheet, 'AdministratorsHandler')),
        (r'/admin/franchises', getattr(work_sheet, 'FranchisesHandler')),
        (r'/admin/position', getattr(work_sheet, 'PositionHandler')),
        (r'/admin/ticket', getattr(work_sheet, 'TicketHandler')),
        (r'/admin/suppliers', getattr(work_sheet, 'SuppliersHandler')),
        (r'/admin/todo-list', getattr(work_sheet, 'TodoListHandler')),
        (r'/admin/todo-detail', getattr(work_sheet, 'TodoDetailHandler')),
        (r'/admin/multimedias/draft', getattr(work_sheet, 'MultimediasDraftHandler')),
        (r'/admin/multimedias/publish', getattr(work_sheet, 'MultimediasPublishHandler')),
        (r'/admin/apply-cashout', getattr(work_sheet, 'ApplyCashoutHandler')),

        (r'/admin/guest-book', getattr(work_sheet, 'GuestBookHandler')),
        (r'/admin/guest-detail', getattr(work_sheet, 'GuestBookDetailHandler')),
        (r'/admin/notice-board', getattr(work_sheet, 'NoticeBoardHandler')),
        (r'/admin/notice-create', getattr(work_sheet, 'NoticeCreateHandler')),
        (r'/admin/notice-edit', getattr(work_sheet, 'NoticeEditHandler')),
        (r'/admin/notice-edit', getattr(work_sheet, 'NoticeEditHandler')),

        (r'/admin/categories/franchises', getattr(category, 'CategoriesFranchisesHandler')),
        (r'/admin/categories/tags', getattr(category, 'CategoriesTagsHandler')),
        (r'/admin/categories/tags/franchises', getattr(category, 'CategoriesTagsFranchisesHandler')),
        (r'/admin/categories/create', getattr(category, 'CategoriesCreateHandler')),
        (r'/admin/categories/index', getattr(category, 'CategoriesIndexHandler')),
        (r'/admin/categories/edit', getattr(category, 'CategoriesEditHandler')),

        (r'/admin/articles', getattr(work_sheet, 'ArticlesIndexHandler')),
        (r'/admin/articles/detail', getattr(work_sheet, 'ArticlesDetailHandler')),

        (r'/admin/api/apply-cash-out/([a-z0-9]*)/accept', getattr(api_point, 'ApiApplyCashoutAcceptXHR')),
        (r'/admin/api/apply-cash-out/([a-z0-9]*)/reject', getattr(api_point, 'ApiApplyCashoutRejectXHR')),

        # comm
        ('.*', getattr(comm, 'PageNotFoundHandler'))

    ]

    return config
