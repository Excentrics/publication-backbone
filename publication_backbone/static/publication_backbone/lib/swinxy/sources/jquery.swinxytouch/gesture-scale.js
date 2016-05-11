
;(function($, undefined)
{
    var g = 'sxy-scale', p = 'swinxytouch';
    
    var defaults =
    {
        'minScale': 0.2
    }
    
    function ScaleGesture(tp, o)
    {
        var
        
          s = this,

          distance = $.fn[p].d,
          midpoint = $.fn[p].m,
          
          isScaling,
          startDistance,
          
          eventData = {};
        
        function trigger(e, state)
        {
            var
              pt = e.pointers;
            
            eventData.state    = state;
            eventData.scale    = (distance(pt[0], pt[1]) / startDistance);
            eventData.position = midpoint(pt[0], pt[1]);
            
            tp.trigger(g, eventData);
        }

        s['sxy-down'] = function(e)
        {
            var
              pt = e.pointers;
            
            if (pt.length == 2)
            {
                isScaling = false;
                startDistance = distance({x:pt[0].x, y:pt[0].y}, {x:pt[1].x, y:pt[1].y});
            }
        };
            
        s['sxy-up'] = function(e)
        {
            if (isScaling)
                trigger(e, 3);
        };
        
        s['sxy-move'] = function(e)
        {
            var pt = e.pointers;
            
            if (pt.length == 2)
            {
                if (isScaling)
                {
                    trigger(e, 2);
                }
                else
                {


                    if (Math.abs(1 - (distance(pt[0], pt[1]) / startDistance)) > o.minScale)
                    {
                        isScaling = true;
                        trigger(e, 1);
                    }
                }
            }
        };
    }
    
    $.fn[p].g(g, ScaleGesture, defaults);
})
(jQuery);