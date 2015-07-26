(function($) {
    $.fn.pagemore = function(options) {
        var settings = $.extend( {
            containerClass: 'pagemore-container',
            paginatorClass: 'pagemore-paginator',
            pageRequested: function(e) {
                e.paginator.hide();
            },
            pageCompleted: function(e) {
                e.paginator.toggle(! e.lastPage);
            }
        }, options);
        return this.each(function() {
            var container = $("." + settings.containerClass);
            var paginator = $(this);
            paginator.click(function() {
                var event = { paginator: paginator };
                settings.pageRequested(event);
                $.get($(this).attr('href'),
                  function(resp) {
                      $(resp).find("." + settings.containerClass).children().appendTo(container);
                      var newPaginator = $(resp).find("." + settings.paginatorClass);
                      var lastPage = ! newPaginator.length;
                      var completedEvent = $.extend({}, event, {
                          lastPage: lastPage });
                      if (! lastPage) {
                        paginator.attr('href',
                         newPaginator.attr('href'));
                    }
                    settings.pageCompleted(completedEvent);
                }
                );
                return false;
            });

        });
    };
})(jQuery);
