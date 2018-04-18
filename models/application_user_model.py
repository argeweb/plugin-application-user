#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from google.appengine.api.datastore_errors import BadValueError

from argeweb import BasicModel
from argeweb import Fields
from argeweb.core.model import ApplicationUserModel as UserModel
from role_model import RoleModel as RoleModel
from argeweb.core.forms.wtforms.validators import InputRequired
# bcrypt use argeweb.libs.bcrypt.zip
from bcrypt import bcrypt


class ApplicationUserModel(UserModel):
    name = Fields.StringProperty(required=True, verbose_name=u'名稱')
    account = Fields.StringProperty(required=True, verbose_name=u'帳號')
    password = Fields.StringProperty(required=True, verbose_name=u'密碼')
    email = Fields.StringProperty(verbose_name=u'E-Mail', default=u'')
    is_email_verified = Fields.BooleanProperty(verbose_name=u'信箱是否已驗証', default=False)
    avatar = Fields.ImageProperty(verbose_name=u'頭像')
    is_enable = Fields.BooleanProperty(verbose_name=u'啟用', default=True)
    rest_password_token = Fields.StringProperty(verbose_name=u'重設密碼令牌', default=u'')
    need_check_old_password = Fields.BooleanProperty(verbose_name=u'可設定新密碼', default=True)
    role = Fields.HiddenProperty(verbose_name=u'角色', default=u'user')
    provider = Fields.HiddenProperty(verbose_name=u'provider', default=u'website')
    federated_id = Fields.HiddenProperty(verbose_name=u'federated id', default=u'')

    @property
    def title(self):
        return self.account

    @classmethod
    def get_user(cls, account, password, is_enable=True):
        a = cls.query(
            cls.account == account,
            cls.is_enable == is_enable).get()
        if a is None:
            return None
        if bcrypt.hashpw(password, a.password) != a.password:
            return None
        return a

    @classmethod
    def get_user_by_account(cls, account, check_is_enable=False):
        if check_is_enable:
            return cls.query(cls.account == account, cls.is_enable==True).get()
        return cls.query(cls.account == account).get()

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
        return a

    def check_password(self, check):
        if bcrypt.hashpw(check, self.password) != self.password:
            return False
        return True

    @classmethod
    def create_account(cls, name, account, password, avatar=None, email=None):
        n = cls()
        n.name = name
        n.account = account
        n.password = bcrypt.hashpw(password, bcrypt.gensalt())
        n.avatar = avatar
        if email:
            n.email = email
        n.put()
        return n

    @classmethod
    def create_account_by_email(cls, email, password, role=None, avatar=None, account=None, user_name=None):
        if account is None:
            account = str(email).split('@')[0]
        if role is None:
            role = RoleModel.find_lowest_level()
        if user_name is None:
            user_name = account
        user = cls.create_account(user_name, account, password, '/plugins/backend_ui_material/static/images/users/avatar-001.jpg', email)
        from ..models.user_role_model import UserRoleModel
        UserRoleModel.set_role(user, role)
        return user

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

    def before_put(self):
        n = []
        try:
            for r in self.roles:
                n.append(r.role_name)
            self.role = ','.join(n)
        except (BadValueError, AttributeError):
            self.role = ''

    @property
    def roles(self):
        if not hasattr(self, '_roles'):
            from user_role_model import UserRoleModel
            self._roles = UserRoleModel.get_user_roles(self).fetch()
        return self._roles

    def get_role_level(self, highest=True):
        if not hasattr(self, '_level'):
            level = 0
            for r in self.roles:
                r_level = r.role.get().level
                if r_level > level:
                    level = r_level
            setattr(self, '_level', level)
        else:
            level = getattr(self, '_level')
        return level

    def has_role(self, role):
        from user_role_model import UserRoleModel
        return UserRoleModel.has_role(self, role)

    def set_role(self, role):
        from user_role_model import UserRoleModel
        return UserRoleModel.set_role(self, role)

    def remove_role(self, role):
        from user_role_model import UserRoleModel
        return UserRoleModel.remove_role(self, role)

    def check_and_get_role(self, role):
        from user_role_model import UserRoleModel
        role = UserRoleModel.get_role(role)
        if len(self.roles) > 0:
            for item in self.roles:
                if item.key == role.key:
                    return role
            return None
        else:
            if UserRoleModel.has_role(self, role):
                return role
            return None

    def has_permission(self, action_full_name, strict=False):
        if len(self.roles) == 0:
            return False
        not_in_count = 0
        if not hasattr(self, '_roles_object'):
            self._roles_object = []
            for item in self.roles:
                r = item.role.get()
                if r:
                    self._roles_object.append(r)
        for item in self._roles_object:
            if action_full_name not in item.prohibited_actions:
                not_in_count += 1
                if strict is False:
                    break
        if strict:
            return (not_in_count > 0) and (len(self.roles) == not_in_count)
        return not_in_count > 0

    def gen_password_token(self):
        from argeweb.core.random_util import gen_random_code
        self.rest_password_token = gen_random_code()

    @classmethod
    def after_delete(cls, key):
        from user_role_model import UserRoleModel
        from google.appengine.ext import ndb
        keys = []
        for i in UserRoleModel.query(UserRoleModel.user == key).fetch():
            keys.append(i.key)
        ndb.delete_multi(keys)

    @classmethod
    def all_count(cls, *args, **kwargs):
        """ 回傳目前的總使用者人數
        :return: 人數
        """
        return cls.query().count(keys_only=True)

    @classmethod
    def all_count_with_date(cls, date=None, *args, **kwargs):
        """ 回傳特定日期加入的使用者人數
        :return: 人數
        """
        from datetime import timedelta
        if date is None:
            from datetime import datetime
            date = datetime.today()
        date_start = date + timedelta(days=-1)
        date_end = date + timedelta(days=+1)
        return cls.query(cls.created > date_start, cls.created < date_end).count(keys_only=True)
