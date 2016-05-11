
;(function($, undefined)
{
    var g = 'sxy-tap', p = 'swinxytouch';
    
    var defaults =
    {
        'maxDelay': 10,
        'maxMove': 2
    }
    
    function TapGesture(tp, o)
    {
        var
        
          s = this,
          a = Math.abs,

          startTime,
          startPoint;
        
        s['sxy-down'] = function(e)
        {
            var pt = e.pointers;

            if (pt.length == 1)
            {
                startTime  = (new Date()).getTime();
                startPoint = {x: pt[0].x, y: pt[0].y};
            }
        };
            
        s['sxy-up'] = function(e)
        {
            var pt = e.pointers;

            if ((pt.length == 1) && (((new Date()).getTime() - startTime) < o.maxDelay) && (a(startPoint.x - pt[0].x) < o.maxMove) && (a(startPoint.y - pt[0].y) < o.maxMove))
                tp.trigger(g, startPoint);
        };
    }
    
    $.fn[p].g(g, TapGesture, defaults);
})
(jQuery);