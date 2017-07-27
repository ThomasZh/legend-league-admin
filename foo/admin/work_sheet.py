#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 7x24hs.com
# thomas@7x24hs.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import tornado.web
import logging
import time
import sys
import os
import uuid
import smtplib
import hashlib
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
from bson import json_util
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import *
from tornado.httputil import url_concat
from bson import json_util

from comm import *
from global_const import *


class AdminIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/index.html',
                admin=admin,
                counter=counter,
                api_domain=API_DOMAIN)


class ProfileEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/profile-edit.html',
                admin=admin,
                counter=counter,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        nickname = self.get_argument("nickname", "")
        avatar = self.get_argument("avatar", "")
        logging.info("try update myinfo nickname:[%r] avatar:[%r]", nickname, avatar)

        admin = self.get_admin_info()

        url = API_DOMAIN+"/api/myinfo"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode({"nickname":nickname, "avatar":avatar})
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)

        self.redirect("/admin/profile/edit")


class AdministratorsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/administrators.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN)


class FranchisesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/franchises.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN)


class SuppliersHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/suppliers.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN)


class TodoListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/todo-list.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN)


class TodoDetailHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        id = self.get_argument("id","")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        url = API_DOMAIN+"/api/leagues/"+admin['league_id']+"/franchises/"+id
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        franchise = data['rs']
        franchise['create_time'] = timestamp_datetime(franchise['create_time'])
        if not franchise['club'].has_key('img'):
            franchise['club']['img'] = ''

        self.render('admin/todo-detail.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                franchise=franchise,
                api_domain=API_DOMAIN)


class ArticlesIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        category_id = self.get_argument("category_id", "")
        logging.info("got category_id %r from argument", category_id)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        # query category_name by category_id
        url = API_DOMAIN+"/api/categories/" + category_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        category = data['rs']

        params = {"filter":"league", "league_id":admin['league_id'], "status":"publish", "category":category_id, "idx":0, "limit":20}
        url = url_concat(API_DOMAIN+"/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        articles = data['rs']
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        self.render('admin/articles-publish.html',
                admin=admin,
                access_token = access_token,
                counter=counter,
                articles=articles,
                category=category,
                api_domain=API_DOMAIN)


class ArticlesDetailHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        category_id = self.get_argument("category_id", "")
        logging.info("got category_id %r from argument", category_id)
        article_id = self.get_argument("id", "")
        logging.info("get article_id=[%r] from argument", article_id)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        url = API_DOMAIN+"/api/articles/"+article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        article = data['rs']

        # article
        url = API_DOMAIN+"/api/articles/"+article_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got article response %r", response.body)
        data = json_decode(response.body)
        article_info = data['rs']
        article_info['publish_time'] = timestamp_friendly_date(article_info['publish_time'])

        self.render('admin/articles-detail.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                article=article,
                article_info=article_info,
                api_domain=API_DOMAIN)


class GuestBookHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/guest-book.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN)


class GuestBookDetailHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        id = self.get_argument("id","")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        url = API_DOMAIN+"/api/guest-book/"+id
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        guest = data['rs']
        guest['create_time'] = timestamp_datetime(guest['create_time'])

        self.render('admin/guest-detail.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                guest=guest)


class NoticeBoardHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/notice-board.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN)


class NoticeCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/notice-create.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN)


class NoticeEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        category_id = self.get_argument("id", "")
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        url = API_DOMAIN+"/api/categories/"+category_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        category = data['rs']

        self.render('admin/notice-edit.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                category=category,
                api_domain=API_DOMAIN)


class MultimediasDraftHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        params = {"filter":"league", "league_id":admin['league_id'], "status":"draft"}
        url = url_concat(API_DOMAIN+"/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        multimedias = data['rs']

        self.render('admin/multimedias-draft.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                multimedias=multimedias,
                api_domain=API_DOMAIN)


class MultimediasPublishHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        params = {"filter":"league", "league_id":admin['league_id'], "status":"publish"}
        url = url_concat(API_DOMAIN+"/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        data = json_decode(response.body)
        multimedias = data['rs']

        self.render('admin/multimedias-publish.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                multimedias=multimedias,
                api_domain=API_DOMAIN)


class VendorBindingWxHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        # create wechat qrcode
        binding_wx_url = WX_NOTIFY_DOMAIN + "/bf/wx/leagues/" + admin['league_id'] + "/administrators/" + admin['account_id'] +"/binding"
        logging.info("got binding_wx_url %r", binding_wx_url)
        data = {"url": binding_wx_url}
        _json = json_encode(data)
        http_client = HTTPClient()
        response = http_client.fetch(QRCODE_CREATE_URL, method="POST", body=_json)
        logging.info("got response %r", response.body)
        qrcode_url = response.body
        logging.info("got qrcode_url %r", qrcode_url)

        self.render('admin/binding-wx.html',
                admin=admin,
                counter=counter,
                qrcode_url=qrcode_url,
                api_domain=API_DOMAIN)


# 积分提现记录
class ApplyCashoutHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('admin/apply-cashout.html',
                access_token=access_token,
                admin=admin,
                counter=counter,
                league_id=league_id,
                api_domain = API_DOMAIN)
