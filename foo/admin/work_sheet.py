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
        admin = self.get_myinfo_basic()
        self.render('admin/index.html',
                admin=admin)


class ProfileEditHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        admin = self.get_myinfo_basic()
        self.render('admin/profile-edit.html',
                admin=admin)

    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        nickname = self.get_argument("nickname", "")
        avatar = self.get_argument("avatar", "")
        logging.info("try update myinfo nickname:[%r] avatar:[%r]", nickname, avatar)

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
        admin = self.get_myinfo_basic()

        self.render('admin/administrators.html',
                admin=admin,
                league_id=LEAGUE_ID)


class FranchisesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_myinfo_basic()

        self.render('admin/franchises.html',
                admin=admin,
                league_id=LEAGUE_ID)


class SuppliersHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_myinfo_basic()

        self.render('admin/suppliers.html',
                admin=admin,
                league_id=LEAGUE_ID)


class TodoListHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        admin = self.get_myinfo_basic()

        self.render('admin/todo-list.html',
                admin=admin,
                league_id=LEAGUE_ID)


class TodoDetailHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        id = self.get_argument("id","")

        admin = self.get_myinfo_basic()

        url = "http://api.7x24hs.com/api/leagues/"+LEAGUE_ID+"/franchises/"+id
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
                league_id=LEAGUE_ID,
                franchise=franchise)


class ArticlesIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        category_id = self.get_argument("category_id", "")
        logging.info("got category_id %r from argument", category_id)
        access_token = self.get_secure_cookie("access_token")

        # query category_name by category_id
        url = "http://api.7x24hs.com/api/categories/" + category_id
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        category = json_decode(response.body)

        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"publish", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-publish.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category=category)


class ArticlesActivityHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        category_id = '0bbf89e2f73411e69a3c00163e023e51'

        # sceneries(活动)
        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"all", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-activity.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category_id=category_id)


class ArticlesTripRouterHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        category_id = '8853422e03a911e7998c00163e023e51'

        # sceneries(线路)
        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"all", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-triprouter.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category_id=category_id)


class ArticlesSceneryHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        category_id = '41c057a6f73411e69a3c00163e023e51'

        # sceneries(景点)
        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"all", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-scenery.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category_id=category_id)


class ArticlesNewsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        category_id = '30a56cb8f73411e69a3c00163e023e51'

        # news(新闻)
        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"all", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-news.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category_id=category_id)


class ArticlesJourneyHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        category_id = '01d6120cf73411e69a3c00163e023e51'

        # journey(游记)
        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"all", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-journey.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category_id=category_id)


class ArticlesPopularHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        category_id = '3801d62cf73411e69a3c00163e023e51'

        # popular(流行)
        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"all", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-popular.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category_id=category_id)


class ArticlesHotHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")
        category_id = '1b86ad38f73411e69a3c00163e023e51'

        # hot(热门)
        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"all", "category":category_id, "idx":0, "limit":20}
        url = url_concat("http://api.7x24hs.com/api/articles", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        articles = json_decode(response.body)
        for article in articles:
            article['publish_time'] = timestamp_friendly_date(article['publish_time'])

        admin = self.get_myinfo_basic()

        self.render('admin/articles-hot.html',
                admin=admin,
                league_id=LEAGUE_ID,
                articles=articles,
                category_id=category_id)


class MultimediasDraftHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"draft"}
        url = url_concat("http://api.7x24hs.com/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        multimedias = json_decode(response.body)

        admin = self.get_myinfo_basic()

        self.render('admin/multimedias-draft.html',
                admin=admin,
                league_id=LEAGUE_ID,
                multimedias=multimedias)


class MultimediasPublishHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        params = {"filter":"league", "league_id":LEAGUE_ID, "status":"publish"}
        url = url_concat("http://api.7x24hs.com/api/multimedias", params)
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response %r", response.body)
        multimedias = json_decode(response.body)

        admin = self.get_myinfo_basic()

        self.render('admin/multimedias-publish.html',
                admin=admin,
                league_id=LEAGUE_ID,
                multimedias=multimedias)
