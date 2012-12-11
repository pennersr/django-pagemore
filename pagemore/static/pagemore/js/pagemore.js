(function($){
    $(function() {
	var container = $(".pagemore-container");
	var paginator = $(".pagemore-paginator");
	paginator.click(function() {
	    paginator.hide();
	    $.get($(this).attr('href'),
		  function(resp) {
		      $(resp).find(".pagemore-container").children().appendTo(container);
		      var newPaginator = $(resp).find(".pagemore-paginator");
		      if (newPaginator.length) {
			  paginator.attr('href',
					 newPaginator.attr('href'));
			  paginator.show();
		      }
                      container.trigger("pagemore.loaded");
		  }
		  );
	    return false;
	});
    });
})(jQuery);
