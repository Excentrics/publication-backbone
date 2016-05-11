(function($) {
	$(document).ready(function() {
		// Add anchor tag for Show/Hide link
		$("div.tabular").each(function(i, elem) {
			// Don't hide if fields in this fieldset have errors
			if ($(elem).find("div.errors").length == 0) {
				$(elem).addClass("").find("h2").first().append(' (<a id="fieldsetcollapser' +
					i +'" class="collapse-toggle" href="#">' + gettext("Hide") +
					'</a>)');
			}
		});
		// Add toggle to anchor tag
		$("div.inline-group a.collapse-toggle").toggle(
			function() { // Hide
				$(this).text(gettext("Show")).closest("fieldset").addClass("collapsed").trigger("hide.div", [$(this).attr("id")]);
				return false;
			},
			function() { // Show
				$(this).text(gettext("Hide")).closest("fieldset").removeClass("collapsed").trigger("show.div", [$(this).attr("id")]);
				return false;
			}
		);
	});
})(django.jQuery);