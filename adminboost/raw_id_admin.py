from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.db.models.fields import FieldDoesNotExist
from django.http import HttpResponse, Http404
from django.utils.html import escape, escapejs
from .widgets import (
    VerboseForeignKeyRawIdWidget, VerboseManyToManyRawIdWidget,
    render_edit_link, render_edit_links)

def admin_improvement_factory(parent_class):
    class ImprovedAdmin(parent_class):
        def formfield_for_dbfield(self, db_field, **kwargs):
            if db_field.name in self.raw_id_fields:
                kwargs.pop("request", None)
                type = db_field.rel.__class__.__name__
                if type == "ManyToOneRel":
                    kwargs['widget'] = \
                        VerboseForeignKeyRawIdWidget(db_field)
                elif type == "ManyToManyRel":
                    kwargs['widget'] = \
                        VerboseManyToManyRawIdWidget(db_field)
                return db_field.formfield(**kwargs)
            return super(
                ImprovedAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        def response_change(self, request, obj):
            if '_edit_popup' in request.REQUEST:
                return HttpResponse(
                    '<script type="text/javascript">'
                    'opener.dismissEditPopup('
                    'window, "%s", "%s");</script>' % (
                        escape(obj._get_pk_val()), escapejs(obj)))
            else:
                return super(ImprovedAdmin, self).response_change(request, obj)

        def render_edit_links(self, request, field_name):
            ids = map(
                int, filter(
                    bool, map(
                        unicode.strip, request.GET.get('ids', '').split(u','))))
            try:
                db_field = self.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                raise Http404
            links = []
            for obj in db_field.rel.to._default_manager.filter(id__in=ids):
                links.append(render_edit_link(obj, db_field, request=request))
            return HttpResponse(render_edit_links(self.model, links, db_field))

        def get_urls(self):
            return patterns(
                '',
                url(r'edit-links/(?P<field_name>\w+)/',
                    self.admin_site.admin_view(self.render_edit_links),
                    name='%s_%s_render_edit_links' % (
                        self.model._meta.app_label,
                        self.model._meta.object_name.lower())),
                ) + super(ImprovedAdmin, self).get_urls()
    return ImprovedAdmin

ImprovedRawIdAdmin = admin_improvement_factory(admin.ModelAdmin)
ImprovedRawIdStackedInline = admin_improvement_factory(admin.StackedInline)
