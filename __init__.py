#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from plugins.application_user.models.application_user_model import ApplicationUserModel


login = ApplicationUserModel.get_login
has_record = ApplicationUserModel.has_record
create_account = ApplicationUserModel.create_account
application_user_init = ApplicationUserModel.init

__all__ = (
    'login',
    'has_record'
    'create_account'
    'application_user_init'
)

application_user_action_helper = {
    "group": u"後台帳號管理",
    "actions": [
        {"action": "list", "name": u"帳號管理"},
        {"action": "add", "name": u"新增帳號"},
        {"action": "edit", "name": u"編輯帳號"},
        {"action": "view", "name": u"檢視帳號"},
        {"action": "delete", "name": u"刪除帳號"},
    ],
    "related_action": "application_user_role"
}

application_user_role_action_helper = {
    "group": u"後台角色管理",
    "actions": [
        {"action": "list", "name": u"角色管理"},
        {"action": "add", "name": u"新增角色"},
        {"action": "edit", "name": u"編輯角色"},
        {"action": "view", "name": u"檢視角色"},
        {"action": "delete", "name": u"刪除角色"},
        {"action": "action_permissions", "name": u"權限設定"}
    ]
}
