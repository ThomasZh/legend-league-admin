#!/usr/bin/env python
# _*_ coding: utf-8_*_
#
# Copyright 2016 planc2c.com
# dev@tripc2c.com
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
import uuid
import time
import json as JSON # 启用别名，不会跟方法里的局部变量混淆
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../dao"))

from tornado.escape import json_encode, json_decode
from tornado.httpclient import HTTPClient
from tornado.httputil import url_concat
from bson import json_util

from global_const import *
from comm import *


# 审核提现申请(接受)
class ApiApplyCashoutAcceptXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, apply_id):
        logging.info(self.request)

        access_token = self.get_secure_cookie("access_token")
        admin = self.get_admin_info()
        league_id = admin['league_id']

        check_status = {}
        try:
            # {'_status':10, '_reason':''}
            check_status = json_decode(self.request.body)
        except:
            logging.warn("Bad Request[400]: update apply_cash_out check_status=[%r]", self.request.body)
            logging.info("~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~")
            logging.info("~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~")

            self.set_status(200) # Bad Request
            self.write(JSON.dumps({"err_code":400,"err_msg":"Bad Request"}))
            self.finish()
            return

        headers={"Authorization":"Bearer "+access_token}
        url = API_DOMAIN + "/api/points/leagues/"+league_id+"/apply-cash-out/"+ apply_id +"/check"
        http_client = HTTPClient()
        _json = json_encode(check_status)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got apply-cash-out check_status %r", response.body)

        # 取得提现申请信息
        apply_cashout = self.get_apply_cashout(league_id, apply_id)

        # 扣除积分，并添加一条日志记录
        bonus_points = {
            'org_id':apply_cashout['org_id'],
            'org_type':apply_cashout['org_type'],
            'account_id':apply_cashout['apply_org_id'],
            'account_type':apply_cashout['apply_org_type'],
            'action': 'cashout',
            'item_type': 'bonus',
            'item_id': DEFAULT_USER_ID,
            'item_name': apply_cashout['apply_org_name'],
            'bonus_type':'bonus',
            'points': -apply_cashout['bonus_point'],
            'order_id': DEFAULT_USER_ID
        }
        self.create_points(bonus_points)

        # budge_num decrease
        self.counter_decrease(league_id, "apply_cashout")

        # budge_num increase
        self.counter_increase(apply_cashout['apply_org_id'], "review_cashout")
        # TODO notify this message to vendor's administrator by SMS

        rs = {'err_code':200, 'err_msg':'Success'}
        self.write(JSON.dumps(rs, default=json_util.default))
        self.finish()


# 审核提现申请（拒绝）
class ApiApplyCashoutRejectXHR(AuthorizationHandler):
    @tornado.web.authenticated  # if no session, redirect to login page
    def post(self, apply_id):
        logging.info(self.request)

        access_token = self.get_secure_cookie("access_token")
        admin = self.get_admin_info()
        league_id = admin['league_id']

        check_status = {}
        try:
            # {'_status':10, '_reason':''}
            check_status = json_decode(self.request.body)
        except:
            logging.warn("Bad Request[400]: update apply_cash_out check_status=[%r]", self.request.body)
            logging.info("~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~")
            logging.info("~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~ ~~~~~")

            self.set_status(200) # Bad Request
            self.write(JSON.dumps({"err_code":400,"err_msg":"Bad Request"}))
            self.finish()
            return

        headers={"Authorization":"Bearer "+access_token}
        url = API_DOMAIN + "/api/points/leagues/"+league_id+"/apply-cash-out/"+ apply_id +"/check"
        http_client = HTTPClient()
        _json = json_encode(check_status)
        response = http_client.fetch(url, method="POST", headers=headers, body=_json)
        logging.info("got apply-cash-out check_status %r", response.body)

        # 取得提现申请信息
        apply_cashout = self.get_apply_cashout(league_id, apply_id)

        # budge_num decrease
        self.counter_decrease(league_id, "apply_cashout")

        # budge_num increase
        self.counter_increase(apply_cashout['apply_org_id'], "review_cashout")
        # TODO notify this message to vendor's administrator by SMS

        rs = {'err_code':200, 'err_msg':'Success'}
        self.write(JSON.dumps(rs, default=json_util.default))
        self.finish()
