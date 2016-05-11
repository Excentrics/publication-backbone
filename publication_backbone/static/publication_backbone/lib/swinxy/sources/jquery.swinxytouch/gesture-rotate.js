
;(function($, undefined)
{
    var g = 'sxy-rotate', p = 'swinxytouch';
    
    var defaults =
    {
        'minRotate': 3
    }
    
    function RotateGesture(tp, o)
    {
        var
        
          s = this,
          
          isRotating,
          
          angle = $.fn[p].a,
          
          startAngle,
          lastAngle,
          
          eventData = {};
        
        function trigger(e, state)
        {
            var
              rotation,
              currentAngle;
            
            eventData.state = state;
            eventData.rotation += (Math.abs(rotation = ((currentAngle = angle(e.pointers)) - lastAngle)) < 180) ? rotation : 0;
            
            lastAngle = currentAngle;
            
            tp.trigger(g, eventData);
        }
        
        s['sxy-down'] = function(e)
        {
            isRotating = false;
            startAngle = lastAngle = angle(e.pointers);
        };
            
        s['sxy-up'] = function(e)
        {
            if (isRotating)
                trigger(e, 3);
        };
        
        s['sxy-move'] = function(e)
        {
            if (isRotating)
            {
                trigger(e, 2);
            }
            else
            {
                if (Math.abs(startAngle - angle(e.pointers)) > o.minRotate)
                {
                    isRotating = true;
                    eventData.rotation = 0.0;
                    trigger(e, 1);
                }
            }
        };
    }
    
    $.fn[p].g(g, RotateGesture, defaults);
})
(jQuery);