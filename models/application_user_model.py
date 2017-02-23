#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from application_user_role_model import ApplicationUserRoleModel as RoleModel
from argeweb.libs.bcrypt import bcrypt
from argeweb.libs.wtforms.validators import InputRequired


class ApplicationUserModel(BasicModel):
    name = Fields.StringProperty(required=True, verbose_name=u'名稱')
    account = Fields.StringProperty(required=True, verbose_name=u'帳號')
    password = Fields.StringProperty(required=True, verbose_name=u'密碼')
    email = Fields.StringProperty(default=u'', verbose_name=u'E-Mail')
    avatar = Fields.ImageProperty(verbose_name=u'頭像')
    is_enable = Fields.BooleanProperty(default=True, verbose_name=u'啟用')
    role = Fields.CategoryProperty(kind=RoleModel, required=True, verbose_name=u'角色')
    rest_password_token = Fields.StringProperty(verbose_name=u'重設密碼令牌', default=u'')

    @classmethod
    def init(cls, name, account, password, prohibited_actions, avatar):
        su_role = RoleModel.get_or_create('super_user', u'超級管理員', 9999, prohibited_actions)
        admin_role = RoleModel.get_or_create('administrator', u'管理員', 999, prohibited_actions)
        user_role = RoleModel.get_or_create('user', u'會員', 1, prohibited_actions)
        if cls.has_record() is False:
            cls.create_account(u'super_user', 'super_user', password, su_role, avatar)
            return cls.create_account(name, account, password, admin_role, avatar)
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
    def get_user_by_email(cls, email, check_is_enable=False):
        if check_is_enable:
            return cls.query(cls.email == email, cls.is_enable==True).get()
        return cls.query(cls.email == email).get()

    @classmethod
    def get_user_by_rest_password_token(cls, token, check_is_enable=True):
        if check_is_enable:
            return cls.query(cls.rest_password_token == token, cls.is_enable==True).get()
        return cls.query(cls.rest_password_token == token).get()

    @classmethod
    def get_user_by_email_and_password(cls, email, password, check_is_enable=True):
        a = cls.get_user_by_email(email, check_is_enable)
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
    def create_account(cls, name, account, password, role, avatar=None, email=None):
        n = cls()
        n.name = name
        n.account = account
        n.password = bcrypt.hashpw(password, bcrypt.gensalt())
        n.role = role.key
        n.avatar = avatar
        if email:
            n.email = email
        n.put()
        return n

    @classmethod
    def create_account_by_email(cls, email, password, role=None, avatar=None):
        account = str(email).split('@')[0]
        if role is None:
            role = RoleModel.find_lowest_level()
        return cls.create_account(account, account, password, role, '/plugins/backend_ui_material/static/images/users/avatar-001.jpg', email)

    @classmethod
    def get_list(cls):
        return cls.query(cls.account != 'super_user').order(cls.account, -cls.sort, -cls._key)

    def bycrypt_password_with_old_password(self):
        if self.old_password != self.new_password:
            self.password = u'' + bcrypt.hashpw(u'' + self.new_password, bcrypt.gensalt())
            self.put()

    def bycrypt_password(self):
        self.password = u'' + bcrypt.hashpw(u'' + self.password, bcrypt.gensalt())
        self.put()
