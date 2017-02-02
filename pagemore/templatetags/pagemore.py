import calendar
from datetime import datetime

from django import template
from django.db.models.fields import DateTimeField
from django.db.models.query import QuerySet
from django.utils import timezone


register = template.Library()

class PaginationStrategy(object):
    FILTER = 'filter'
    SLICE = 'slice'


class BasePaginator(object):

    def __init__(self, request, objects, per_page, ordered_by):
        self.request = request
        self.objects = objects
        self.per_page = per_page or 10
        self.ordered_by = ordered_by

    def get_context_data(self):
        objects, next_val = self.paginate()
        has_more = next_val is not None
        get = self.request.GET.copy()
        get[self.GET_PARAM] = next_val
        return dict(objects=objects,
                    object_count=len(objects),
                    has_more=has_more,
                    next_query=get.urlencode())


class FilteringPaginator(BasePaginator):
    GET_PARAM = 'pagemore_after'

    def __init__(self, request, objects, per_page, ordered_by):
        if not isinstance(objects, QuerySet):
            raise NotImplementedError('The "filter" strategy supports only'
                                      ' querysets, use strategy="slice"')
        ordered_by = ordered_by or 'id'
        objects = objects.order_by(ordered_by)
        super(FilteringPaginator, self).__init__(request,
                                                 objects,
                                                 per_page,
                                                 ordered_by)
        if ordered_by[0] == '-':
            self.order_field = ordered_by[1:]
            self.order_op = 'lt'
        else:
            self.order_field = ordered_by
            self.order_op = 'gt'

    def paginate(self):
        after_val = self.request.GET.get(self.GET_PARAM)
        objects = self.objects
        if after_val is not None:
            field_type = self.objects.model \
            ._meta.get_field(self.order_field)
            if isinstance(field_type, DateTimeField):
                after_val = timezone.make_aware(
                    datetime.utcfromtimestamp(int(after_val)),
                    timezone.utc
                )
            order_q = self.order_field + '__' + self.order_op
            objects = objects.filter(**{order_q: after_val} )
        objects = list(objects[0:self.per_page+1]) # evaluate qs, intentionally
        next_after_val = None
        if len(objects) > self.per_page:
            next_after_val = getattr(objects[-2], self.order_field)
            if isinstance(next_after_val, datetime):
                next_after_val = int(calendar.timegm(next_after_val
                                                     .utctimetuple()))
            objects = objects[0:self.per_page]
        else:
            next_after_val = None
        return objects, next_after_val
    

class SlicingPaginator(BasePaginator):
    GET_PARAM = 'pagemore_page'

    def __init__(self, request, objects, per_page, ordered_by):
        if ordered_by:
            if not isinstance(objects, QuerySet):
                raise NotImplementedError('Ordering is only supported for'
                                          ' querysets')
            objects = objects.order_by(ordered_by)
        super(SlicingPaginator, self).__init__(request,
                                               objects,
                                               per_page,
                                               ordered_by)


    def get_page(self):
        try:
            page = int(self.request.GET.get(self.GET_PARAM, 1))
        except ValueError:
            page = 1
        return page

    def paginate(self):
        page = self.get_page()
        page0 = self.get_page() - 1
        objects = self.objects[page0*self.per_page:1+page*self.per_page]
        objects = list(objects) # evaluate qs, intentionally
        next_page = None
        if len(objects) > self.per_page:
            next_page = page + 1
            objects = objects[0:self.per_page]
        return objects, next_page


@register.assignment_tag(takes_context=True)
def more_paginator(context, objects, per_page=None, ordered_by=None,
                   strategy=PaginationStrategy.FILTER):
    request = context['request']
    # Shortcut when there is nothing to paginate
    # not just 'if objects:' -- I don't want to eval a qs
    if objects is None or objects == '' or objects == []:
        paginator = SlicingPaginator(request, [], None, None)
    else:
        paginator_klazz = { 
            PaginationStrategy.FILTER: FilteringPaginator,
            PaginationStrategy.SLICE: SlicingPaginator }[strategy]
        paginator = paginator_klazz(request, 
                                    objects, 
                                    per_page=per_page,
                                    ordered_by=ordered_by)
    return paginator.get_context_data()

