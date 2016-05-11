;(function($, undefined)
{
    var
    
      defaults = 
      {
          'damping': 8,
          'steps': 15,
          'mode': 'dock'
      },
      
      p = 'swinxyzoom';

    /**
     *
     */
    function E(e, x)
    {
        this.e = e.get(0);
        this.j = e.first();
          
        if (x != undefined) $.extend(this, x);
    }


    /**
    * @constructor
    */
    function Zoom(element, options)
    {
        var s = this;

        s.element = $(element);
        s.options = $['extend']({}, defaults, options);

        s.driver = new $.fn.swinxyzoom.modes[s.options['mode']](this);
        
        s.initialised = false; // true when the target elements html is rebuilt
        s.enabled     = false; // true when everything is up and running
        s.waiting     = null;  // holds callback if waiting on user interaction before loading large image
        
        s.element.css({cursor: 'default'});
    
        s.dmp = {cX: 0, tX: 0, cY: 0, tY: 0, timer: false};

    
        s.hasFocus = false;
        
        /*
         * Internal functions used as callbacks requiring a this = that style
         * closure
         */

        /**
         *
         */
        s._animate = function()
        {
            var 
              dmp   = s.dmp,
              sis   = s.si.e.style,
              d     = s.options['damping'],
              xDiff = dmp.tX - dmp.cX,
              yDiff = dmp.tY - dmp.cY;

            sis.left = (dmp.cX += xDiff / d) + 'px';
            sis.top  = (dmp.cY += yDiff / d) + 'px';

            if ((~~(xDiff) == 0) && (~~(yDiff) == 0))
            {
                clearTimeout(dmp.timer);
                dmp.timer = false;
            }
        };
         
        /**
         *
         */
        s._moveSlider = function(tp)
        {
            var y = tp.pointers[0].y;

            var offset = s.ct.sl.j.offset();
            var scale = (s.maxZoom / s.ct.sl.j.height());

            y = s.ct.sl.j.height() - (y - offset.top);

            var level = y * scale;

            s.zoom(level, s.cursor.lastX, s.cursor.lastY);
        };
        
        /**
         *
         */
        s._focus = function()
        {
            s.hasFocus = true;
            s.ct.j.show();
            s.ct.ol.j.stop().animate({opacity:0.5}, {queue:false});
            s.ct.j.show();
        };
        
        /**
         *
         */
        s._blur = function(e)
        {
            s.hasFocus = false;
            s.ct.j.hide();
            s.ct.ol.j.stop().animate({opacity:0.0}, {queue:false, complete: function() {  }});
            //s.ct.j.stop().animate({opacity:0.0},{queue:false, complete: function() { s.ct.j.hide(); }});
            
        }
        
        /**
         *
         */
        s._mousewheel = function(e, d, x, y)
        {
            e.preventDefault();
            s.zoom(s.level + Math.round(y * (s.maxZoom / s.options['steps'])), e.pageX, e.pageY);
        };
        
        /**
         *
         */
        s._stepIn = function(e)
        {
            e.preventDefault();
            s.zoom(s.level + Math.round(1 * (s.maxZoom / s.options['steps'])), s.cursor.lastX, s.cursor.lastY);
        };
        
        /**
         *
         */
        s._stepOut = function(e)
        {
             e.preventDefault();
             s.zoom(s.level + Math.round(-1 * (s.maxZoom / s.options['steps'])), s.cursor.lastX, s.cursor.lastY);
        };
        
        var scaleStartLevel;
        
        s._scale = [];
        s._scale[1] = function(e) {  scaleStartLevel = s.level; $('#info').append('start[' + scaleStartLevel + '] '); };
        s._scale[2] = function(e) { $('#info').append('s '); $('#info').append('s[' + Math.abs((scaleStartLevel * e.scale)) + ',' + e.position.x + '] '); s.zoom((scaleStartLevel * e.scale), e.position.x, e.position.y);  };
        s._scale[3] = function(e) {};
        
        var thumbSrc = s.element.children().first().attr('src');
        var largeSrc = s.element.attr('href');
        
        var img = new Image();
        img.onload = function() { s.load(thumbSrc, largeSrc); }
        img.src = thumbSrc;
    }

    /**
     *
     */
    Zoom.prototype.load = function(thumb, large, hasFocus)
    {
        var
          s = this;
        
        if (s.initialised == false)
            s.tearUp();
        
        if (hasFocus)
            s._focus();
        
        s.dp.tn.src = thumb;
        s.si.src = large;
        
        /*
         * Handle loading of the thumbnail
         */
        
        if (s.dp.tn.j.attr('src') != s.dp.tn.src)
        {
            s.dp.tn.j.one('load', function()
            {
                s.rt.j.css({width:s.dp.tn.j.width(), height:s.dp.tn.j.height()});
                
                s.dp.tn.j.stop().animate({opacity: 1.0}, {queue: false, complete: function()
                {
                    s.rt.j.css({background: "url('" + s.dp.tn.src + "')"});
                    s.dp.tn.j.css({opacity: 0.0});
                }});
            });


            s.dp.tn.j.attr('src', s.dp.tn.src);
        }

        /*
         * Handle loading of the large image
         */

        var hndLoad = function(x, y)
        {
            var _hndMove;
            
            s.si.j.one('load', function()
            {
                s.dp.j.off('sxy-move sxy-hover', _hndMove);
                s.waiting = null;
                
                s.rebuild();
                s.zoom(s.maxZoom, s.cursor.lastX, s.cursor.lastY);

                if (s.driver.load)
                    s.driver.load(s.cursor.lastX, s.cursor.lastY);

                s.zoom(s.maxZoom, s.cursor.lastX, s.cursor.lastY);
                s.rt.j.toggleClass('sxy-zoom-loading');
            });
            
            s.cursor = { lastX: x, lastY: y};
            s.dp.j.on('sxy-move sxy-hover', _hndMove = function(e) { var p = e.pointers[0]; s.cursor = {lastX: p.x, lastY: p.y}; });
            s.si.j.attr('src', s.si.src);
        }
        
        if (hasFocus)
        {
            s.waiting = null;
            s.rt.j.toggleClass('sxy-zoom-loading');
            hndLoad(0, 0);
        }
        else
        {
            if (!s.waiting)
            {
                s.rt.j.one('sxy-focus', s.waiting = function(e)
                {                    
                    s.rt.j.toggleClass('sxy-zoom-loading');
                    hndLoad(e.pointers[0].x, e.pointers[0].y);
                });
            }
        }
        
    };

    /**
     *
     */
    Zoom.prototype.getNaturalSize = function(src)
    {
        var i = new Image();
        i.src = src;
        
        return {w: i.width, h: i.height};
    };

    /**
     *
     */
    Zoom.prototype.rebuild = function()
    {
        var
          s  = this,
          dp = s.dp,
          vp = s.vp,
          si = s.si,
          vf = s.vf;
        
        
        // Dragpad
        $.extend(dp, 
        {
            w   : dp.tn.j.width(),
            h   : dp.tn.j.height(),
            ol  : dp.j.offset().left,
            ot  : dp.j.offset().top,
            hyp : Math.round(Math.sqrt(Math.pow(dp.tn.j.width(), 2) + Math.pow(dp.tn.j.height(), 2)))
        });
        
        dp.j.css({width: dp.w, height:dp.h});
        dp.ovl.j.css({width: dp.w, height:dp.h});
        
        // Container
        s.rt.j.css({width: dp.w, height:dp.h});
        
        // Viewport
        $.extend(vp, { w: dp.w, h: dp.h });
        s.vp.j.css({width: dp.w, height:dp.h});
        
        // Scale Image
        
        var siNs = s.getNaturalSize(s.si.src);
        
        $.extend(si,
        {
            w: 0,
            h: 0,
            l: 0,
            t: 0,
            mL: 0,
            mT: 0,
            oHyp: Math.round(Math.sqrt(Math.pow(siNs.w, 2) + Math.pow(siNs.h, 2))),
            oH: siNs.h,
            oW: siNs.w
        });
        
        // View Finder
        $.extend(vf, {w: 0, h: 0, l: 0, t: 0});
        
        // Controls
        s.ct.j.css({height: dp.h});
        s.ct.sl.j.css({height: (s.ct.sl.h = (s.ct.j.height() - (s.ct.zin.j.outerHeight() + s.ct.zout.j.outerHeight())))});
        
        s.ct.sl.h -= 16;
        
        // General Variables
        clearTimeout(s.dmp.timer);
        
        s.dmp     = {cX: 0, tX: 0, cY: 0, tY: 0, timer: false};
        s.scale   = Math.atan(s.si.oH / s.si.oW);
        s.angle   = 0;
        s.maxZoom = si.oHyp - dp.hyp;
        s.level   = 0;
        //s.cursor  = { lastX: 0, lastY: 0 };
    };

    /**
     * 
     */
    Zoom.prototype.tearUp = function()
    {
        var
          t = null,
          s = this,
         
          tplWrapper = '<div class="sxy-zoom-container sxy-zoom-mode-{mode}" style="width: {w}px; height: {h}px; background: url({srcthumb})" ></div>',
          tplContent   = '<div class="sxy-controls" style="height: {h}px;" >'
                         + '<div class="overlay" style="height: {h}px;"></div>'
                         + '<a class="in" href="#"></a>'
                         + '<div class="sxy-slider" style="height:{h}px;"><div class="sxy-handle" style="top: 0px;"></div></div>'
                         + '<a class="out" href="#"></a>'
                       + '</div>'
                       + '<div class="sxy-zoom-dragpad" style="width:{w}px; height:{h}px;">'
                         + '<div class="sxy-overlay" style="width: {w}px; height: {h}px;"></div>'
                         + '<div class="sxy-zoom-viewport"><img galleryimg="no" /></div>'
                         + '<img class="inner-thumb" src="{srcthumb}" />'
                         + '<div class="sxy-zoom-viewfinder"></div>'
                       + '</div>'
                       + '<div class="sxy-loading"><span></span></div>';

        s.initialised = true;

        /*
         * Asked to load a new image without ever tearing up the original, clear
         * waiting.
         */
/*
        if (s.waiting)
        {
            s.element.off('sxy-focus', s.waiting);
            s.waiting = null;
        }
*/
        // Target Element
        s.el    = new E(s.element);
        s.el.tn = new E(s.element.children());

        var thumbDimensions = s.getNaturalSize(s.el.tn.j.attr('src'));

        var filters =
        {
            'w': thumbDimensions.w,
            'h': thumbDimensions.h,
            'srcthumb': s.el.tn.j.attr('src'),
            'mode': s.options['mode']
        };

        s.el.j.wrap(tplWrapper.replace(/\{(\w+)\}/g, function(s, k) { return filters[k] || s; }));
        s.element.hide();
        
        // Root Container
        s.rt = new E(s.el.j.parent());
        s.rt.j.append(tplContent.replace(/\{(\w+)\}/g, function(s, k) { return filters[k] || s; }));
        
        s.rt.j.on('dragstart', function(e) { return false; });
        
        // Controls
        s.ct      = new E(s.rt.j.find('.sxy-controls').hide());
        s.ct.ol   = new E(s.ct.j.find('.overlay'));
        s.ct.zin  = new E(s.ct.j.find('.in'));
        s.ct.zout = new E(s.ct.j.find('.out'));
        s.ct.sl   = new E((t = s.ct.j.find('.sxy-slider').first()), {h:0 });
        s.ct.hnd  = new E(s.ct.j.find('.sxy-handle'));

        // Dragpad
        s.dp     = new E((t = s.rt.j.find('.sxy-zoom-dragpad').first()), {w: 0, h: 0, ol: 0, ot: 0, hyp: 0});
        
        s.dp.ovl = new E(s.dp.j.find('.sxy-overlay'));
        s.dp.tn  = new E(s.dp.j.find('.inner-thumb').css({opacity: 0}), {src: ''});

        // Viewport
        s.vp = new E(s.dp.j.find('.sxy-zoom-viewport').css({opacity: 0.0}), {w: 0, h: 0});
        
        // Scale Image
        s.si = new E(s.vp.j.find('img'), {w: 0, h: 0, l: 0, t: 0, mL: 0, mT: 0, oHyp: 0, oH: 0, oW: 0, src: ''});
        
        // View Finder
        s.vf = new E(s.dp.j.find('.sxy-zoom-viewfinder').css({display: 'none'}), {w: 0, h: 0, l: 0, t: 0, osl: 0, ost: 0});
        
        /*
         * Wire up the events we're interested in
         */
        
        s.rt.j.on('sxy-focus', s._focus);
        s.rt.j.on('sxy-blur', s._blur);

        if($.event['special'].mousewheel)
            s.rt.j.on('mousewheel', s._mousewheel);
        
        s.dp.j.on('sxy-scale', function(e) { s._scale[e.state](e);});
        
        s.ct.zin.j.on('click', s._stepIn);
        s.ct.zout.j.on('click', s._stepOut);

        s.ct.sl.j.on('sxy-down sxy-move', s._moveSlider);

    };

    /**
     *
     */
    Zoom.prototype.move = function(left, top, animate)
    {
        var s = this;

        /*
         * Update viewfinder values, we dont change the css here
         * and leave that upto the driver.
         */

        var sL = (-1 * (left / s.scale));
        var sT = (-1 * (top / s.scale));

        // Store requested center point (usually this is the relative x,y of the cursor, this
        // is needed later to zoom in and out as expected.

        s.cursor.lastX = sL + (s.vf.w / 2) + s.dp.ol;
        s.cursor.lastY = sT + (s.vf.h / 2) + s.dp.ot;

        /*
         * Keep values within range of the current scaled original
         * image.
         */

        if (sL < 0) { sL = left = 0; }
        if (sT < 0) { sT = top = 0; }

        if ((sL + s.vf.w) > s.dp.w) { sL = s.dp.w - s.vf.w; left = s.si.mL; }
        if ((sT + s.vf.h) > s.dp.h) { sT = s.dp.h - s.vf.h; top = s.si.mT; }

        // IE8 FIX - For some reason subpixel rounding in IE8 appears to work differently? So
        // for the momment lets just force everyone to floor it.

        s.vf.l = ~~(sL);
        s.vf.t = ~~(sT);

        /*
         * Prime the dampening animation
         */

        s.dmp.tX = left;
        s.dmp.tY = top;                

        if (animate && s.options['damping'] != false)
        {
            if (!s.dmp.timer)
                s.dmp.timer = setInterval(s._animate, 16); // Aim for 60fps
        }
        else
        {
            clearTimeout(s.dmp.timer);
            s.dmp.timer = false;
            
            var sis = s.si.e.style;
            sis.left = (s.dmp.tX = s.dmp.cX = left) + 'px';
            sis.top  = (s.dmp.tY = s.dmp.cY = top) + 'px';  
        }  
    };

    /**
     *
     */
    Zoom.prototype.center = function(x, y, animate)
    {
        var s = this;
        
        s.move((-1 * ((x - (s.vf.w / 2)) * s.scale)), (-1 * ((y - (s.vf.h / 2)) * s.scale)), animate);
    };

    /**
     *
     */
    Zoom.prototype.zoom = function(level, x, y)
    {
        var
          s = this,
          t = null;
        
        /*
         * Ensure we never go beyond the calculated maxmimum zoom
         * level
         */
        
        s.level = level;

        if (s.level < 0) s.level = 0;
        if (s.level > s.maxZoom) s.level = s.maxZoom;

        var pc = (((s.si.oHyp - s.level) / s.si.oHyp) * 100);

        // TODO: account for height of element
        s.ct.hnd.j.css({top:(s.ct.sl.h - ((s.ct.sl.h / 100) * ((s.level / s.maxZoom) * 100)))});

        s.vf.w = ((s.vp.w / 100) * pc);
        s.vf.h = ((s.vp.h / 100) * pc);

        // TODO: is this still used?
        s.vf.osl = parseInt(s.vf.j.css('border-left-width'), 10);
        s.vf.ost = parseInt(s.vf.j.css('border-top-width'), 10);

        /*
         * Scale gives us a multiplier we can use to translate the cursor coordinates on the thumnail to what
         * the coordiantes on the large image would be at the current zoom level.
         */

        // full image width / dragpad width = maximum possible scale
        // full scaled image width / viewing area width = portion of scaled image to display

        s.scale = (s.si.oW / s.vp.w) / (((s.si.oW / 100) * pc) / s.vp.w);

        s.si.w = (s.si.oW / (((s.si.oW / 100)*pc) / s.dp.w));
        s.si.h = (s.si.oH / (((s.si.oH / 100)*pc) / s.dp.h));

        s.vf.j.css({width: s.vf.w, height: s.vf.h});
        s.si.j.css({width: s.si.w, height: s.si.h});

        s.si.mL = (0 - (s.si.w - s.vp.w));
        s.si.mT = (0 - (s.si.h - s.vp.h));
        
        if (s.driver.zoom)
            s.driver.zoom(x, y);
    };

    /**
     * 
     */
    $.fn[p] = function(method)
    {
        var
          args = Array.prototype.slice.call(arguments, 1);
        
        return this.each(function()
        {
            var zoom;
            
            if((zoom = $.data(this, p)))
            {
                if(zoom[method])
                    return zoom[method].apply(zoom, args)
                
                $.error("Method " + method + " does not exist on jQuery.swinxyzoom")
            }
            else
            {
                $.data(this, p, new Zoom(this, method))
            }
       });
    }
    
    // Add a container for the various zoom modes
    
    $.fn[p]['modes'] = {};
})
(jQuery);