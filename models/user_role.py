#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import BasicModel
from argeweb import Fields
from application_user_model import ApplicationUserModel
from role_model import RoleModel


class UserRoleModel(BasicModel):
    name = Fields.StringProperty(required=True, verbose_name=u'識別名稱')
    user = Fields.KeyProperty(verbose_name=u'使用者', kind=ApplicationUserModel)
    user_name = Fields.SearchingHelperProperty(verbose_name=u'使用者名稱', target='user', target_field_name='name')
    user_account = Fields.SearchingHelperProperty(verbose_name=u'使用者帳號', target='user', target_field_name='account')
    role = Fields.KeyProperty(verbose_name=u'角色', kind=RoleModel)
    role_name = Fields.SearchingHelperProperty(verbose_name=u'角色識別名稱', target='role', target_field_name='name')
    role_title = Fields.SearchingHelperProperty(verbose_name=u'角色名稱', target='role', target_field_name='title')

    @classmethod
    def is_in_role(cls, user, role_name):
        role = RoleModel.find_by_name(role_name)
        if role is None:
            return False
        n = cls.query(cls.user == user.key, cls.role == role.key).get()
        if n:
            return True
        return False

    @classmethod
    def has_permission(cls, user, action_full_name, strict=False):
        items = cls.query(cls.user == user.key).fetch()
        not_in_count = 0
        for item in items:
            r = item.role.get()
            if r:
                if action_full_name not in r.prohibited_actions:
                    not_in_count += 1
                    if strict is False:
                        break
        if strict:
            return (not_in_count > 0) and (len(items) == not_in_count)
        return not_in_count > 0
