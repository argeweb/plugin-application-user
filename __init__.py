#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from .models.application_user_model import ApplicationUserModel


get_user = ApplicationUserModel.get_user
has_record = ApplicationUserModel.has_record
create_account = ApplicationUserModel.create_account
application_user_init = ApplicationUserModel.init

__all__ = (
    'get_user',
    'has_record'
    'create_account'
    'application_user_init'
)

plugins_helper = {
    "title": u"使用者",
    "desc": u"網站使用者",
    "controllers": {
        "application_user": {
            "group": u"使用者",
            "actions": [
                {"action": "list", "name": u"帳號管理"},
                {"action": "add", "name": u"新增帳號"},
                {"action": "edit", "name": u"編輯帳號"},
                {"action": "view", "name": u"檢視帳號"},
                {"action": "delete", "name": u"刪除帳號"},
            ]
        },
        "application_user_role": {
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
    }
}
