/*
Makes all inline forms collapsible.
*/

jQuery(function($) {
    $.makeCollapsible = function(target, item, collapsible, triggerTarget, setInitStatus, setFirstStatus)
    {
        var triggerExpand = gettext('Show');
        var triggerCollapse = gettext('Hide');
        var triggerClass = 'collapse-expand';
        var triggerLink = '<a class="' + triggerClass + '" href="javascript:void(0)"></a>';
        var triggerPrepend = ' (';
        var triggerAppend = ')';

        $(target).find(item).each(function(i) {
            if ($(this).data('isCollapsible')) return;
            $(this).data('isCollapsible', true);

            $(this).find(collapsible).hide();

            // trigger already exists if created with "Add another" link
            var trigger = $(this).find(triggerTarget).find('.'+triggerClass);
            if (!trigger.length) {
                trigger = $(triggerLink);
                $(this).find(triggerTarget).append(trigger);
                trigger.before(triggerPrepend);
                trigger.after(triggerAppend);
            }

            var item = this;
            var toggleCollapse = function(status, speed)
            {
                if (status == null) {
                    status = !item.collapseStatus;
                }
                if (speed == null) {
                    speed = 1;
                }
                item.collapseStatus = status;
                if (status) {
                    trigger.html(triggerCollapse);
                    $(item).find(collapsible).show();
                } else {
                    trigger.html(triggerExpand);
                    $(item).find(collapsible).hide();
                }
            }

            trigger.click(function(event) {
                event.preventDefault();
                toggleCollapse(null, 'normal')
            })

            // Collapse by default unless there are errors
            initStatus = setInitStatus != null ? setInitStatus : $(this).find('.errors').length != 0;
            firstStatus = setFirstStatus != null ? setFirstStatus : initStatus;

            toggleCollapse(i == 0 ? firstStatus : initStatus)
        });
    };

    var init = function() {
        $.makeCollapsible('div#changelist-filter', 'div.inline-related', 'fieldset', 'h2');
    }
    init();
    // init again when "Add another" link is clicked
    $('.add-row a').click(function() {
        init();
    })
});




jQuery(function($) {
	$(document).ready(function() {
		// Add anchor tag for Show/Hide link
		$("#changelist-filter").each(function(i, elem) {
			// Don't hide if fields in this fieldset have errors
			if ($(elem).find("div.errors").length == 0) {
				$(elem).addClass("").find("h2").first().append(' (<a id="fieldsetcollapser' +
					i +'" class="collapse-toggle" href="#">' + gettext("Hide") +
					'</a>)');
			}
		});
		// Add toggle to anchor tag
		$("#changelist-filter a.collapse-toggle").toggle(
			function() { // Hide
				$(this).text(gettext("Show")).closest("div").addClass("collapsed").trigger("hide.div", [$(this).attr("id")]);
				return false;
			},
			function() { // Show
				$(this).text(gettext("Hide")).closest("div").removeClass("collapsed").trigger("show.div", [$(this).attr("id")]);
				return false;
			}
		);
	});
});