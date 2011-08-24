from django.contrib import admin
from django import template
from django.utils.functional import update_wrapper
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.core.management import load_command_class
from django.http import Http404
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from django.utils.html import escape
from django.utils.translation import ugettext as _

from models import *

class GroupAdmin(admin.ModelAdmin):
    list_display = ["acronym", "name", "type", "role_list"]
    list_display_links = ["acronym", "name"]
    list_filter = ["type"]
    search_fields = ["name"]
    ordering = ["name"]
    raw_id_fields = ["charter", "parent", "ad"]

    def role_list(self, obj):
        roles = Role.objects.filter(group=obj).order_by("name", "email__person__name").select_related('email')
        res = []
        for r in roles:
            res.append(u'<a href="../../person/person/%s/">%s</a> (<a href="../../group/role/%s/">%s)' % (r.email.person.pk, escape(r.email.person.name), r.pk, r.name.name))
        return ", ".join(res)
    role_list.short_description = "Persons"
    role_list.allow_tags = True
    

    # SDO reminder
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urls = patterns('',
            url(r'^reminder/$',
                wrap(self.send_reminder),
                name='%s_%s_reminder' % info),
            url(r'^(.+)/reminder/$',
                wrap(self.send_one_reminder),
                name='%s_%s_one_reminder' % info),
            )
        urls += super(GroupAdmin, self).get_urls()
        return urls

    def send_reminder(self, request, sdo=None):
        opts = self.model._meta
        app_label = opts.app_label

        output = None
        sdo_pk = sdo and sdo.pk or None
        if request.method == 'POST' and request.POST.get('send', False):
            command = load_command_class('ietf.liaisons', 'remind_update_sdo_list')
            output=command.handle(return_output=True, sdo_pk=sdo_pk)
            output='\n'.join(output)

        context = {
            'opts': opts,
            'has_change_permission': self.has_change_permission(request),
            'app_label': app_label,
            'output': output,
            'sdo': sdo,
            }
        return render_to_response('admin/group/group/send_sdo_reminder.html',
                                  context,
                                  context_instance = template.RequestContext(request, current_app=self.admin_site.name),
                                 )

    def send_one_reminder(self, request, object_id):
        model = self.model
        opts = model._meta

        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
        except model.DoesNotExist:
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        return self.send_reminder(request, sdo=obj)
    

admin.site.register(Group, GroupAdmin)
admin.site.register(GroupHistory)

class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "group"]
    list_display_links = ["name"]
    search_fields = ["name", "email"]
    list_filter = ["name"]
    ordering = ["id"]
    raw_id_fields = ["email", "group"]

admin.site.register(Role, RoleAdmin)
