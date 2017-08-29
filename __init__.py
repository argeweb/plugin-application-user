#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from google.appengine.ext import ndb

from argeweb.core.events import on
from .models.user_role_model import UserRoleModel, RoleModel, ApplicationUserModel, application_user_init

get_user = ApplicationUserModel.get_user
has_record = ApplicationUserModel.has_record
create_account = ApplicationUserModel.create_account


@on('disable_role_action')
def disable_action(controller, action_uri):
    roles = RoleModel.all().fetch()
    for role in roles:
        role_prohibited_actions_list = str(role.prohibited_actions).split(',')
        if action_uri not in role_prohibited_actions_list:
            role_prohibited_actions_list.append(action_uri)
        role.prohibited_actions = ','.join(role_prohibited_actions_list)
    ndb.put_multi(roles)


@on('enable_role_action')
def enable_action(controller, action_uri):
    roles = RoleModel.all().fetch()
    for role in roles:
        role_prohibited_actions_list = str(role.prohibited_actions).split(',')
        if action_uri in role_prohibited_actions_list:
            role_prohibited_actions_list.remove(action_uri)
        role.prohibited_actions = ','.join(role_prohibited_actions_list)
    ndb.put_multi(roles)

__all__ = (
    'get_user',
    'has_record'
    'create_account'
    'application_user_init'
)

plugins_helper = {
    'title': u'使用者',
    'desc': u'網站使用者',
    'controllers': {
        'application_user': {
            'group': u'使用者',
            'actions': [
                {'action': 'list', 'name': u'帳號管理'},
                {'action': 'add', 'name': u'新增帳號'},
                {'action': 'edit', 'name': u'編輯帳號'},
                {'action': 'view', 'name': u'檢視帳號'},
                {'action': 'delete', 'name': u'刪除帳號'},
                {'action': 'profile', 'name': u'個人資料設定'},
                {'action': 'set_role', 'name': u'角色設定'},
            ]
        },
        'role': {
            'group': u'後台角色管理',
            'actions': [
                {'action': 'list', 'name': u'角色管理'},
                {'action': 'add', 'name': u'新增角色'},
                {'action': 'edit', 'name': u'編輯角色'},
                {'action': 'view', 'name': u'檢視角色'},
                {'action': 'delete', 'name': u'刪除角色'},
                {'action': 'action_permissions', 'name': u'權限設定'}
            ]
        },
        'user_role': {
            'group': u'帳號角色管理',
            'actions': [
                {'action': 'list', 'name': u'帳號角色管理'},
                {'action': 'add', 'name': u'新增帳號角色關連'},
                {'action': 'edit', 'name': u'編輯帳號角色關連'},
                {'action': 'view', 'name': u'檢視帳號角色關連'},
                {'action': 'delete', 'name': u'刪除帳號角色關連'},
            ]
        }
    }
}
