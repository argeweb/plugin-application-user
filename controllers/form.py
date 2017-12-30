#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from datetime import datetime
from argeweb import Controller, scaffold, route_with, route, add_authorizations, auth, require_post
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from ..models.application_user_model import ApplicationUserModel


class Form(Controller):
    class Meta:
        default_view = 'json'
        Model = ApplicationUserModel

    class Scaffold:
        display_in_form = ['name', 'account', 'is_enable', 'sort', 'created', 'modified']
        display_in_list = ['name', 'account']

    @route
    def admin_search_application_user(self):
        self.meta.pagination_limit = 25
        scaffold.list(self)

    @route
    @require_post
    @route_with(name='form:user:login_by_account')
    def login_by_account(self):
        self.context['data'] = {'result': 'failure', 'message': u'帳號密碼有誤，或帳號不存在'}

        input_account = self.params.get_string('account')
        input_password = self.params.get_string('password')
        if input_account == u'' or input_password == u'':
            self.context['message'] = u'帳號密碼不可為空'
            return

        application_user = self.meta.Model.get_user(input_account, input_password)
        if application_user is None:
            if self.meta.Model.has_record():
                return

        self.session['application_user_key'] = application_user.key
        self.context['data'] = {'result': 'success'}

    @route
    @require_post
    @route_with(name='form:user:login_by_email')
    def login_by_email(self):
        input_remember_account = self.params.get_string('remember_account')
        input_email = self.params.get_string('email')
        input_password = self.params.get_string('password').strip()
        if input_email == u'' or input_password == u'':
            return self.json_failure_message(u'帳號密碼不可為空')

        application_user = self.meta.Model.get_user_by_email_and_password(input_email, input_password)
        if application_user is None and self.meta.Model.has_record():
            return self.json_failure_message(u'帳號密碼有誤，或帳號不存在')

        if input_remember_account:
            self.session['remember_account'] = input_email
        self.session['application_user_key'] = application_user.key
        self.context['data'] = {'result': 'success'}

    @route
    @require_post
    @route_with(name='form:user:create_by_email_and_password')
    def create_by_email_and_password(self):
        self.response.headers.setdefault('Access-Control-Allow-Origin', '*')
        self.context['data'] = {'result': 'failure'}

        input_email = self.params.get_string('email')
        input_password = self.params.get_string('password').strip()
        input_account = self.params.get_string('account', None)
        input_user_name = self.params.get_string('user_name', None)
        input_federated_id = self.params.get_string('federated_id', None)
        input_confirm_password = self.params.get_string('confirm_password').strip()
        if input_email is u'' and input_account is not None:
            input_email = input_account
        if input_email == u'' or input_password == u'':
            self.context['message'] = u'帳號密碼不可為空'
            return

        if input_password != input_confirm_password:
            self.context['message'] = u'密碼不相同，請輸入一致的密碼'
            return

        if input_account is not None and input_account == u'':
            input_account = None
        if input_account is not None:
            application_user = self.meta.Model.get_user_by_account(input_account)
            if application_user:
                self.context['message'] = u'此帳號已經註冊過了'
                return
        else:
            application_user = self.meta.Model.get_user_by_email(input_email)
            if application_user:
                self.context['message'] = u'此 email 已經註冊過了'
                return

        application_user = self.meta.Model.create_account_by_email(
            input_email, input_password, account=input_account, user_name=input_user_name)
        if input_federated_id is not None:
            application_user.federated_id = input_federated_id
            application_user.put()
        self.session['application_user_key'] = application_user.key
        self.fire('after_user_signup', user=application_user)
        self.context['message'] = u'註冊完成'
        self.context['data'] = {'result': 'success'}

    @route
    @route_with(name='form:user:reset_password_with_token')
    def reset_password_with_token(self):
        input_token = self.params.get_string('token').strip()
        input_password = self.params.get_string('password').strip()
        input_confirm_password = self.params.get_string('confirm_password').strip()
        self.context['data'] = {'result': 'failure'}
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
        self.context['data'] = {'result': 'success'}
        self.context['message'] = u'密碼已重新設置'

    @route
    @require_post
    @route_with(name='form:user:send_email_to_reset_password')
    def send_email_to_reset_password(self):
        self.context['data'] = {'result': 'failure'}

        input_email = self.params.get_string('email')
        if input_email == u'':
            self.context['message'] = u'請填寫 E-Mail '
            return

        application_user = self.meta.Model.get_user_by_email(input_email)
        if application_user is None:
            self.context['message'] = u'查無此用戶'
            return

        application_user.gen_password_token()
        application_user.put()

        r = self.fire('user_request_email_reset', user=application_user)
        for item in r:
            if item['status'] == 'success':
                self.context['data'] = {'result': 'success'}
                self.context['message'] = u'密碼重置郵件已寄出'
            else:
                self.context['data'] = {'result': item['status']}
                self.context['message'] = item['message']

    @route
    @require_post
    @route_with(name='form:user:logout')
    def logout(self):
        self.session['application_user_key'] = None
        self.session['application_user_level'] = None
        self.context['data'] = {
            'result': 'success'
        }
