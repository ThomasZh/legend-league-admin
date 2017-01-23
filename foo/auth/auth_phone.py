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

from comm import *
from global_const import *


class AuthPhoneLoginHandler(BaseHandler):
    def get(self):
        logging.info(self.request)
        err_msg = ""
        self.render('auth/phone-login.html', err_msg=err_msg)

    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        phone = self.get_argument("lg_phone", "")
        pwd = self.get_argument("lg_pwd", "")
        remember = self.get_argument("lg_remember", "")
        logging.info("try login as phone:[%r] pwd:[%r] remember:[%r]", phone, pwd, remember)

        # login
        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/auth/token"
            http_client = HTTPClient()
            data = {"code":code,
                    "login":phone,
                    "pwd":pwd}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            session_ticket = json_decode(response.body)
            self.set_secure_cookie("access_token", session_ticket['access_token'])
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 404: Not Found':
                err_msg = "手机号码或密码不正确!"
                self.render('auth/phone-login.html', err_msg=err_msg)
                return

        self.redirect('/auth/welcome')


class AuthPhoneRegisterHandler(BaseHandler):
    def get(self):
        err_msg = ""
        self.render('auth/phone-register.html', err_msg=err_msg)

    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        phone = self.get_argument("reg_phone", "")
        pwd = self.get_argument("reg_pwd", "")
        logging.info("try register as phone:[%r] pwd:[%r]", phone, pwd)

        # register
        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/auth/accounts"
            http_client = HTTPClient()
            data = {"code":code,
                    "login":phone,
                    "pwd":pwd}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
            session_ticket = json_decode(response.body)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 409: Conflict':
                err_msg = "此手机号码已经注册!"
                self.render('auth/phone-register.html', err_msg=err_msg)
                return

        err_msg = "注册成功，请登录!"
        self.render('auth/phone-register.html', err_msg=err_msg)



class AuthPhoneLostPwdHandler(BaseHandler):
    def get(self):
        err_msg = "When you fill in your registered email address, you will be sent instructions on how to reset your password."
        self.render('auth/phone-lost-pwd.html', err_msg=err_msg)

    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        phone = self.get_argument("reset_phone", "")
        verify_code = self.get_argument("reset_verify_code", "")
        pwd = self.get_argument("reset_pwd", "")
        logging.info("try to reset password phone=[%r] verify_code=[%r] pwd=[%r]", phone, verify_code, pwd)

        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/auth/phone/reset-pwd"
            http_client = HTTPClient()
            data = {"code":code,
                    "phone":phone,
                    "verify_code":verify_code,
                    "pwd":pwd}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 404: Not Found':
                err_msg = "帐号不存在!"
                self.render('auth/phone-lost-pwd.html',
                        err_msg=err_msg)
                return
            elif err_detail == 'HTTP 401: Unauthorized':
                err_msg = "验证码不正确!"
                self.render('auth/phone-lost-pwd.html',
                        err_msg=err_msg)
                return
            elif err_detail == 'HTTP 408: Request Timeout':
                err_msg = "请求超时, 在5分钟内有效!"
                self.render('auth/phone-lost-pwd.html',
                        err_msg=err_msg)
                return

        err_msg = "密码修改成功, 请重新登录!"
        self.render('auth/phone-lost-pwd.html',
                err_msg=err_msg)


class AuthPhoneVerifyCodeHandler(BaseHandler):
    def post(self):
        logging.info(self.request)
        logging.info(self.request.body)
        req = json_decode(self.request.body)
        phone = req['phone']
        logging.info("try to send lost password sms to [%r]", phone)

        try:
            code = self.get_code()

            url = "http://api.7x24hs.com/auth/phone/verify-code"
            http_client = HTTPClient()
            data = {"code":code,
                    "phone":phone}
            _json = json_encode(data)
            logging.info("request %r body %r", url, _json)
            response = http_client.fetch(url, method="POST", body=_json)
            logging.info("got response %r", response.body)
        except:
            err_title = str( sys.exc_info()[0] );
            err_detail = str( sys.exc_info()[1] );
            logging.error("error: %r info: %r", err_title, err_detail)
            if err_detail == 'HTTP 404: Not Found':
                err_msg = "帐号不存在!"
                self.render('auth/forgot-pwd.html', err_msg=err_msg)
                return

        err_msg = "邮件已经发出, 请注意查收! 此邮件在5分钟内有效。"
        self.render('auth/phone-lost-pwd.html', err_msg=err_msg)
