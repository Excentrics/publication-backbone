;(function($, undefined)
{
    /**
    * @constructor
    */
    function ZoomWindow(b)
    {
        var
          s = this;
        
        this.initialised = false;

        function tearUp(x, y)
        {
            b.rt.j.on('sxy-focus', function(e) { focus(e.pointers[0].x, e.pointers[0].y); });
            b.rt.j.on('sxy-blur',  function() { blur(); });
            b.dp.j.on('sxy-hover sxy-move sxy-down', function(e) { var p; if ( e.pointers.length == 1) { p = e.pointers[0]; move(p.x, p.y, true); } });
        };
        
        var timer = false, lastLeft, lastTop;
        
        function load(x, y)
        {
            b.vp.j.css({opacity: 0.0, width: b.dp.w, height: b.dp.h, left: 0, top: 0});

            lastLeft = lastTop = 0;

            if (!s.initialised)
                s.tearUp();

            if (b.hasFocus)
                s.focus(x, y);
        }
        
        function focus(x, y)
        {
            if (!b.waiting)
            {
                b.si.j.show();
                b.vp.j.show();
                b.vf.j.show();

                b.vp.j.stop().animate({opacity: 1.0}, { queue: false });

                move(x, y, true);
            }
        };

        function blur()
        {
            b.vf.j.hide();
            b.vp.j.stop().animate({opacity: 0.0}, { queue: false });
        };

        function zoom(x, y)
        {
            move(x, y, false);
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

        function move(x, y, animate)
        {
            b.center((x - b.dp.ol), (y - b.dp.ot), animate);

            if (!timer)
                _moveViewFinder();
        };

        s.tearUp = tearUp;
        s.load   = load;
        s.focus  = focus;
        s.blur   = blur;
        s.move   = move;
        s.zoom   = zoom;
    }

    $.fn['swinxyzoom']['modes']['window'] = ZoomWindow;
})
(jQuery);