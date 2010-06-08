from django import template, VERSION

# see http://docs.djangoproject.com/en/dev/howto/custom-template-tags/

# if django version is less then 1.2.x then we define a csrf_token
if VERSION[0] == 1 and VERSION[1] < 2:
    register = template.Library()

    class GoCsrfTokenNode(template.Node):
        def render(self, context):
            return ''

    def do_csrf_token(parser, token):
        return GoCsrfTokenNode()

    register.tag('csrf_token', do_csrf_token)
