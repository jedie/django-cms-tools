# coding: utf-8

"""
    permission helpers
    ~~~~~~~~~~~~~~~~~~

    create 06.Sep.2017 by Jens Diemer
"""


from __future__ import unicode_literals, absolute_import, print_function

import logging

from django_tools.permissions import ModelPermissionMixin as ModelPermissionBaseMixin


log = logging.getLogger(__name__)


class EditModeAndChangePermissionMixin:
    """
    Helper for easy model permission checks.

    Note, needs 'has_change_permission' from:
        django_tools.permissions.ModelPermissionMixin.has_change_permission

    e.g.:
        from django_tools.permissions import ModelPermissionMixin
        from django_cms_tools.permissions import EditModeAndChangePermissionMixin

        class FooModel(ModelPermissionMixin, EditModeAndChangePermissionMixin, models.Model):
            ...

        def view(request):
            if FooModel.edit_mode_and_change_permission(request):
                ...
    """
    @classmethod
    def edit_mode_and_change_permission(cls, request):
        edit_mode = hasattr(request, 'toolbar') and request.toolbar.edit_mode
        # edit_mode = request.user.is_staff and request.session.get('cms_edit', False)

        if not edit_mode:
            # log.debug("Not in edit mode.")
            return False

        user = request.user
        if not cls.has_change_permission(user, raise_exception=False):
            # log.debug("User has no change permissions.")
            return False

        return True


class ModelPermissionMixin(ModelPermissionBaseMixin, EditModeAndChangePermissionMixin):
    """
    Helper for easy model permission checks.

    Combinded with needed
        django_tools.permissions.ModelPermissionMixin

    e.g.:
        from django_cms_tools.permissions import ModelPermissionMixin

        class FooModel(ModelPermissionMixin, models.Model):
            ...

        def view(request):
            if FooModel.edit_mode_and_change_permission(request):
                ...
    """
    pass

