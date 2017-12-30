#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/5/3.

from argeweb import BasicConfigModel
from argeweb import Fields


class ConfigModel(BasicConfigModel):
    first_login_roles = Fields.StringProperty(verbose_name=u'首次登入後的角色', default=u'user')
