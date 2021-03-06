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


class Role(Controller):
    class Scaffold:
        display_in_form = ('title', 'name', 'level')
        display_in_list = ['title', 'name', 'level']
        hidden_in_form = ['prohibited_actions']
        actions_in_list = [{
            'name': 'permissions',
            'title': u'權限',
            'uri': 'admin:application_user:role:action_permissions',
            'button': u'權限'
        }]

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
            msg = u'權限已啟用'
        else:
            if uri not in role_prohibited_actions_list:
                role_prohibited_actions_list.append(uri)
            msg = u'權限已停用'
        role.prohibited_actions = ','.join(role_prohibited_actions_list)
        role.put()
        self.context['data'] = {
            'result': 'success',
            'message': msg
        }

    @route
    def admin_action_permissions(self, source):
        def get_plugin_helper(application_or_plugin_name):
            sp_name = application_or_plugin_name.split('.')
            type_name = sp_name[0]
            application_or_plugin_name = '.'.join(sp_name)
            helper = self.plugins.get_helper(application_or_plugin_name, type_name)
            if helper is None:
                return None
            if 'controllers' not in helper:
                return None
            controllers, item_plugins_check = process_controller(helper)
            return {
                'name': helper['title'],
                'controllers': controllers,
                'plugins_check': item_plugins_check,
                'desc': helper['desc']
            }

        def process_controller(helper):
            action_list_in_controller = []
            enable_or_disable_plugin_check = None
            try:
                for ra_item in helper['controllers']:
                    item_n = process_actions(item, ra_item, helper['controllers'][ra_item], role_prohibited_actions)
                    if 'plugins_check' in item_n:
                        enable_or_disable_plugin_check = item_n['plugins_check']
                    action_list_in_controller.append(item_n)
            except:
                pass
            return action_list_in_controller, enable_or_disable_plugin_check

        def process_actions(plugin, controller, item, action):
            for act in item['actions']:
                uri = 'admin:%s:%s' % (controller, act['action'])
                act['uri'] = '%s.controllers.%s.%s' % (plugin, controller, act['action'])
                act['checkbox_id'] = 'plugins-%s-controllers-%s-%s' % (plugin, controller, act['action'])
                if act['uri'] in action:
                    act['enable'] = False
                else:
                    act['enable'] = True
                item[act['action']] = act
            return item

        role = self.params.get_ndb_record(source)
        self.context['application_user_level'] = self.application_user.get_role_level()
        if self.context['application_user_level'] < role.level:
            return self.abort(403)
        model_list = []
        role_prohibited_actions = role.prohibited_actions
        plugins_list = self.host_information.plugins_list
        for item in plugins_list:
            if item != 'plugins.plugin_manager':
                app_information = get_plugin_helper(item)
                if app_information is not None:
                    model_list.append(app_information)

        self.context['item'] = role
        self.context['item_key'] = source
        self.context['role'] = model_list

    @route_menu(list_name=u'backend', group=u'帳號管理', text=u'角色管理', sort=9802, icon='users')
    def admin_list(self):
        self.context['application_user_level'] = self.application_user.get_role_level()
        return scaffold.list(self)

    @csrf_protect
    def admin_add(self):
        def scaffold_before_validate(**kwargs):
            parser = kwargs['parser']
            change_level = self.params.get_integer('level')
            def validate():
                if self.application_user_level < change_level:
                    parser.errors['level'] = u"您的權限等級 (%s) 低於設定值 (%s)，您無法設置比您高等級的值" % (self.application_user_level, change_level)
                    return False
                return parser.container.validate() if parser.container else False
            parser.validate = validate

        self.application_user_level = self.application_user.get_role_level()
        self.events.scaffold_before_validate += scaffold_before_validate
        return scaffold.add(self)

    @csrf_protect
    def admin_edit(self, key, *args):
        def scaffold_before_validate(**kwargs):
            parser = kwargs['parser']
            change_level = self.params.get_integer('level')
            def validate():
                if self.application_user_level < target_level:
                    parser.errors['level'] = u"您的權限等級 (%s) 低於目標值 (%s)，您無法設置比您高等級的角色" % (self.application_user_level, target_level)
                    return False
                if self.application_user_level < change_level:
                    parser.errors['level'] = u"您的權限等級 (%s) 低於設定值 (%s)，您無法設置比您高等級的值" % (self.application_user_level, change_level)
                    return False
                if change_level > 1000 < self.application_user_level and target_level != 9999:
                    parser.errors['level'] = u'權限等級最高為 999'
                    return False
                if target_level == 9999 and change_level != 9999:
                    parser.errors['level'] = u'此權限等級無法變更'
                    return False
                return parser.container.validate() if parser.container else False
            parser.validate = validate

        target = self.params.get_ndb_record(key)
        target_level = target.level
        self.application_user_level = self.application_user.get_role_level()
        if self.application_user_level < target_level:
            return self.abort(403)
        self.events.scaffold_before_validate += scaffold_before_validate
        self.context['application_user_level'] = self.application_user_level
        return scaffold.edit(self, key)

    def admin_view(self, key):
        self.application_user_level = self.application_user.get_role_level()
        self.context['application_user_level'] = self.application_user_level
        return scaffold.view(self, key)

    def admin_delete(self, key):
        target = self.params.get_ndb_record(key)
        self.application_user_level = self.application_user.get_role_level()
        target_level = target.level
        if self.application_user_level< target_level:
            return self.abort(403)
        return scaffold.delete(self, key)
