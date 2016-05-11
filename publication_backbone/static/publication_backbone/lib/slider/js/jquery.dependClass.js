/**
 * jquery.dependClass - Attach class based on first class in list of current element
 * 
 * Written by
 * Egor Khmelev (hmelyoff@gmail.com)
 *
 * Licensed under the MIT (MIT-LICENSE.txt).
 *
 * Modify by
 * Yarovoy Artem (yarovoy@excentrics.ru)
 * 
 **/

(function($) {

    "use strict";

    $.baseClass = function(obj){
        obj = $(obj)
        return obj.get(0).className.match(/([^ ]+)/)[1]
    }
	
	$.fn.addDependClass = function(className, delimiter){
		var options = {
		  delimiter: delimiter ? delimiter : '-'
		}
		return this.each(function(){
            var baseClass = $.baseClass(this)
            if (baseClass)
                $(this).addClass(baseClass + options.delimiter + className)
		})
	}

	$.fn.removeDependClass = function(className, delimiter){
		var options = {
		  delimiter: delimiter ? delimiter : '-'
		}
		return this.each(function(){
            var baseClass = $.baseClass(this);
            if(baseClass)
                $(this).removeClass(baseClass + options.delimiter + className)
		})
	}

	$.fn.toggleDependClass = function(className, delimiter){
		var options = {
		  delimiter: delimiter ? delimiter : '-'
		}
		return this.each(function(){
            var baseClass = $.baseClass(this);
            if (baseClass) {
                if ($(this).is("." + baseClass + options.delimiter + className))
                    $(this).removeClass(baseClass + options.delimiter + className)
                else
                    $(this).addClass(baseClass + options.delimiter + className)
            }
		})
	}

})(jQuery);