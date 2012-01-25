from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.urlresolvers import clear_url_caches
from django.db.models.fields import FieldDoesNotExist
from django.http import HttpResponse, Http404
from django.utils.html import escape, escapejs

from adminboost import urls
from .widgets import (
    VerboseForeignKeyRawIdWidget, VerboseManyToManyRawIdWidget,
    render_edit_link, render_edit_links)

def admin_improvement_factory(parent_class):
    class ImprovedAdmin(parent_class):
        def __init__(self, *args, **kwargs):
            """
            This ensures that verbose raw ID widgets work in inlines, 
            especially in FeinCMS content types.
            
            Since the Django admin only initialises InlineModelAdmin objects
            as they're needed, we have to update the URLs used to generate the
            preview HTML that's called when the foreign object has been edited
            as we go along. Not brilliant.
            
            The other option would be to introspect all registered ModelAdmin
            objects for defined inlines, and it might be good to eventually
            switch to that approach.
            """
            super(ImprovedAdmin, self).__init__(*args, **kwargs)
            if issubclass(type(self), admin.options.InlineModelAdmin):
                if getattr(self.admin_site, '_inline_urls', None) is None:
                    # Store the URLs in an "_inline_urls" attribute of the 
                    # AdminSite object. Use a dictionary so each inline is
                    # only added once, which allows us to simply grab .values()
                    # for a list of URLs to register
                    self.admin_site._inline_urls = {}
                name = self.model._meta.object_name.lower()
                if name not in self.admin_site._inline_urls:
                    # When we're adding a previously unseen inline, recalculate
                    # the urlpatterns objects in adminboost.urls and clear
                    # Django's URL cahce
                    self.admin_site._inline_urls[name] = self.get_inline_url()
                    reload(urls)
                    clear_url_caches()
                    
        
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
            """
            Provides a URL where the "preview" section of the verbose raw ID
            widget can be requested from. This is used when the foreign model
            gets updated via the "edit" link on the main model, so that the
            preview can be updated on save.
            """
            return patterns(
                '',
                url(r'edit-links/(?P<field_name>\w+)/',
                    self.admin_site.admin_view(self.render_edit_links),
                    name='%s_%s_render_edit_links' % (
                        self.model._meta.app_label,
                        self.model._meta.object_name.lower())),
                ) + super(ImprovedAdmin, self).get_urls()
        
        def get_inline_url(self):
            """
            As above, except for inline verbose raw IDs, we only want the
            foreign model name, and there can only be one URL. This only gets
            called by the __init__ method above.
            """
            return url(
                r'^edit-links/(?P<field_name>\w+)/',
                self.admin_site.admin_view(self.render_edit_links),
                name='inline_%s_render_edit_links' % \
                    self.model._meta.object_name.lower(),
            )
    
    return ImprovedAdmin

ImprovedRawIdAdmin = admin_improvement_factory(admin.ModelAdmin)
ImprovedRawIdStackedInline = admin_improvement_factory(admin.StackedInline)

try:
    from feincms.admin.item_editor import FeinCMSInline
    ImprovedFeinCMSInline = admin_improvement_factory(FeinCMSInline)
except ImportError:
    pass
