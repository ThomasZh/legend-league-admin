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


def map():

    config = [

        (r'/', getattr(work_sheet, 'ClubsHandler')),

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
        (r'/admin/clubs', getattr(work_sheet, 'ClubsHandler')),
        (r'/admin/todo-list', getattr(work_sheet, 'TodoListHandler')),
        (r'/admin/multimedias/draft', getattr(work_sheet, 'MultimediasDraftHandler')),
        (r'/admin/multimedias/publish', getattr(work_sheet, 'MultimediasPublishHandler')),

        (r'/admin/categories/create', getattr(category, 'CategoriesCreateHandler')),
        (r'/admin/categories/index', getattr(category, 'CategoriesIndexHandler')),
        (r'/admin/categories/edit', getattr(category, 'CategoriesEditHandler')),

        (r'/admin/articles/activity', getattr(work_sheet, 'ArticlesActivityHandler')),
        (r'/admin/articles/trip-router', getattr(work_sheet, 'ArticlesTripRouterHandler')),
        (r'/admin/articles/scenery', getattr(work_sheet, 'ArticlesSceneryHandler')),
        (r'/admin/articles/news', getattr(work_sheet, 'ArticlesNewsHandler')),
        (r'/admin/articles/journey', getattr(work_sheet, 'ArticlesJourneyHandler')),
        (r'/admin/articles/popular', getattr(work_sheet, 'ArticlesPopularHandler')),
        (r'/admin/articles/hot', getattr(work_sheet, 'ArticlesHotHandler')),

        # comm
        ('.*', getattr(comm, 'PageNotFoundHandler'))

    ]

    return config
