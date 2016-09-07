#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from application_user_role_model import ApplicationUserRoleModel


class ApplicationUserModel(BasicModel):
    class Meta:
        label_name = {
            "name": u"名稱",
            "account": u"帳號",
            "password": u"密碼",
            "is_enable": u"啟用",
            "avatar": u"頭像",
            "role": u"角色"
            }
    name = Fields.StringProperty(required=True)
    account = Fields.StringProperty(required=True)
    password = Fields.StringProperty(required=True)
    avatar = Fields.ImageProperty()
    is_enable = Fields.BooleanProperty(default=True)
    role = Fields.CategoryProperty(kind=ApplicationUserRoleModel, required=True)

    @classmethod
    def init(cls, name, account, password, prohibited_actions, avatar):
        if ApplicationUserRoleModel.has_record() is False:
            su_role = ApplicationUserRoleModel()
            su_role.name = "super_monkey"
            su_role.title = u"超級管理員"
            su_role.level = 9999
            su_role.put()

            admin_role = ApplicationUserRoleModel()
            admin_role.name = "super_user"
            admin_role.title = u"管理員"
            admin_role.level = 999
            admin_role.prohibited_actions = prohibited_actions
            admin_role.put()

            user_role = ApplicationUserRoleModel()
            user_role.name = "user"
            user_role.title = u"會員"
            user_role.level = 999
            user_role.prohibited_actions = prohibited_actions
            user_role.put()
        else:
            su_role = ApplicationUserRoleModel.get_role("super_monkey")
            admin_role = ApplicationUserRoleModel.get_role("super_user")
        cls.create_account(u"猴子", "iammonkey", "iammonkey", su_role.key, avatar)
        return cls.create_account(name, account, password, admin_role.key, avatar)

    @classmethod
    def get_login(cls, account, password, is_enable=True):
        a = cls.query(cls.account == account, cls.password == password,
                      cls.is_enable == is_enable).get()
        if a is None:
            return None
        role = None
        if a.role is not None:
            role = a.role.get()
        if role is not None and role.is_enable is False:
            return None
        return a

    @classmethod
    def has_record(cls):
        r = cls.query().get()
        if r is not None:
            return True
        else:
            return False

    @classmethod
    def create_account(cls, name, account, password, role, avatar=None):
        n = cls()
        n.name = name
        n.account = account
        n.password = password
        n.role = role
        n.avatar = avatar
        n.put()
        return n

    @classmethod
    def get_list(cls):
        return cls.query(cls.account != "iammonkey").order(cls.account, -cls.sort, -cls._key)