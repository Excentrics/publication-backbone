;(function($, undefined)
{
    function ZoomSlippy(b)
    {
        this.initialised = false;
        
        var
          s = this,
          start = {};
        
        function tearUp()
        {
            b.dp.j.on('sxy-focus', function(e) { focus(e.pointers[0].x, e.pointers[0].y); });
            b.dp.j.on('sxy-blur',  function(e) { blur(); });
            b.dp.j.on('sxy-down', function(e) { b.dp.j.toggleClass('down'); var p = e.pointers[0]; start = { l: b.dmp.tX, t: b.dmp.tY, x: p.x - b.dp.ol, y: p.y - b.dp.ot }});
            b.dp.j.on('sxy-up', function(e) { b.dp.j.toggleClass('down'); });
            b.dp.j.on('sxy-move', function(e) { var p = e.pointers[0]; move(p.x, p.y); });
        }

        var timer = false, lastLeft, lastTop;

        function load(x, y)
        {
            b.vp.j.css({opacity: 0.0, width: b.dp.w, height: b.dp.h, left: 0, top: 0});

            start = { l: 0, t: 0, x: x, y: y };
            b.center((b.dp.w / 2), (b.dp.h / 2), false);
            
            lastLeft = lastTop = 0;
            
            if (!s.initialised)
                tearUp();

            if (b.hasFocus)
                focus(x, y);
        };

        function focus(x, y)
        {
            if (!b.waiting)
            {
                b.si.j.show();
                b.vp.j.show();
                b.vf.j.show();

                b.vp.j.stop().animate({opacity: 1.0}, { queue: false });
            }
        };

        function blur(x, y)
        {
            b.vf.j.hide();
            b.vp.j.animate({opacity: 0.0}, { queue: false });
        };

        function zoom(x, y)
        {
            b.center(b.cursor.lastX- b.dp.ol, b.cursor.lastY - b.dp.ot, false);
            b.vf.j.css({left:b.vf.l, top:b.vf.t});  
        };

        function _moveViewFinder()
        {
            var
              vf  = b.vf,
              vfs = b.vf.e.style;
              
            if (vf.l != lastLeft || vf.t != lastTop)
            {
                vfs.left = (lastLeft = vf.l) + 'px';
                vfs.top  = (lastTop = vf.t) + 'px';

                timer = setTimeout(_moveViewFinder, 8);
            }
            else
            {
                timer = false;
            }
        }

        function move(x, y)
        {
            b.move((start.l + ((x - b.dp.ol) - start.x)), (start.t + ((y - b.dp.ot) - start.y)), true);

            if (!timer)
                _moveViewFinder();
        };

        s.tearUp = tearUp;
        s.load   = load;
        s.focus  = focus;
        s.blur   = blur;
        s.zoom   = zoom;
    }
    
    $.fn['swinxyzoom']['modes']['slippy'] = ZoomSlippy;
})
(jQuery);