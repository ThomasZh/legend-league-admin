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

# 景区分类列表页
class CategoriesFranchisesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        admin = self.get_admin_info()
        league_id = admin['league_id']

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        params = {"_type":"scenery"}
        url = url_concat(API_DOMAIN + "/api/def/leagues/"+ LEAGUE_ID +"/categories",params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        categorys = data['rs']

        counter = self.get_counter(league_id)
        self.render('category/category-franchises.html',
                admin=admin,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                counter=counter,
                categorys=categorys,
                league_id=league_id)


# 二级分类
class CategoriesTagsHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        admin = self.get_admin_info()
        league_id = admin['league_id']

        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        category_id = self.get_argument('category_id','')
        logging.info("get category_id",category_id)

        # TODO: get second_category info
        url = API_DOMAIN + "/api/def/categories/"+ category_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_category_info = data['rs']

        url = API_DOMAIN + "/api/def/categories/"+ category_id +"/level2"
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_categorys = data['rs']

        counter = self.get_counter(league_id)
        self.render('category/tags.html',
                admin=admin,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                counter=counter,
                category_id=category_id,
                second_category_info=second_category_info,
                second_categorys=second_categorys,
                league_id=league_id)


# /tag下的商品
class CategoriesTagsFranchisesHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        admin = self.get_admin_info()
        league_id = admin['league_id']
        access_token = self.get_access_token()
        logging.info("GET access_token %r", access_token)

        second_categorys_id = self.get_argument('second_categorys_id','')
        logging.info("get second_categorys_id",second_categorys_id)

        # TODO: get second_category info
        url = API_DOMAIN + "/api/def/categories/"+ second_categorys_id
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        second_category_info = data['rs']

        # 获取景区列表
        params = {"filter":"league", "franchise_type":"景区", "page":1, "limit":200}
        url = url_concat(API_DOMAIN + "/api/leagues/"+ league_id +"/clubs", params)
        http_client = HTTPClient()
        headers = {"Authorization":"Bearer " + access_token}
        response = http_client.fetch(url, method="GET", headers=headers,)
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        franchises = data['rs']['data']

        counter = self.get_counter(league_id)
        self.render('category/tags-franchises.html',
                admin=admin,
                access_token=access_token,
                API_DOMAIN=API_DOMAIN,
                counter=counter,
                second_categorys_id=second_categorys_id,
                second_category_info=second_category_info,
                franchises=franchises)


class CategoriesIndexHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        url = API_DOMAIN+"/api/leagues/"+admin['league_id']+"/categories"
        http_client = HTTPClient()
        response = http_client.fetch(url, method="GET")
        logging.info("got response.body %r", response.body)
        data = json_decode(response.body)
        categories = data['rs']

        self.render('category/index.html',
                admin=admin,
                counter=counter,
                categories=categories,
                api_domain=API_DOMAIN)


class CategoriesCreateHandler(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def get(self):
        logging.info(self.request)
        access_token = self.get_secure_cookie("access_token")

        admin = self.get_admin_info()
        league_id = admin['league_id']
        counter = self.get_counter(league_id)

        self.render('category/create.html',
                admin=admin,
                counter=counter,
                access_token=access_token,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET)


class CategoriesEditHandler(AuthorizationHandler):
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

        self.render('category/edit.html',
                admin=admin,
                counter=counter,
                category=category,
                access_token=access_token,
                api_domain=API_DOMAIN,
                upyun_domain=UPYUN_DOMAIN,
                upyun_notify_url=UPYUN_NOTIFY_URL,
                upyun_form_api_secret=UPYUN_FORM_API_SECRET,
                upyun_bucket=UPYUN_BUCKET)
