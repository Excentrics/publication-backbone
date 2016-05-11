;(function($, undefined)
{
    var h = 'bound', p = 'swinxytouch';
    
    /**
     * 
     */
    function BoundHelper(tp)
    {
        var

          offset = tp.el.offset(),

          left   = offset.left,
          top    = offset.top,
          right  = left + tp.el.width(),
          bottom = top + tp.el.height();
         
        tp.el.on('sxy-hover sxy-down sxy-up sxy-move sxy-focus', function(e)
        {
            var p = e.pointers[0];

            if (p.y < top || p.x > right || p.y > bottom || p.x < left)
            {
                if (tp.hasFocus)
                    tp.blur();
            }
            else
            {
                if (!tp.hasFocus)
                {
                    tp.focus();
                    tp.el.trigger($.Event('sxy-focus', { pointers: e.pointers, originalEvent: e.originalEvent }));
                }
            }
        });
    }
    
    $.fn[p].h(h, BoundHelper);    
})
(jQuery);