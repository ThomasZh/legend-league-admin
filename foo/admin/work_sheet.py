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
