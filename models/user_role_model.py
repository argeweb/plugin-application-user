#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from google.appengine.ext import ndb

from argeweb import BasicModel
from argeweb import Fields
from application_user_model import ApplicationUserModel
from role_model import RoleModel


class UserRoleModel(BasicModel):
    name = Fields.HiddenProperty(verbose_name=u'識別名稱')
    user = Fields.KeyProperty(verbose_name=u'使用者', kind=ApplicationUserModel)
    user_name = Fields.SearchingHelperProperty(verbose_name=u'使用者名稱', target='user', target_field_name='name')
    user_account = Fields.SearchingHelperProperty(verbose_name=u'使用者帳號', target='user', target_field_name='account')
    role = Fields.KeyProperty(verbose_name=u'角色', kind=RoleModel)
    role_name = Fields.SearchingHelperProperty(verbose_name=u'角色識別名稱', target='role', target_field_name='name')
    role_title = Fields.SearchingHelperProperty(verbose_name=u'角色名稱', target='role', target_field_name='title')

    @classmethod
    def init(cls, name, account, password, prohibited_actions, avatar):
        su_role = RoleModel.get_or_create('super_user', u'超級管理員', 9999, prohibited_actions)
        admin_role = RoleModel.get_or_create('administrator', u'管理員', 999, prohibited_actions)
        user_role = RoleModel.get_or_create('user', u'會員', 1, prohibited_actions)
        if ApplicationUserModel.has_record():
            su = ApplicationUserModel.find_by_name(u'super_user')
            admin = ApplicationUserModel.find_by_name(name)
        else:
            su = ApplicationUserModel.create_account(u'super_user', 'super_user', password, avatar)
            admin = ApplicationUserModel.create_account(name, account, password, avatar)
        if su:
            cls.set_role(su, su_role)
        if admin:
            cls.set_role(admin, admin_role)

    @classmethod
    def get_user_roles(cls, user):
        return cls.query(cls.user == user.key)

    @classmethod
    def get_role(cls, role):
        if isinstance(role, basestring):
            role = RoleModel.find_by_name(role)
        return role

    @classmethod
    def set_role(cls, user, role):
        role = cls.get_role(role)
        if role is None:
            return None
        n = cls.query(cls.user == user.key, cls.role == role.key).get()
        if n is None:
            n = cls()
            n.user = user.key
            n.role = role.key
            n.put()
        return n

    @classmethod
    def remove_role(cls, user, role):
        role = cls.get_role(role)
        if role is None:
            return None
        n = cls.query(cls.user == user.key, cls.role == role.key).get()
        if n is None:
            ndb.delete_multi(n.key)
        return n

    @classmethod
    def has_role(cls, user, role):
        role = cls.get_role(role)
        if role is None:
            return False
        n = cls.query(cls.user == user.key, cls.role == role.key).get()
        if n:
            return True
        return False

