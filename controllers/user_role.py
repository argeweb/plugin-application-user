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


class UserRole(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)

    class Scaffold:
        display_in_form = ('name', 'user', 'role')
        display_in_list = ('name', 'user', 'role')

    @route
    def admin_permissions_set_json(self):
        self.meta.change_view('json')
        role = self.params.get_ndb_record('role_key')
        if not role:
            return self.error(403)
        if self.application_user.get_role_level() < role.level:
            return self.error(403)
        uri = self.params.get_string('uri', '')
        enable = self.params.get_string('enable', 'enable')
        if uri is '':
            return self.error(404)
        role_prohibited_actions_list = str(role.prohibited_actions).split(',')
        if enable == u'true':
            if uri in role_prohibited_actions_list:
                role_prohibited_actions_list.remove(uri)
            msg = u'已啟用'
        else:
            if uri not in role_prohibited_actions_list:
                role_prohibited_actions_list.append(uri)
            msg = u'已停用'
        s = ','.join(role_prohibited_actions_list)
        role.prohibited_actions = s
        role.put()
        self.context['data'] = {
            'info': 'done',
            'msg': msg
        }

    @route_with('/admin/application_user_role/:<key>/permissions')
    def admin_action_permissions(self, key):
        def process_item(plugin, controller, item, action):
            for act in item['actions']:
                uri = 'admin:%s:%s' % (controller, act['action'])
                act['uri'] = 'plugins.%s.controllers.%s.%s' % (plugin, controller, act['action'])
                act['checkbox_id'] = 'plugins-%s-controllers-%s-%s' % (plugin, controller, act['action'])
                if act['uri'] in action:
                    act['enable'] = False
                else:
                    act['enable'] = True
            return item

        role = self.params.get_ndb_record(key)
        if self.application_user_level < role.level:
            return self.abort(403)
        action_list = []
        role_prohibited_actions = role.prohibited_actions
        for item in self.plugins.get_enable_plugins_from_db(self.server_name, self.namespace):
            helper = self.plugins.get_helper(item)
            if helper is None:
                continue
            if 'controllers' not in helper:
                continue
            try:
                for ra_item in helper['controllers']:
                    action_list.append(process_item(item, ra_item, helper['controllers'][ra_item], role_prohibited_actions))
            except:
                pass
        module_path = 'application'
        module = __import__('%s' % module_path, fromlist=['*'])
        for item in self.plugins.get_installed_list():
            try:
                cls = getattr(module, '%s_action_helper' % item)
                action_list.append(process_item('application', item, cls, role_prohibited_actions))
            except:
                pass

        self.context['item'] = role
        self.context['item_key'] = key
        self.context['role'] = action_list

    @route_menu(list_name=u'backend', text=u'帳號角色管理', sort=9803, icon='users', group=u'帳號管理')
    def admin_list(self):
        return scaffold.list(self)
