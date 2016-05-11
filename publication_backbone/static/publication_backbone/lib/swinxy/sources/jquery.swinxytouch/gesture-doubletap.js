
;(function($, undefined)
{
    var g = 'sxy-doubletap', p = 'swinxytouch';
    
    var defaults =
    {
        'maxDelay': 10,
        'maxMove': 2
    }
    
    function DoubleTapGesture(tp, o)
    {
        var
        
          s = this,
          a = Math.abs,

          startTime,
          startPoint;
        
        s['sxy-tap'] = function(e)
        {
            var p = e.position;
            
            if (startTime == null)
            {
                startTime  = (new Date()).getTime();
                startPoint = {x: p.x, y: p.y};
            }
            else
            {
                if ((((new Date()).getTime() - s.time) < o.maxDelay) && (a(startPoint.x - p.x) < o.maxMove) && (a(startPoint.y - p.y) < o.maxMove))
                    tp.trigger(g, startPoint);
                
                startTime = null;
            }
        };
    }
    
    $.fn[p].g(g, DoubleTapGesture, defaults);
})
(jQuery);