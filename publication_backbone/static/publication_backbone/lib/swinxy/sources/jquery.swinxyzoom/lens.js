;(function($, undefined)
{
    function ZoomLens(b)
    {
        this.initialised = false;

        var
          s = this,
          hasFocus = true;

        var _hndMove  = function(e) { var p; if ( e.pointers.length == 1) { p = e.pointers[0]; move(p.x, p.y, true); } };

        function tearUp(x, y)
        {      
            b.dp.j.swinxytouch('bound');
            b.dp.j.on('sxy-focus', function(e) { focus(e.pointers[0].x, e.pointers[0].y); });
            b.dp.j.on('sxy-blur', function() { blur(); });
        };

        var timer = false, lastLeft, lastTop;

        function load(x, y)
        {
            b.vp.j.css({opacity: 0.0, width: 200, height: 200, left: 0, top: 0});
            b.vp.w = 200;
            b.vp.h = 200;
            b.vp.j.show();
            b.si.j.show();
            b.vf.j.hide();

            lastLeft = lastTop = 0;

            if (!s.initialised)
                s.tearUp();

            if (b.hasFocus)
                focus(x, y);
        }

        function focus(x, y)
        {
            if (!b.waiting)
            {
                hasFocus = true;

                b.dp.j.on('sxy-hover sxy-move sxy-down', _hndMove);
                b.vp.j.show(); 
                b.vp.j.stop().animate({opacity: 1.0, width: b.vp.w, height: b.vp.h}, { queue: false });

                s.move(x, y, true);
            }
        };

        function blur()
        {
            if (hasFocus)
            {
                hasFocus = false;
                b.dp.j.off('sxy-hover sxy-move sxy-down', _hndMove);
                b.vp.j.stop().animate({opacity: 0.0}, { queue: false, complete: function() { b.vp.j.hide(); } });
            }
        };

        function _moveViewFinder()
        {
            var
              vf  = b.vf,
              vp  = b.vp,
              vps = b.vp.e.style;
              
            if (vf.l != lastLeft || vf.t != lastTop)
            {
                vps.left = (b.cursor.lastX - b.dp.ol) - (vp.w / 2) + 'px';
                vps.top = (b.cursor.lastY - b.dp.ot) - (vp.h / 2) + 'px';

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

        function zoom(x, y)
        {
            move(x, y, false);
        };

        s.tearUp = tearUp;
        s.load   = load;
        s.focus  = focus;
        s.blur   = blur;
        s.move   = move;
        s.zoom   = zoom;
    }

    $.fn['swinxyzoom']['modes']['lens'] = ZoomLens;
})
(jQuery);