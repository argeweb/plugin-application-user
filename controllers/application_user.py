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


class ApplicationUser(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)

    class Scaffold:
        display_in_form = ('name', 'account', 'is_enable', 'sort', 'created', 'modified')
        hidden_in_form = ['rest_password_token']
        display_in_list = ('name', 'account', 'email', 'is_enable', 'created')

    @route_with('/application_user_init')
    def application_user_init(self):
        prohibited_actions = settings.get('application_user_prohibited_actions', u'')
        from ...application_user import application_user_init
        application_user_init(u'管理員', 'admin', "qwER12#$", prohibited_actions,
                             '/plugins/backend_ui_material/static/images/users/avatar-001.jpg')
        return self.redirect('/')

    @route_menu(list_name=u'backend', text=u'帳號管理', sort=9801, icon='users', group=u'帳號管理', need_hr_parent=True)
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
        self.events.scaffold_after_save += bycrypt_password
        return scaffold.add(self)

    @csrf_protect
    def admin_edit(self, key):
        target = self.params.get_ndb_record(key)
        target_level = target.get_role_level()
        self.application_user_level = self.application_user.get_role_level()
        if self.application_user_level < target_level:
            return self.abort(403)

        def scaffold_before_validate(**kwargs):
            parser = kwargs['parser']
            item = kwargs['item']
            item.old_password = item.password
            item.new_password = parser.data['password']

            def validate():
                if self.application_user_level < target_level:
                    parser.errors['role'] = u'您的權限等級低於此角色'
                    return False
                return parser.container.validate() if parser.container else False
            parser.validate = validate

        def bycrypt_password(**kwargs):
            item = kwargs['item']
            item.bycrypt_password_with_old_password()

        self.events.scaffold_before_validate += scaffold_before_validate
        self.events.scaffold_after_save += bycrypt_password
        return scaffold.edit(self, key)

    def require_high_level_role(controller):
        """
        Authorization chain that validates the CSRF token.
        """
        if controller.request.method in ('POST', 'PUT') and not controller.request.path.startswith('/taskqueue'):
            token = controller.session.get('_csrf_token')
            if not token or str(token) != str(controller.request.get('csrf_token')):
                return False, 'Cross-site request forgery failure'
        return True

    @csrf_protect
    @route
    def admin_profile(self):
        self.context['change_view_to_view_function'] = ''
        def scaffold_before_validate(**kwargs):
            parser = kwargs['parser']
            change_level = parser.data['role'].get().level
            item = kwargs['item']
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

        self.events.scaffold_before_validate += scaffold_before_validate
        self.events.scaffold_after_save += bycrypt_password
        return scaffold.edit(self, self.application_user.key)

    def admin_delete(self, key):
        target = self.params.get_ndb_record(key)
        self.application_user_level = self.application_user.get_role_level()
        target_level = target.get_role_level()
        self.logging.info('self.application_user_level = %s' % self.application_user_level)
        self.logging.info('target_level = %s' % target_level)
        if self.application_user_level < target_level:
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