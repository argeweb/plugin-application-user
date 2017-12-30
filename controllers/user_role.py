#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.


from argeweb import Controller, scaffold, route_menu, route
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search


class UserRole(Controller):
    class Scaffold:
        display_in_form = ['user', 'role']
        display_in_list = ['user', 'user_account', 'role']

    @route_menu(list_name=u'super_user', group=u'帳號管理', text=u'帳號角色管理', sort=9803, icon='account_box')
    def admin_list(self):
        from ..models.role_model import RoleModel
        self.context['su_key'] = RoleModel.get_role('super_user').key
        self.context['has_role'] = self.application_user.has_role('super_user')
        return scaffold.list(self)
