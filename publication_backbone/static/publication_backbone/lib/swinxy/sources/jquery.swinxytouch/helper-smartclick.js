
;(function($, undefined)
{
    var h = 'smartclick';
    
    /**
     *
     */
    function HelperSmartClick(b)
    {
        this.b = b;
        
        var
          s = this;

        s.allow = false;

        s._hndClick = function(e)
        {
            if (!s.allow)
                e.preventDefault();
                
            s.allow = false;
        };
        
        s._hndTap = function()
        {
            s.allow = true;
            $(b.lastEvent.target).trigger('click');
        };
        
        b.element.on('click', s._hndClick);
        b.on('tap', s._hndDown);
    }
 
   $.fn['swinxytouch']['helpers'][h] = HelperSmartClick;
 
})(jQuery);