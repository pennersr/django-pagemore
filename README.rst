===============
django-pagemore
===============

KISS approach to a "Load more" style AJAX paginator

Features
========

- Non-intrusive: your Django view is completely unaware of dynamic
  load-more stuff going on.
- There is literally no code (no Python, no Javascript) required to
  get a fully AJAX style "load more" going.
- KISS


Quickstart
==========

- Write your view as usual, handing over an (unpaginated) list of
  items to a template.
- Render the list of items in your template as follows::

    {% load pagemore %}
    {% more_paginator items per_page=10 ordered_by="-created_at" as paginator %}
    
    {% for item in paginator.objects %}
    {% if forloop.first %}
    <div class="pagemore-container">
    {% endif %}
    {{item}}
    {% if forloop.last %}
    </div>
    {% if paginator.has_more %}
    <a class="pagemore-paginator" href="?{{paginator.next_query}}">More items...</a>
    {% endif %}
    {% endif %}
    {% endfor %}

    <script type="text/javascript" src="{{STATIC_URL}}pagemore/js/pagemore.js"></script>

- That's all!

Q&A
===

**Q:** Why does the template tag order the items itself, slicing them
using on `__gt` like operators? Why not use offset based slicing of an
already ordered queryset?

**A:** If a user is paginating through a list of items, while at the
same time new items are inserted, offset based slicing would result in
duplicate items being shown.




