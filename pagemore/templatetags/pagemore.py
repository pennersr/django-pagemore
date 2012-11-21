import time
from datetime import datetime
from django import template
from django.db.models.fields import DateTimeField

register = template.Library()

@register.assignment_tag(takes_context=True)
def more_paginator(context, objects, per_page=10, ordered_by='id'):
    objects = objects.order_by(ordered_by)
    request = context['request']
    if ordered_by[0] == '-':
        field = ordered_by[1:]
        op = 'lt'
    else:
        field = ordered_by
        op = 'gt'
    get_param = 'pagemore_after'
    after_val = request.GET.get(get_param)
    if after_val is not None:
        field_type = objects.model._meta.get_field_by_name(field)[0]
        if isinstance(field_type, DateTimeField):
            after_val = datetime.fromtimestamp(int(after_val))
        objects = objects.filter(**{field + '__' + op: after_val} )
    objects = list(objects[0:per_page+1]) # evaluate qs, intentionally
    has_more = len(objects) > per_page
    objects = objects[0:per_page]
    object_count = len(objects) 
    if object_count:
        next_after_val = getattr(objects[-1], field)
        if isinstance(next_after_val, datetime):
            next_after_val = int(time.mktime(next_after_val.timetuple()))
    else:
        next_after_val = None
    get = request.GET.copy()
    get[get_param] = next_after_val
    return dict(objects=objects,
                object_count=object_count,
                has_more=has_more,
                next_query=get.urlencode(),
                next_after_val=next_after_val)

