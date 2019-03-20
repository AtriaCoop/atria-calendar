from django import template
from django.template.base import TemplateSyntaxError, kwarg_re
from django.template.defaulttags import URLNode

register = template.Library()


class SNURLNode(URLNode):
    def render(self, context):
        request = context.get('request')

        if request:
            url_namespace = request.session.get('URL_NAMESPACE')

            if url_namespace:
                self.view_name.var = url_namespace + self.view_name.var

        return super().render(context)


# Mostly copied from django.template.defaulttags.url
@register.tag
def snurl(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "'%s' takes at least one argument, a URL pattern name." % bits[0])
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return SNURLNode(viewname, args, kwargs, asvar)
