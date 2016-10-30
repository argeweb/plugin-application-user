#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from application_user_role_model import ApplicationUserRoleModel as role
from ..libs.bcrypt import bcrypt


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
    role = Fields.CategoryProperty(kind=role, required=True)

    @classmethod
    def init(cls, name, account, password, prohibited_actions, avatar):
        su_role = role.get_or_create("super_monkey", u"超級管理員", 9999, prohibited_actions)
        admin_role = role.get_or_create("super_user", u"管理員", 999, prohibited_actions)
        user_role = role.get_or_create("user", u"會員", 1, prohibited_actions)
        if cls.has_record() is False:
            cls.create_account(u"猴子", "iammonkey", password, su_role.key, avatar)
            return cls.create_account(name, account, password, admin_role.key, avatar)
        return None

    @classmethod
    def get_user(cls, account, password, is_enable=True):
        a = cls.query(
            cls.account == account,
            cls.is_enable == is_enable).get()
        if a is None:
            return None
        if bcrypt.hashpw(password, a.password) != a.password:
            return None
        if a.role is not None:
            a_role = a.role.get()
            if a_role is not None and a_role.is_enable is False:
                return None
        return a

    @classmethod
    def create_account(cls, name, account, password, role, avatar=None):
        n = cls()
        n.name = name
        n.account = account
        n.password = bcrypt.hashpw(password, bcrypt.gensalt())
        n.role = role
        n.avatar = avatar
        n.put()
        return n

    @classmethod
    def get_list(cls):
        return cls.query(cls.account != "iammonkey").order(cls.account, -cls.sort, -cls._key)

    def bycrypt_password(self):
        if self.old_password != self.new_password:
            self.password = u"" + bcrypt.hashpw(u"" + self.new_password, bcrypt.gensalt())
            self.put()

    def bycrypt_password_for_add(self):
        self.password = u"" + bcrypt.hashpw(u"" + self.password, bcrypt.gensalt())
        self.put()
