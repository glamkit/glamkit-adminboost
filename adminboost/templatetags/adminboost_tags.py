from django.template import Library, Node, TemplateSyntaxError, loader
from django.conf import settings

register = Library()

class SortableInlineNode(Node):
    def __init__(self, includes):
        self.includes = includes

    def render(self, context):
        c = {"prefixes": ["%s_set" % model_name.lower() for model_name in self.includes], "MEDIA_URL": settings.MEDIA_URL}
        return loader.render_to_string("adminboost/sortable_inlines.html", c)


@register.tag
def sortable_inlines(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) < 1:
        raise TemplateSyntaxError("'sortable_inlines' statement requires at least one argument")
    try:
        bits = [c[1:-1] for c in bits]
    except IndexError:
        raise TemplateSyntaxError("syntax of the model names passed for the 'sortable_inline' is incorrect. Try surrounding model names with double quotes")
    return SortableInlineNode(bits)
