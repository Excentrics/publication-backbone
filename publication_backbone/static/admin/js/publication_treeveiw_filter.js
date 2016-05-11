(function($){
    $(function(){
        $("#manage-treeview-filter").treeview({
            collapsed: true
        });
    });
    
    function getUrlParams(url) {
        var params = {};
        url.replace(/[?&]+([^=&]+)=([^&]*)/gi,
             function (str, key, value) {
                  params[key] = value;
             });
        return params;
    }
    
    function makeFiltering(publication_rubrics_set) {
	old_param = $(location).attr('search')
 	params = getUrlParams(old_param)
	params['publication_rubrics_set'] = publication_rubrics_set;
        param = '?'
        $.each(params, function(i, val) {
       	    param = param + i + '=' + val + '&'
    	});
	if (param != '?') { param = param.slice(0,-1) }
	url = window.location.protocol + "//" + window.location.host + window.location.pathname + param;
        if (old_param != param) { window.location.href = url }
    }
    
    $(document).ready( function () {
        $("#manage-treeview-filter .rubric_set_checkbox").click(function() {
            rubric_list = new Array();
            $("#manage-treeview-filter :checked").each(function(){
                    rubric_list.push(parseInt($(this).val()))
                });
                makeFiltering(rubric_list.toString());
        });
        $("#clear_rubric_filter").click(function() {
            makeFiltering('');
            event.preventDefault();
        });
    });
})(django.jQuery);
