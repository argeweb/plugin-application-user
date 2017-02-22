#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu, route_with, route, settings
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from ..models.application_user_model import ApplicationUserModel
import httplib2
from urllib import urlencode

class Api(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)
        pagination_actions = ('list',)
        pagination_limit = 50
        default_view = 'json'
        Model = ApplicationUserModel

    class Scaffold:
        display_in_form = ('name', 'account', 'is_enable', 'sort', 'created', 'modified')
        display_in_list = ('name', 'account')

    @route
    def login(self):
        self.context['data'] = {'is_login': 'false'}
        if self.request.method != 'POST':
            return

        input_account = self.params.get_string('account')
        input_password = self.params.get_string('password')
        if input_account == u'' or input_password == u'':
            return

        application_user = self.meta.Model.get_user(input_account, input_password)
        if application_user is None:
            if self.meta.Model.has_record():
                return

        self.session['application_user_key'] = application_user.key
        self.context['data'] = {'is_login': 'true'}

    @route
    def login_by_email(self):
        self.context['data'] = {'is_login': 'false'}
        if self.request.method != 'POST':
            return

        input_email = self.params.get_string('email').strip()
        input_password = self.params.get_string('password').strip()
        if input_email == u'' or input_password == u'':
            return

        application_user = self.meta.Model.get_user_by_email(input_email, input_password)
        if application_user is None:
            if self.meta.Model.has_record():
                return

        self.session['application_user_key'] = application_user.key
        self.context['data'] = {'is_login': 'true'}

    @route
    def create_by_email_and_password(self):
        self.context['data'] = {'create': 'failure'}
        if self.request.method != 'POST':
            self.context['message'] = u'只接受 Post 的資料'
            return

        input_email = self.params.get_string('email').strip()
        input_password = self.params.get_string('password').strip()
        input_confirm_password = self.params.get_string('confirm_password').strip()
        if input_email == u'' or input_password == u'':
            self.context['message'] = u'帳號密碼不可為空'
            return

        if input_password != input_confirm_password:
            self.context['message'] = u'密碼不相同，請輸入一致的密碼'
            return

        application_user = self.meta.Model.check_user_by_email(input_email)
        if application_user:
            self.context['message'] = u'此 email 已經註冊過了'
            return

        application_user = self.meta.Model.create_account_by_email(input_email, input_password)
        self.session['application_user_key'] = application_user.key
        self.context['message'] = u'註冊完成'
        self.context['data'] = {'create': 'success'}

    @route
    def send_email_to_reset_password(self):
        self.context['data'] = {'send_email': 'failure'}
        MAILGUN_DOMAIN_NAME = 'yooliang.com'
        http = httplib2.Http()
        http.add_credentials('api', 'key-4df974aaafbe668bfd9b3539d14987e3')

        url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
        data = {
            'from': 'Example Sender <mailgun@{}>'.format(MAILGUN_DOMAIN_NAME),
            'to': self.params.get_string('email'),
            'subject': 'This is an example email from Mailgun',
            'text': 'Test message from Mailgun'
        }

        resp, content = http.request(
            url, 'POST', urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"})

        if resp.status != 200:
            raise RuntimeError(
                'Mailgun API error: {} {}'.format(resp.status, content))

        if self.request.method != 'POST':
            self.context['message'] = u'只接受 Post 的資料'
            return

        input_email = self.params.get_string('email').strip()
        if input_email == u'':
            self.context['message'] = u'請填寫 E-Mail '
            return

        application_user = self.meta.Model.check_user_by_email(input_email)
        if application_user is False:
            self.context['message'] = u'查無此用戶'
            return

        self.context['data'] = {'send_email': 'success'}
        self.context['message'] = u'密碼重置郵件已寄出'


    @route
    def logout(self):
        self.session['application_user_key'] = None
        self.session['application_user_level'] = None
        self.context['data'] = {
            'is_login': u'false',
            'logout': 'success'
        }