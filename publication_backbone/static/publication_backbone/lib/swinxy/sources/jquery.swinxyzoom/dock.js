;(function($, undefined)
{
    function ZoomDock(b)
    {
        this.initialised = false;
        
        var
          hasFocus = false,
          s = this;
        
        var _hndMove = function(e) { var p; if ( e.pointers.length == 1) { p = e.pointers[0]; move(p.x, p.y, true); } };
        
        function checkBounds(x, y)
        {
            var

              offset = b.dp.j.offset(),

              left   = offset.left,
              top    = offset.top,
              right  = left + b.dp.j.width(),
              bottom = top + b.dp.j.height();
              
            return ((y < top || x > right || y > bottom || x < left) ? false : true);
        };
        
        function blur()
        {
            if (hasFocus)
            {
                hasFocus = false;
                b.vf.j.hide();

                b.dp.ovl.j.stop().animate({opacity: 0.0}, {queue: false});
                b.vp.j.stop().animate({opacity: 0.0, left: (b.dp.w / 2), top: (b.dp.h / 2), width: 0, height: 0},
                {
                    queue: false
                });
            }
        };        
        
        function focus(x, y)
        {
            if (!b.waiting)
            {
                hasFocus = true;

                b.si.j.show();
                b.vp.j.show();
                b.vf.j.show();

                b.dp.ovl.j.stop().animate({opacity: 0.5}, {queue: false});
                b.vp.j.stop().animate({opacity: 1.0, left: b.dp.w + 10, top: 0, width: b.vp.w, height: b.vp.h}, { queue: false });

                s.move(x, y, true);
            }
        };
        
        function tearUp()
        {
            b.rt.j.on('sxy-focus', function(e) { var p = e.pointers[0]; focus(p.x, p.y); });
            b.rt.j.on('sxy-blur',  function(e) {  blur(); });
            b.dp.j.on('sxy-hover sxy-move sxy-down', _hndMove);
        };
        
        var timer = false, lastLeft, lastTop;
        
        function load(x, y)
        {
            b.vp.j.css({width: 0, height: 0, left: (b.dp.w / 2), top: (b.dp.h / 2)});
            b.dp.ovl.j.css({opacity: 0});
            b.vf.j.css({'background-image': 'url(' + b.dp.tn.src + ')'});
            
            lastLeft = lastTop = 0;

            if (!s.initialised)
                tearUp();

            if (b.hasFocus)
                focus(x, y);
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
                vfs.backgroundPosition = '-' + (vf.l + b.vf.osl) + 'px -' + (vf.t + b.vf.ost) + 'px';

                timer = setTimeout(_moveViewFinder, 8);
            }
            else
            {
                timer = false;
            }
        }

        function move(x, y, animate)
        {
            if (checkBounds(x, y))
            {
                if (!hasFocus)
                    focus(x, y);

                b.center((x - b.dp.ol), (y - b.dp.ot), animate);
                
                if (!timer)
                    _moveViewFinder();
            }
            else
            {
                blur();
            }
        };

        s.tearUp = tearUp;
        s.load   = load;
        s.focus  = focus;
        s.blur   = blur;
        s.move   = move;
        s.zoom   = zoom;
    }
    
    $.fn['swinxyzoom']['modes']['dock'] = ZoomDock;
})
(jQuery);