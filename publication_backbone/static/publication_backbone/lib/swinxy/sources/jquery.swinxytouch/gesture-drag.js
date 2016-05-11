
;(function($, undefined)
{
    var g = 'sxy-drag', p = 'swinxytouch';
    
    function DragGesture(tp)
    {
        var
        
          s = this,
          
          isDragging,
          
          eventData = {position: {}};
        
        function trigger(e, state)
        {
            var pt = e.pointers;
            
            eventData.state = state;
            
            if (pt.length > 0)
            {
                eventData.position.x = pt[0].x;
                eventData.position.y = pt[0].y;
            }
            
            tp.trigger(g, eventData);
        }
            
        s['sxy-up'] = function(e)
        {
            if (isDragging)
                trigger(e, 3);
            
            isDragging = false;
        };
        
        s['sxy-move'] = function(e)
        {
            isDragging ? trigger(e, 2) : (isDragging = true, trigger(e, 1));
        };
    }
    
    $.fn[p].g(g, DragGesture);
})
(jQuery);