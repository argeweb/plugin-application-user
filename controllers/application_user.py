#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search


class ApplicationUser(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)

    class Scaffold:
        display_in_form = ['name', 'account', 'is_enable', 'sort', 'created', 'modified']
        hidden_in_form = ['rest_password_token']
        display_in_list = ['name', 'account', 'email', 'is_enable', 'created']
        actions_in_list = [{
            'name': 'role_list',
            'title': u'角色',
            'uri': 'admin:application_user:application_user:set_role',
            'button': u'角色'
        }]

    def __init__(self, *args, **kwargs):
        super(ApplicationUser, self).__init__(*args, **kwargs)
        self.target = None
        self.target_level = 0
        self.application_user_level = 0

    @route_with('/application_user_init')
    def application_user_init(self):
        self.fire('application_user_init')
        return self.redirect('/')

    def check_level(self, target):
        self.target = target
        self.application_user_level = self.application_user.get_role_level()
        if self.application_user_level < self.target_level:
            return False
        return True

    @route
    def admin_set_role(self, source):
        if self.check_level(self.params.get_ndb_record(source)) is False:
            return self.abort(403)
        from ..models.role_model import RoleModel
        from ..models.user_role_model import UserRoleModel
        roles = RoleModel.get_list()
        user_roles = UserRoleModel.get_user_roles(self.application_user)
        for role in roles:
            has_role = False
            for user_role in user_roles:
                if role.name == user_role.role_name:
                    has_role = True
            setattr(role, 'has_role', has_role)
        self.context['application_user'] = self.application_user
        self.context['roles'] = roles

    @route
    def admin_set_user_role(self, key):
        self.meta.change_view('json')
        self.scaffold.scaffold_type = 'set_boolean_field'
        user = self.params.get_ndb_record(key)
        role = self.params.get_ndb_record('role')
        role_value = self.params.get_boolean('value')
        from ..models.user_role_model import UserRoleModel
        if role_value:
            UserRoleModel.set_role(user, role)
            val_word = u'啟用'
        else:
            UserRoleModel.remove_role(user, role)
            val_word = u'停用'
        self.context['data'] = {'info': 'success'}
        self.context['message'] = u'%s 已 %s' % (role.title, val_word)

    @route_menu(list_name=u'backend', group=u'帳號管理', text=u'帳號管理', sort=9801, icon='users')
    def admin_list(self):
        self.context['application_user_key'] = self.application_user.key
        self.context['application_user_level'] = self.application_user.get_role_level()
        scaffold.list(self)
        for item in self.context[self.scaffold.plural]:
            item.level = item.get_role_level()

    @csrf_protect
    def admin_add(self):
        def bycrypt_password(**kwargs):
            item = kwargs['item']
            item.bycrypt_password()
            item.try_to_create_user_role()
        self.events.scaffold_after_save += bycrypt_password
        return scaffold.add(self)

    @csrf_protect
    def admin_edit(self, key):
        def scaffold_before_validate(**kwargs):
            parser = kwargs['parser']
            item = kwargs['item']
            item.old_password = item.password
            item.new_password = parser.data['password']

            def validate():
                if self.application_user_level < self.target_level:
                    parser.errors['role'] = u'您的權限等級低於此角色'
                    return False
                return parser.container.validate() if parser.container else False
            parser.validate = validate

        def bycrypt_password(**kwargs):
            item = kwargs['item']
            item.bycrypt_password_with_old_password()
            item.try_to_create_user_role()

        if self.check_level(self.params.get_ndb_record(key)) is False:
            return self.abort(403)
        self.events.scaffold_before_validate += scaffold_before_validate
        self.events.scaffold_after_save += bycrypt_password
        if self.target.key == self.application_user.key:
            self.Scaffold.hidden_in_form.append('is_enable')
        return scaffold.edit(self, key)

    @route
    def admin_login_for_test(self):
        self.session['application_user_key'] = self.session['application_admin_user_key']
        return str(self.session['application_admin_user_key'])

    @csrf_protect
    @route
    @route_menu(list_name=u'system', group=u'帳號管理', text=u'資料變更', sort=9998, icon=u'account_box')
    def admin_profile(self):
        def scaffold_before_validate(**kwargs):
            parser = kwargs['parser']
            item = kwargs['item']
            change_level = item.get_role_level()
            item.old_password = item.password
            item.new_password = parser.data['password']

            def validate():
                try:
                    _validate = parser.container.validate()
                    if _validate:
                        return parser.container
                except:
                    return False
            # parser.validate = validate

        def bycrypt_password(**kwargs):
            item = kwargs['item']
            item.bycrypt_password_with_old_password()

        self.context['change_view_to_view_function'] = ''
        self.events.scaffold_before_validate += scaffold_before_validate
        self.events.scaffold_after_save += bycrypt_password
        self.Scaffold.hidden_in_form.append('is_enable')
        return scaffold.edit(self, self.application_user.key)

    def admin_delete(self, key):
        if self.check_level(self.params.get_ndb_record(key)) is False:
            return self.abort(403)
        return scaffold.delete(self, key)

    @route_with('/login.json')
    def login_json(self):
        self.meta.change_view('json')
        self.context['data'] = {
            'is_login': u'false'
        }
        if self.request.method != 'POST':
            return
        input_account = self.params.get_string('account')
        input_password = self.params.get_string('password')
        self.logging.info(input_account + input_password)
        application_user = self.meta.Model.get_user(input_account, input_password)
        if application_user is None:
            if self.meta.Model.has_record():
                return
        self.session['application_user_key'] = application_user.key
        self.context['data'] = {
            'is_login': 'true'
        }

    @route
    def login_by_email_json(self):
        self.meta.change_view('json')
        self.context['data'] = {
            'is_login': u'false'
        }
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
        self.context['data'] = {
            'is_login': 'true'
        }

    @route
    def create_by_email_and_password_json(self):
        self.meta.change_view('json')
        self.context['data'] = {
            'is_login': u'false'
        }
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
        self.context['data'] = {
            'is_login': 'true'
        }

    @route_with('/logout')
    def logout(self):
        self.session['application_user_key'] = None
        return self.redirect('/')

    @route_with('/logout.json')
    def logout_json(self):
        self.meta.change_view('json')
        self.session['application_user_key'] = None
        self.context['data'] = {
            'is_login': 'false'
        }
