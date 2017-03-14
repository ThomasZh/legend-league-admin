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

        self.render('admin/index.html',
                admin=admin)


class ProfileEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        admin = self.get_admin_info()

        self.render('admin/profile-edit.html',
                admin=admin)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        nickname = self.get_argument("nickname", "")
        avatar = self.get_argument("avatar", "")
        logging.info("try update myinfo nickname:[%r] avatar:[%r]", nickname, avatar)

        admin = self.get_admin_info()

        url = "http://api.7x24hs.com/api/myinfo"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer "+access_token}
        _json = json_encode({"nickname":nickname, "avatar":avatar})
        response = http_client.fetch(url, method="PUT", headers=headers, body=_json)
        logging.info("got response.body %r", response.body)

        self.redirect("/")


class AdministratorsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()

        self.render('admin/administrators.html',
                admin=admin)


class FranchisesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()

        self.render('admin/franchises.html',
                admin=admin)


class SuppliersHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()

        self.render('admin/suppliers.html',
                admin=admin)


class TodoListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        admin = self.get_admin_info()

        self.render('admin/todo-list.html',
                admin=admin)


class TodoDetailHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        id = self.get_argument("id","")

        admin = self.get_admin_info()

        url = "http://api.7x24hs.com/api/leagues/"+admin['league_id']+"/franchises/"+id
        http_client = HTTPClient()
        headers={"Authorization":"Bearer "+access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response %r", response.body)
        franchise= json_decode(response.body)
        franchise['create_time'] = timestamp_datetime(franchise['create_time'])
        if not franchise['club'].has_key('img'):
            franchise['club']['img'] = ''

        self.render('admin/todo-detail.html',
                admin=admin,
                franchise=franchise)


class ArticlesIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        category_id = self.get_argument("category_id", "")
        logging.info("got category_id %r from argument", category_id)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()

        # query category_name by category_id
        url = "http://api.7x24hs.com/api/categories/" + category_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        category = json_decode(response.body)

        params = {"filter":"league", "league_id":admin['league_id'], "status":"publish", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        self.render('admin/articles-publish.html',
                admin=admin,
                articles=articles,
                category=category)


class MultimediasDraftHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()

        params = {"filter":"league", "league_id":admin['league_id'], "status":"draft"}
        url = url_concat("http://api.7x24hs.com/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        multimedias = json_decode(response.body)

        self.render('admin/multimedias-draft.html',
                admin=admin,
                multimedias=multimedias)


class MultimediasPublishHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()

        params = {"filter":"league", "league_id":admin['league_id'], "status":"publish"}
        url = url_concat("http://api.7x24hs.com/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        multimedias = json_decode(response.body)

        self.render('admin/multimedias-publish.html',
                admin=admin,
                multimedias=multimedias)
