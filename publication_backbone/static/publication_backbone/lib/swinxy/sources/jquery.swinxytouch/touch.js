;(function($, undefined)
{

    // Early versions of android really mess up when they fake mouse events so as a temporary hack
    // we disregard the mouse on these devices.
    var ua = navigator.userAgent.toLowerCase();
    var isMobileAndroid = ((ua.indexOf("android") > -1) && (ua.indexOf("mobile") > -1));
    
    var
      
      p = 'swinxytouch',
      
      defaults =
      {
          preventDefault: false,
          stopPropagation: false
      },
      
      // New events we will be adding
      sxyEvents = ['sxy-focus', 'sxy-blur', 'sxy-hover', 'sxy-down', 'sxy-move', 'sxy-up'];
      
    /**
     * Quick way to get the TouchPad instance of an element or instantiate
     * if needed.
     * 
     * @param element e TouchPad will be attatched to this element
     * @param object o Each TouchPad is allowed to have it's own options by using the swinxytouch helper first
     * 
     * @return TouchPad
     */
    function getInstance(e, o)  
    {
        var t;
        return (!(t = $.data(e, p))) ? $.data(e, p, t = new TouchPad(e, o)) : t;
    }
    
    /**
     * Angle based on the coordinates of 2 points, each point
     * takes the form of {x:int, y:int}
     * 
     * @param object p1 
     * @param object p2
     * 
     * @return float Calculated angle in degrees, 0-360 but the starting orientation is left not up.
     */
    function angle(p1, p2)
    {
        var
          t;

        return (((t = Math.atan2((p1.y - p2.y), (p1.x - p2.x))) < 0) ? (360 - t) : t);
    }
    
    /**
     * Simple distance between the specified points, each point
     * takes the form of {x:int, y:int}
     * 
     * @param object p1
     * @param object p2
     * 
     * @return float
     */
    function distance(p1, p2)
    {
        var
          x = p1.x - p2.x,
          y = p1.y - p2.y
          
        return Math.sqrt((x * x) + (y * y));
    }

    /**
     *
     */
    function midpoint(p1, p2)
    {
        return { x: ((p1.x + p2.x) / 2), y: ((p1.y + p2.y) / 2) };
    }

    /**
     * Helper allowing gestures to be registered with jQuery events 
     * then hooked into an appropriate TouchPad as and when needed.
     *
     * @param string event The name people will use to hook into the gesture
     * @param object handler Gesture definition
     * @param object defaults User overridable object of default options the gesture uses
     * 
     * @return void
     */
    function gesture(event, handler, defaults)
    {
        $.event.special[event] =
        {
            setup: function()
            {
                var
                  tp = getInstance(this),
                  n,
                  h;
                  
                h = tp.g[event] = new handler(tp, defaults);
                
                for (var i = 0, c = sxyEvents.length; i < c; ++i)
                    if (h[n = sxyEvents[i]])
                        tp.el.on(n, h[n]);
            },
            teardown: function()
            {
                var
                  tp = getInstance(this),
                  n,
                  h = tp.g[event];
 
                for (var i = 0, c = sxyEvents.length; i < c; ++i)
                    if (handler[n = sxyEvents[i]])
                        tp.el.off(n, h);
                
                tp.g[event] = null;
            }
        };
    }

    /**
     *
     */
    function helper(name, obj)
    {
        TouchPad.prototype[name] = function()
        {
            this.h[name] = new obj(this);
        }
    }

    /**
     * 
     */
    function TouchPad(element, options)
    {
        var
        
          s = this,
          eventType = 'sxy-hover',
          mouseState = {x: 0, y: 0, down: false},
          handlers = [],
          eventMap = {},
          originalEvent;
        
        this.options = options = $.extend({}, defaults, options);
        
        this.el = $(element);
        this.pt = [];
        this.g  = {};
        this.h  = {};
        this.hasFocus = false;
        
        for (var i = 0; i < sxyEvents.length; ++i)
            eventMap[sxyEvents[i]] = [];


        // Mouse specific event handlers

        if (!isMobileAndroid)
        {
            listen('mouseenter', [0, 2, 4], function(e)
            {
                if (!s.hasFocus)
                    focus(mouse, e);
                
                eventType = 'sxy-hover';
                mouse(e);
            });
            
            // 
            listen('mouseleave', [1, 2, 5], function(e)
            {
                mouseState.down ? eventType = 'sxy-up' : eventType = 'sxy-hover';
                mouseState.down = false;
                mouse(e);

                blur(mouse, e);
            });
            
            listen('mousedown', [3, 4], function(e)
            {
                eventType = 'sxy-down';
                mouseState.down = true;
                mouse(e);
                
                eventType = 'sxy-move';
            });
            
            listen('mouseup', [0, 1, 2, 3, 4, 5], function(e)
            {
                eventType = 'sxy-up';
                mouseState.down = false;
                mouse(e);
                
                eventType = 'sxy-hover';
            });
            
            listen('mousemove', [2, 4], mouse);
        }
        
        // Touch specific event handlers

        listen('touchstart', [0, 1, 2, 3, 4, 5], function(e)
        {
            eventType = 'sxy-down';
            
            if (!s.hasFocus)
                focus(touch, e);
            
            touch(e);
            
            eventType = 'sxy-move';
        });

        listen('touchend', [0, 1, 2, 3, 4, 5], function(e)
        {
            
            eventType = 'sxy-up';
            touch(e);  
            
            eventType = 'sxy-hover';
        });
        
        listen('touchmove', [0, 1, 2, 3, 4, 5], touch);
        
        // Focus specific touch event
        
        var touchFocusHandler = function(e)
        {
            if (s.pt.length == 0)
                blur(touch, e);
        };
        
        /*
         * Public Methods
         */
        
        var createEvent = $.Event;
        
        this.trigger = function(type, data)
        {
            originalEvent.preventDefault();

            data = data || {};

            data.pointers      = s.pt;
            data.originalEvent = originalEvent;

            s.el.trigger(createEvent(type, data));
        }
        
        this.eventEnabler = function(event, state)
        {
            var
              t,
              e = eventMap[event],
              n = ((state) ? 1 : -1);

            for (var i = 0, c = e.length; i < c; ++i)
            {
                switch(((t = e[i]).l += n)) 
                {
                    case 0: t.el.off(t.e, t.hnd); break;
                    case 1: t.el.on(t.e, t.hnd); break;
                }
            }
        };
        
        /*
         * Private Methods
         */

        function focus(handler, event)
        {
            $(document).on('touchstart', touchFocusHandler);
            
            s.hasFocus  = true;
            eventType = 'sxy-focus';
            
            if (handler)
                handler(event);
            
            eventType = 'sxy-hover';
        }
        
        s.focus = focus;
        
        function blur()
        {
            $(document).off('touchstart', touchFocusHandler);

            s.hasFocus = false;
            eventType = 'sxy-blur';

            s.el.triggerHandler(eventType);
            eventType = 'sxy-hover';
        }
        
        s.blur = blur;
        
        function mouse(e)
        {
            originalEvent = e;
            
            mouseState.x = e.pageX;
            mouseState.y = e.pageY;

            s.pt = [mouseState];

            s.trigger(eventType);
        }


        function touch(e)
        {
            originalEvent = e;
            
            var
              tt = e.originalEvent.targetTouches,
              pt = s.pt = [];

            
            for (var i = 0, c = tt.length; i < c; ++i)
                pt.push({x: tt[i].pageX, y: tt[i].pageY});

            s.trigger(eventType);
        }
        
        function listen(event, dependents, cb, el)
        {
            var
              h;

            handlers.push(h =
            {
                e: event,
                hnd: cb,
                l: 0,
                el: el || s.el
            });

            for (var i = 0, c = dependents.length; i < c; ++i)
                eventMap[sxyEvents[dependents[i]]].push(h);
        }
    }

    /*
     * All done with our definitions, time to do some plumbing in jQuery
     */

    // Register our custom events

    var

      touchSetupFactory = function(e)
      {
          return function() { getInstance(this).eventEnabler(e, true); };
      },
      touchTeardownFactory = function(e)
      {
          return function() { getInstance(this).eventEnabler(e, false); };
      };

    for (var i = 0, c = sxyEvents.length; i < c; ++i)
    {
        var e = sxyEvents[i];
        
        $.event.special[e] =
        {
            setup: touchSetupFactory(e),
            teardown: touchTeardownFactory(e)
        };
    }
    
    // Register the main helper for use with selectors
    
    $.fn[p] = function(method)
    {
        return this.each(function()
        {
            var tp = getInstance(this);
            
            if (method && tp[method])
            {
                tp[method].apply(tp, Array.prototype.slice.call(arguments, 1));
            }
        });
    };
    
    // Register the rest of our helpers
    
    $.fn[p].g = gesture;
    $.fn[p].d = distance;
    $.fn[p].a = angle;
    $.fn[p].h = helper;
    $.fn[p].m = midpoint;
})
(jQuery);