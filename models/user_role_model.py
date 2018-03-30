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
from argeweb.core.events import on
from role_model import RoleModel


@on('application_user_init')
def application_user_init(
        controller,
        user_name=u'管理員',
        user_account='admin',
        user_password='qwER12#$',
        user_prohibited_actions='plugins.backend_ui_material.controllers.backend_ui_material.super_user_menu',
        user_image='/plugins/backend_ui_material/static/images/users/avatar-001.jpg', *args, **kwargs):
    su_role = RoleModel.get_or_create_by_name('super_user', title=u'超級管理員', level=9999, prohibited_actions='')
    admin_role = RoleModel.get_or_create_by_name('administrator', title=u'管理員', level=999, prohibited_actions=user_prohibited_actions)
    user_role = RoleModel.get_or_create_by_name('user', title=u'會員', level=1, prohibited_actions=user_prohibited_actions)
    if ApplicationUserModel.has_record():
        su = ApplicationUserModel.get_by_name(u'super_user')
        admin = ApplicationUserModel.get_by_name(user_name)
    else:
        su = ApplicationUserModel.create_account(u'super_user', 'super_user', user_password, user_image)
        admin = ApplicationUserModel.create_account(user_name, user_account, user_password, user_image)
    if su:
        UserRoleModel.set_role(su, su_role)
    if admin:
        UserRoleModel.set_role(admin, admin_role)


class UserRoleModel(BasicModel):
    user = Fields.ApplicationUserProperty(verbose_name=u'使用者')
    role = Fields.KeyProperty(verbose_name=u'角色', kind=RoleModel)

    @classmethod
    def get_user_roles(cls, user):
        return cls.query(cls.user == user.key)

    @classmethod
    def get_role(cls, role):
        if isinstance(role, basestring):
            role = RoleModel.get_by_name(role)
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
            return False
        n = cls.query(cls.user == user.key, cls.role == role.key).get(keys_only=True)
        if n is not None:
            ndb.delete_multi([n])
        return True

    @classmethod
    def has_role(cls, user, role):
        role = cls.get_role(role)
        if role is None:
            return False
        n = cls.query(cls.user == user.key, cls.role == role.key).get(keys_only=True)
        if n:
            return True
        return False

