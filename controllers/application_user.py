#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.

from argeweb import Controller, scaffold, route_menu, route_with, settings
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from .. import application_user_action_helper


class ApplicationUser(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)
        pagination_actions = ("list",)
        pagination_limit = 50

    class Scaffold:
        title = application_user_action_helper["actions"]
        display_properties = ("name", "account", "is_enable", "sort", "created", "modified")
        display_properties_in_list = ("name", "account")

    @route_with("/application_user_init")
    def application_user_init(self):
        prohibited_actions = settings.get("application_user_prohibited_actions", u"")
        from plugins.application_user import application_user_init, has_record
        application_user_init(u"管理員", "admin", "qwER12#$", prohibited_actions,
                             "/plugins/backend_ui_material/static/img/profile_small.jpg")
        return self.redirect("/")

    @route_menu(list_name=u"backend", text=u"帳號管理", sort=9700, icon="users", group=u"帳號管理")
    @route_with("/admin/application_user/list")
    def admin_list(self):
        self.context["application_user_key"] = self.application_user.key
        scaffold.list(self)
        for item in self.context[self.scaffold.plural]:
            item.level = item.role.get().level

    @csrf_protect
    def admin_add(self):
        def scaffold_before_validate(**kwargs):
            parser = kwargs["parser"]
            change_level = parser.data["role"].get().level
            def validate():
                if change_level > self.application_user_level:
                    parser.errors["role"] = u"您的權限等級低於此角色"
                    return False
                return parser.container.validate() if parser.container else False
            parser.validate = validate
        self.events.scaffold_before_validate += scaffold_before_validate
        return scaffold.add(self)

    @csrf_protect
    def admin_edit(self, key):
        target = self.util.decode_key(key).get()
        target_level = target.role.get().level
        if self.application_user_level < target_level:
            return self.abort(403)
        change_password = u""
        def scaffold_before_validate(**kwargs):
            parser = kwargs["parser"]
            change_level = parser.data["role"].get().level
            item = kwargs["item"]
            item.old_password = item.password
            item.new_password = parser.data["password"]
            def validate():
                if self.application_user_level < change_level:
                    parser.errors["role"] = u"您的權限等級低於此角色"
                    return False
                return parser.container.validate() if parser.container else False
            parser.validate = validate
        def bycrypt_password(**kwargs):
            item = kwargs["item"]
            item.bycrypt_password()
        self.events.scaffold_before_validate += scaffold_before_validate
        self.events.scaffold_after_save += bycrypt_password
        return scaffold.edit(self, key)

    @csrf_protect
    @route_with("/admin/application_user/profile")
    def admin_profile(self):
        target = self.application_user
        target_level = target.role.get().level
        if self.application_user_level < target_level:
            return self.abort(403)
        def scaffold_before_validate(**kwargs):
            parser = kwargs["parser"]
            change_level = parser.data["role"].get().level
            def validate():
                if  self.application_user_level < change_level:
                    parser.errors["role"] = u"您的權限等級低於此角色"
                    return False
                return parser.container.validate() if parser.container else False
            parser.validate = validate
        self.events.scaffold_before_validate += scaffold_before_validate
        return scaffold.edit(self, self.application_user.key)

    def admin_delete(self, key):
        target = self.util.decode_key(key).get()
        target_level = target.role.get().level
        if self.application_user_level < target_level:
            return self.abort(403)
        return scaffold.delete(self, key)
