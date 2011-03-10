from django import template
from django.template.loader_tags import BaseIncludeNode
from django.template import Template
from django.conf import settings

from pages.plugins import html_to_template_text
from pages.plugins import LinkNode


register = template.Library()


class PageContentNode(BaseIncludeNode):
    def __init__(self, html_var, *args, **kwargs):
        super(PageContentNode, self).__init__(*args, **kwargs)
        self.html_var = template.Variable(html_var)

    def render(self, context):
        try:
            html = str(self.html_var.resolve(context))
            t = Template(html_to_template_text(html))
            return self.render_template(t, context)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''


@register.tag(name='render_page')
def do_render_page(parser, token):
    try:
        tag, html_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, ("%r tag requires one argument" %
                                             token.contents.split()[0])
    return PageContentNode(html_var)


def is_quoted(text):
    return text[0] == text[-1] and text[0] in ('"', "'")


@register.tag(name='link')
def do_link(parser, token):
    try:
        tag, href = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires one argument" %
                                           token.contents.split()[0])
    if not is_quoted(href):
        raise template.TemplateSyntaxError(
                                    "%r tag's argument should be in quotes" %
                                     token.contents.split()[0])

    nodelist = parser.parse(('endlink',))
    parser.delete_first_token()
    return LinkNode(href[1:-1], nodelist)
