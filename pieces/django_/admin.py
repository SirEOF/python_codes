# coding=utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.db.models import ManyToOneRel
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.utils.translation import ugettext_lazy


class DeletableMixin(object):
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

    delete_selected.short_description = ugettext_lazy('Delete selected %(verbose_name_plural)s')


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """
    只读model admin
    """

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def readonly_model_admin(model_class):
    """
    构建只读model admin
    :param model_class: 
    :return: 
    """
    readonly_field_names = [f.name for f in model_class._meta.get_fields() if not isinstance(f, ForeignObjectRel)]
    attrs = {
        'readonly_fields': readonly_field_names
    }
    new_model_admin_type = type(str(model_class.__name__ + 'ModelAdmin'), (ReadOnlyModelAdmin,), attrs)
    return admin.register(model_class)(new_model_admin_type)
