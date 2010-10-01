from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib.admin.options import InlineModelAdmin

from easy_thumbnails.files import get_thumbnailer


# Admin classes ------------------------------------------------------------

class ImagePreviewInline(InlineModelAdmin):
    def __init__(self, *args, **kwargs):
        # enforce use of fieldsets so we can inject the preview field
        if not self.fieldsets:
            self.__class__.fieldsets = (
                (None, {'fields': self.form.base_fields}),)
        super(ImagePreviewInline, self).__init__(*args, **kwargs)
        # inject 'preview' after super init since it won't validate
        self.declared_fieldsets[0][1]['fields'] = ('preview',) + \
            tuple(self.declared_fieldsets[0][1]['fields'])    

class ImagePreviewStackedInline(ImagePreviewInline):
    template = 'admin/edit_inline/stacked.html'

class ImagePreviewTabularInline(ImagePreviewInline):
    template = 'admin/edit_inline/tabular.html'

# Form classes ------------------------------------------------------------
    
class ImagePreviewWidget(forms.widgets.Input):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.form = kwargs.pop('form', None)
        super(ImagePreviewWidget, self).__init__(*args, **kwargs)
        
    def render(self, name, data, attrs={}):
        if self.instance:
            image = self.form.get_image(self.instance)
            options = dict(size=(120, 120), crop=False)
            thumbnail = get_thumbnailer(image.file).get_thumbnail(options)
            image_url = image.file.url
            return mark_safe('<a href="%(image_url)s" target="_blank"><img src="%(thumbnail_url)s" class="feincmstools-thumbnail"/></a>' % {'image_url': image_url, 'thumbnail_url': thumbnail.url})
        else:
            return ''

class ImagePreviewField(forms.Field):
    """ Dummy "field" to provide preview thumbnail. """
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.form = kwargs.pop('form', None)
        kwargs['widget'] = ImagePreviewWidget(instance=self.instance, form=self.form)
        super(ImagePreviewField, self).__init__(*args, **kwargs)

class ImagePreviewInlineForm(forms.ModelForm):
    """ Add image preview. """
    def __init__(self, *args, **kwargs):
        super(ImagePreviewInlineForm, self).__init__(*args, **kwargs)
        preview_field = ImagePreviewField(
            label=_('Preview'), required=False,
            instance=kwargs.get('instance', None), form=self)
        self.fields.insert(0, 'preview', preview_field)
        self.base_fields.insert(0, 'preview', preview_field)
        
    def get_image(self, instance):
        ''' This needs to be specified by the child form class, as we cannot anticipate the name of the image model field '''
        raise NotImplementedError
