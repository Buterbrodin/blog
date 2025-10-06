from django import template
from django.core.paginator import Paginator

register = template.Library()


@register.inclusion_tag('post/comments.html', takes_context=True)
def show_comments(context, comments):
    paginator = Paginator(comments, 5)
    request = context['request']
    page = request.GET.get('c', 1)
    comments = paginator.get_page(page)
    return {'comments': comments, 'request': request}
