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

        application_user = self.meta.Model.get_user_by_email_and_password(input_email, input_password)
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

        application_user = self.meta.Model.get_user_by_email(input_email)
        if application_user:
            self.context['message'] = u'此 email 已經註冊過了'
            return

        application_user = self.meta.Model.create_account_by_email(input_email, input_password)
        self.session['application_user_key'] = application_user.key
        self.context['message'] = u'註冊完成'
        self.context['data'] = {'create': 'success'}

    @route
    def reset_password_with_token(self):
        input_token = self.params.get_string('token').strip()
        input_password = self.params.get_string('password').strip()
        input_confirm_password = self.params.get_string('confirm_password').strip()
        self.context['data'] = {'reset_password': 'failure'}
        if input_token == u'':
            self.context['message'] = u'請重新產生 token'
            return

        if input_password == u'':
            self.context['message'] = u'密碼不可為空'
            return

        if input_password != input_confirm_password:
            self.context['message'] = u'密碼不相同，請輸入一致的密碼'
            return

        application_user = self.meta.Model.get_user_by_rest_password_token(input_token)
        if application_user is None:
            self.context['message'] = u'此 token 已經使用或不存在，或者是該帳戶已被停用'
            return

        application_user.rest_password_token = u''
        application_user.password = input_password
        application_user.bycrypt_password()
        application_user.put()
        self.context['data'] = {'reset_password': 'success'}
        self.context['message'] = u'密碼已重新設置'

    @route
    def send_email_to_reset_password(self):
        self.context['data'] = {'send_email': 'failure'}

        if self.request.method != 'POST':
            self.context['message'] = u'只接受 Post 的資料'
            return

        input_email = self.params.get_string('email').strip()
        if input_email == u'':
            self.context['message'] = u'請填寫 E-Mail '
            return

        application_user = self.meta.Model.get_user_by_email(input_email)
        if application_user is None:
            self.context['message'] = u'查無此用戶'
            return
        try:
            from plugins.mail import Mail
            import datetime
            import random, string
            r = ''.join(random.choice(string.lowercase) for i in range(25))
            application_user.rest_password_token = u'%s-%s-%s-%s' % (r[0:4], r[5:9], r[10:14], r[15:19])
            application_user.put()

            mail = Mail(self)
            r = mail.send_width_template('send_email_to_reset_password', application_user.email, {
                'site_name': self.host_information.site_name,
                'name': application_user.name,
                'created_date': self.util.localize_time(datetime.datetime.now()),
                'domain': self.host_information.host,
                'token': application_user.rest_password_token
            })
            if r['status'] == 'success':
                self.context['data'] = {'send_email': 'success'}
                self.context['message'] = u'密碼重置郵件已寄出'
            else:
                self.context['data'] = {'send_email': r['status']}
                self.context['message'] = r['message']
        except ImportError:
            self.context['message'] = u'郵件組件未載入或未啟用'
        except:
            self.context['message'] = u'郵件寄送時發生錯誤了'

    @route
    def logout(self):
        self.session['application_user_key'] = None
        self.session['application_user_level'] = None
        self.context['data'] = {
            'is_login': u'false',
            'logout': 'success'
        }