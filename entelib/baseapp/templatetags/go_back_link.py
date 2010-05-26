from baseapp.config import Config
from django import template

# see http://docs.djangoproject.com/en/dev/howto/custom-template-tags/

register = template.Library()

class GoBackLinkNode(template.Node):
    def __init__(self, link_name):
        if not link_name:
            config = Config()
            link_name = config.get_str('default_go_back_link_name')
        self.link_name = link_name

    def render(self, context):
        t = template.loader.get_template('tags/go_back_link.html')
        ctx = {'name': self.link_name,
               'link': 'javascript:history.go(-1)',
               }
        return t.render(template.Context(ctx))

def do_go_back_link(parser, token):
    try:
        tokens = token.split_contents()    # split_contents() knows not to split quoted strings.
        if len(tokens) < 2:
            tag_name, link_name = tokens[0], None
        else:
            tag_name, link_name = tokens
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires 0 or 1 argument" % token.contents.split()[0]
    if not (link_name==None
            or (len(link_name)>1 and link_name[0]==link_name[-1] and link_name[0] in ('"', "'"))):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    if link_name==None:
        return GoBackLinkNode(None)
    else:
        return GoBackLinkNode(link_name[1:-1])
register.tag('go_back_link', do_go_back_link)
