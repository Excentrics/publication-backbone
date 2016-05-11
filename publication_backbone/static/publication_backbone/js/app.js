/**
 * app - backbone application core (BBNS) 1.0.0
 *
 * Written by
 * (c) 2007-2013 Yarovoy Artem, Excentrics Ltd.
 * http://excentrics.ru
 *
 * Licensed under the MIT (MIT-LICENSE.txt).
 *
 * Dependencies
 *
 * jQuery 1.8.0 (http://jquery.com)
 * _ Underscore.js 1.6.0 (http://underscorejs.org)
 * Backbone.js 1.1.2 (http://backbonejs.org)
 *
 **/


(function($, Backbone, _) {

    "use strict";

    //  Top-level namespace
    var BBNS = window.BBNS = {}

    // Create quick reference variables for speed access to core prototypes.
    var slice = [].slice

    // Helpers
    // -------

    // Shared empty constructor function to aid in prototype-chain creation.
    var ctor = function(){}

    // Helper function to correctly set up the prototype chain, for subclasses.
    // Similar to `goog.inherits`, but uses a hash of prototype properties and
    // class properties to be extended.
    var extend = function(protoProps, staticProps) {
        var parent = this
        ,   child

        // The constructor function for the new subclass is either defined by you
        // (the "constructor" property in your `extend` definition), or defaulted
        // by us to simply call the parent's constructor.
        if (protoProps && protoProps.hasOwnProperty('constructor')) {
            child = protoProps.constructor
        } else {
            child = function(){ parent.apply(this, arguments) }
        }

        // Inherit class (static) properties from parent.
        _.extend(child, parent)

        // Set the prototype chain to inherit from `parent`, without calling
        // `parent`'s constructor function.
        ctor.prototype = parent.prototype
        child.prototype = new ctor()

        // Add prototype properties (instance properties) to the subclass,
        // if supplied.
        if (protoProps) _.extend(child.prototype, protoProps)

        // Add static properties to the constructor function, if supplied.
        if (staticProps) _.extend(child, staticProps)

        // Correctly set child's `prototype.constructor`.
        child.prototype.constructor = child

        // Set a convenience property in case the parent's prototype is needed later.
        child.__super__ = parent.prototype

        return child
    }

    // Core
    // -------

    //  Protection against exceptions when window.console is not defined.
    if ( !window.console ) {
        window.console = {}
    }
    if ( !console.log ) {
        console.log = function() {}
    }
    if ( !console.warn ) {
        console.warn = function() {}
    }
    if ( !console.error ) {
        console.error = function() {}
    }
    if ( !console.info ) {
        console.info = function() {}
    }

    //  Main log output function.
    BBNS.consoleOutput = function() {
        var args = slice.call(arguments)
        ,   date
        ,   level
        ,   msg
        ,   outputRoutine = args[0]
        ,   timestamp

        args.shift()
        if ( !outputRoutine || !(Function.prototype.bind && console) ) {
            return
        }
        if ( args.length > 1 ) {
            level = parseInt(args[0])
            if ( [0, 1, 2, 3, 4, 5, 6].indexOf(level) > -1 ) {
                args.shift()
                if ( BBNS.app.debug < level ) {
                    return false
                }
            }
        }
        if ( isNaN(level) ) {
            level = 0
        }
        if ( level == null ) {
            level = 0
        }
        date = new Date
        timestamp = "" + (date.getUTCFullYear()) + "-" + (date.getUTCMonth() + 1) + "-" + (date.getUTCDate()) + "@" +
            (date.getUTCHours()) + ":" + (date.getUTCMinutes()) + ":" + (date.getUTCSeconds()) + "." + (date.getUTCMilliseconds())
        msg = args[0]
        if ( args.length > 1 ) {
            args.shift()
        } else {
            args = []
        }

        var outputRoutineWrapper = Function.prototype.bind.call(console[outputRoutine], console)
        outputRoutineWrapper.apply(console, ["[" + level + ":" + timestamp + "] " + msg].concat(args))

        return true

    }

    BBNS.log = function() {
        return BBNS.consoleOutput.apply(BBNS, ['log'].concat(slice.call(arguments)))
    }

    BBNS.info = function() {
        return BBNS.consoleOutput.apply(BBNS, ['info'].concat(slice.call(arguments)))
    }

    BBNS.warn = function() {
        return BBNS.consoleOutput.apply(BBNS, ['warn'].concat(slice.call(arguments)))
    }

    BBNS.error = function() {
        return BBNS.consoleOutput.apply(BBNS, ['error'].concat(slice.call(arguments)))
    }


    // -------------------------- ImagesLoaded -------------------------- //
    // Detect when images have been loaded.
    /**
    * @param {Array, Element, NodeList, String} elem
    * @param {Object or Function} options - if function, use as callback
    * @param {Function} onAlways - callback function
    */

    var ImagesLoaded = BBNS.ImagesLoaded = (function() {

        var ImagesLoaded = function(elem, options, onAlways) {
            if ( !( this instanceof ImagesLoaded ) ) {
                return BBNS.error("'new' keyword expected before 'ImagesLoaded(...'")
            }
            // use elem as selector string
            if ( _.isString(elem) ) {
                elem = document.querySelectorAll(elem)
            }
            this.elements = _.toArray(elem)
            this.options = _.extend({}, this.options)
            if ( _.isFunction(options) ) {
                onAlways = options
            } else {
                _.extend(this.options, options)
            }
            if ( onAlways ) {
                this.once('always', onAlways, this.options.context)
            }
            this.getImages()
            _.bindAll(this, 'check')
            // HACK check async to allow time to bind listeners
            _.defer(this.check)
        }

        _.extend(ImagesLoaded.prototype, Backbone.Events, {

            options: {}

        ,   getImages: function() {
                this.images = []
                // filter & find items if we have an item selector
                for ( var i=0, len=this.elements.length; i < len; i++ ) {
                    var elem = this.elements[i]
                    // filter siblings
                    if ( elem.nodeName === 'IMG' ) {
                        this.addImage( elem )
                    }
                    // find children
                    // no non-element nodes, #143
                    var nodeType = elem.nodeType
                    if ( !nodeType || !( nodeType === 1 || nodeType === 9 || nodeType === 11 ) ) {
                        continue
                    }
                    var childElems = elem.querySelectorAll('img')
                    // concat childElems to filterFound array
                    for ( var j=0, jLen = childElems.length; j < jLen; j++ ) {
                        var img = childElems[j]
                        this.addImage( img )
                    }
                }
            }

            /**
            * @param {Image} img
            */
        ,   addImage: function(img) {
                var loadingImage = new LoadingImage(img)
                this.images.push(loadingImage)
            }

        ,   check: function() {
                var checkedCount = 0
                ,   length = this.images.length
                this.hasAnyBroken = false
                // complete if no images
                if ( !length ) {
                    this.complete()
                    return
                }
                function onConfirm(image, message) {
                    if ( _.isNumber(this.options.debug) ) {
                        BBNS.log(this.options.debug, 'confirm', image, message)
                    }
                    this.progress(image)
                    checkedCount++
                    if ( checkedCount === length ) {
                        this.complete()
                    }
                }
                var isLoading = false
                for ( var i=0; i < length; i++ ) {
                    var loadingImage = this.images[i]
                    loadingImage.once('confirm', onConfirm, this)
                    if ( loadingImage.check() && !isLoading ) {
                        isLoading = true
                        this.trigger('loading', this)
                    }
                }
            }

        ,   progress: function(image) {
                this.hasAnyBroken = this.hasAnyBroken || !image.isLoaded
                // HACK - Chrome triggers event before object properties have changed.
                _.defer(_.bind(function() {
                    this.trigger('progress', this, image)
                }, this))
            }

        ,   complete: function() {
                var eventName = this.hasAnyBroken ? 'fail' : 'done'
                this.isComplete = true;
                // HACK - another setTimeout so that confirm happens after progress
                _.defer(_.bind(function() {
                    this.trigger(eventName, this)
                    this.trigger('always', this)
                }, this))
            }

        })

        return ImagesLoaded

    })()

    ImagesLoaded.extend = extend


    // -------------------------- LoadingImage -------------------------- //
    var LoadingImage = (function() {

        var LoadingImage = function(img) {
            this.img = img
        }

        _.extend(LoadingImage.prototype, Backbone.Events, {

            check: function() {
                // first check cached any previous images that have same src
                var resource = imageResourceCache[this.img.src] || new ImageResource(this.img.src)
                if ( resource.isConfirmed ) {
                    this.confirm(resource.isLoaded, 'cached was confirmed')
                    return false
                }
                // If complete is true and browser supports natural sizes,
                // try to check for image status manually.
                if ( this.img.complete && this.img.naturalWidth !== undefined ) {
                    // report based on naturalWidth
                    this.confirm(this.img.naturalWidth !== 0, 'naturalWidth')
                    return false
                }
                // If none of the checks above matched, simulate loading on detached element.
                resource.once('confirm', function(resrc, message) {
                    this.confirm(resrc.isLoaded, message)
                }, this)
                return resource.check()
            }

        ,   confirm: function(isLoaded, message) {
                this.isLoaded = isLoaded
                this.trigger('confirm', this, message)
            }

        })

        return LoadingImage

    })()

    LoadingImage.extend = extend

    var imageResourceCache = {}

    // -------------------------- ImageResource -------------------------- //
    // ImageResource checks each src, only once
    // separate class from LoadingImage to prevent memory leaks.
    var ImageResource = (function() {

        var ImageResource = function(src) {
            var args = slice.call(arguments)
            this.src = src
            // add to cache
            imageResourceCache[src] = this
            _.bindAll(this, 'onLoad', 'onError')
        }

        _.extend(ImageResource.prototype, Backbone.Events, {

            check: function() {
                // only trigger checking once
                if ( this.isChecked ) {
                    return false
                }
                // simulate loading on detached element
                var proxyImage = new Image()
                $(proxyImage).on('load', this.onLoad).on('error', this.onError)
                proxyImage.src = this.src
                // set flag
                this.isChecked = true
                return true
            }

        ,   onLoad: function(event) {
                this.confirm(true, 'onload')
                this.unbindProxyEvents(event)
            }

        ,   onError: function(event) {
                this.confirm(false, 'onerror')
                this.unbindProxyEvents(event)
            }

        ,   unbindProxyEvents: function(event) {
                $(event.target).off('load', this.onLoad).off('error', this.onError)
            }

        ,   confirm: function(isLoaded, message) {
                this.isConfirmed = true
                this.isLoaded = isLoaded
                this.trigger('confirm', this, message)
            }

        })

        return ImageResource

    })()

    ImageResource.extend = extend


    // A module that uses Backbone's collection to represent the cookies that you can read on a site.
    // Also allows the creation and editing of these cookies.

    var CookieModel = Backbone.Model.extend({

        idAttribute: 'name'

    ,   defaults: {
            days: 0
        }

    ,   destroy: function() {
            this.set({
                value: ""
            ,   days: -1
            }).save()
        }

    ,   validate: function(attrs) {
            if( !attrs.name ) {
                return "Cookie needs name"
            }
        }

    ,   get: function(name) {
            if ( name == 'value' ) {
                var value = this.attributes[name]
                if ( value[0] == '"' ){
                    value = value.slice(1, value.length - 1)
                }
                return decodeURIComponent(value)
            } else {
                return this.attributes[name]
            }
        }

    ,   save: function() {
            var pieces = []
            ,   value = this.get('value')
            if ( value.match(/[^\w\d]/) ) {
                value = '"'.concat(encodeURIComponent(value), '"')
            }
            pieces.push(this.get('name').concat("=", value))
            if ( this.get('days') ) {
                var date = new Date();
                date.setTime(date.getTime() + (this.get('days')*24*60*60*1000))
                pieces.push("expires".concat('=', date.toGMTString()))
            }
            if ( this.get('path') ) {
                pieces.push("path".concat('=', this.get('path')))
            }
            if ( this.get('domain') ) {
                pieces.push("domain".concat('=', this.get('domain')))
            }
            if ( this.get('secure') ) {
                pieces.push("secure")
            }
            document.cookie = pieces.join('; ')
        }
    })

    var cookie = BBNS.Cookie = new (Backbone.Collection.extend({

        model: CookieModel

    ,   initialize: function() {
            this._readCookies()
            this.on('add', function (model) {
                model.save()
            })
        }

    ,   remove: function(models) {
            Backbone.Collection.prototype.remove.apply(this, arguments)
            models = _.isArray(models) ? models.slice() : [models]
            var i, l
            for (i = 0, l = models.length; i < l; i++) {
                models[i].destroy()
            }
        }

    ,   _readCookies: function () {
            var cookies = document.cookie.split('; ')
            ,   cookieObjects = {}
            for (var i = 0, l = cookies.length; i < l; i++) {
                if( cookies[i].match(/^\n+$/) ) {
                    continue
                }
                var cookie = cookies[i].split(/^([^=]+)=(.*$)/)
                cookie = [
                    cookie[1],
                    cookie[2]
                ]
                if( !cookie[1] ) {
                    continue
                }
                cookieObjects[cookie[0]] = {name: cookie[0], value: decodeURIComponent(cookie[1])}
            }
            this.each(function (existingModel) {
                if( !cookieObjects[existingModel].id ) {
                    existingModel.destroy()
                }
            })
            _.each(cookieObjects, function (potentialModel) {
                if( this.get(potentialModel.name) ) {
                    this.get(potentialModel.name).set(potentialModel)
                } else {
                    this.add(potentialModel)
                }
            }, this)
        }

    ,   fetch: function () {
            this._readCookies()
        }

    }))


    // Helper function param
    //
    // Create a serialized representation of an array or object,
    // suitable for use in a URL query string or Ajax request.
    //
    // Usage:
    //
    // > BBNS.param( obj [, traditional ] )
    //
    // Arguments:
    //
    //  obj - (Array, Object) An array or object to serialize.
    //  traditional - (Boolean) A Boolean indicating whether to perform a traditional "shallow" serialization.
    //
    // Returns:
    //
    //  (String) An string representing the serialized object.

    var param = BBNS.param = $.param


    // Helper function deparam
    //
    // Deserialize a params string into an object, optionally coercing numbers,
    // booleans, null and undefined values; this method is the counterpart to the
    // internal jQuery.param method.
    //
    // Usage:
    //
    // > BBNS.deparam( params [, coerce ] );
    //
    // Arguments:
    //
    //  params - (String) A params string to be parsed.
    //  coerce - (Boolean) If true, coerces any numbers or true, false, null, and
    //    undefined to their actual value. Defaults to false if omitted.
    //
    // Returns:
    //
    //  (Object) An object representing the deserialized params string.

    var deparam = BBNS.deparam = function(params, coerce) {
        var obj = {}
        ,   coerce_types = { 'true': !0, 'false': !1, 'null': null }

        // Iterate over all name=value pairs.
        _.each( params.replace( /\+/g, ' ' ).split( '&' ), function(v){
            var param = v.split( '=' )
            ,   key = decodeURIComponent( param[0] )
            ,   val
            ,   cur = obj
            ,   i = 0

            // If key is more complex than 'foo', like 'a[]' or 'a[b][c]', split it
            // into its component parts.
            ,   keys = key.split( '][' )
            ,   keys_last = keys.length - 1

            // If the first keys part contains [ and the last ends with ], then []
            // are correctly balanced.
            if ( /\[/.test( keys[0] ) && /\]$/.test( keys[ keys_last ] ) ) {
                // Remove the trailing ] from the last keys part.
                keys[ keys_last ] = keys[ keys_last ].replace( /\]$/, '' )

                // Split first keys part into two parts on the [ and add them back onto
                // the beginning of the keys array.
                keys = keys.shift().split('[').concat( keys )

                keys_last = keys.length - 1
            } else {
                // Basic 'foo' style key.
                keys_last = 0
            }

            // Are we dealing with a name=value pair, or just a name?
            if ( param.length === 2 ) {
                val = decodeURIComponent( param[1] )

                // Coerce values.
                if ( coerce ) {
                    val = val && !isNaN(val)                ? +val              // number
                        : val === 'undefined'               ? undefined         // undefined
                        : !_.isUndefined(coerce_types[val]) ? coerce_types[val] // true, false, null
                        : val                                                   // string
                }

                if ( keys_last ) {
                    // Complex key, build deep object structure based on a few rules:
                    // * The 'cur' pointer starts at the object top-level.
                    // * [] = array push (n is set to array length), [n] = array if n is
                    //   numeric, otherwise object.
                    // * If at the last keys part, set the value.
                    // * For each keys part, if the current level is undefined create an
                    //   object or array based on the type of the next keys part.
                    // * Move the 'cur' pointer to the next level.
                    // * Rinse & repeat.
                    for ( ; i <= keys_last; i++ ) {
                        key = keys[i] === '' ? cur.length : keys[i]
                        cur = cur[key] = i < keys_last
                            ? cur[key] || ( keys[i+1] && isNaN( keys[i+1] ) ? {} : [] )
                            : val
                    }

                } else {
                    // Simple key, even simpler rules, since only scalars and shallow
                    // arrays are allowed.

                    if ( _.isArray( obj[key] ) ) {
                        // val is already an array, so push on the next value.
                        obj[key].push( val )

                    } else if ( !_.isUndefined(obj[key]) ) {
                        // val isn't an array, but since a second value has been specified,
                        // convert val into an array.
                        obj[key] = [ obj[key], val ]

                    } else {
                        // val is a scalar.
                        obj[key] = val
                    }
                }

            } else if ( key ) {
                // No value was defined, so set something meaningful.
                obj[key] = coerce ? undefined : ''
            }
        })

        return obj
    }

    //  Extend Backbones routing mechanism to be able to maps each route to a multiple callbacks

    var _loadUrl = Backbone.History.prototype.loadUrl

    _.extend(Backbone.History.prototype, {

        loadUrl: function(fragmentOverride) {
            var fragment = this.fragment = this.getFragment(fragmentOverride)
            ,   context = { matched: false }
            _.any(this.handlers, function(handler) {
                if (handler.route.test(fragment)) {
                    this.matched = true
                    var result = handler.callback(fragment)
                    return !_.isBoolean(result) || result
                }
            }, context)
            return context.matched
        }
    })

    //  Let's create a Backbone router class here.
    BBNS.Router = (function() {

        var Router = function() {
            var result = Backbone.Router.prototype.constructor.apply(this, arguments)
            BBNS.app.events.t('router:init:end', this)
            return result
        }

        _.extend(Router.prototype, Backbone.Router.prototype, {

            // Initialize is an empty function by default. Override it with your own
            // initialization logic.
            initialize: function() {
                return BBNS.log('Router initializing ', this)
            }

            // Manually bind a single named route to a callback. For example:
            //
            //     this.route('search/:query/p:num', 'search', function(query, num) {
            //       ...
            //     });
            //
            //    if callback return false Backbone.history.loadUrl pass route test
            //
        ,   route: function(route, name, callback) {
                if (!_.isRegExp(route)) route = this._routeToRegExp(route)
                if (_.isFunction(name)) {
                    callback = name
                    name = ''
                }
                if (!callback) callback = this[name]
                var router = this
                Backbone.history.route(route, function(fragment) {
                    var args = router._extractParameters(route, fragment)
                    ,   result
                    callback && (result = callback.apply(router, args))
                    router.trigger.apply(router, ['route:' + name].concat(args))
                    router.trigger('route', name, args)
                    Backbone.history.trigger('route', router, name, args)
                    return result
                })
                return this
            }

        ,   paramsNamespace: ''

        ,   reParams: function() {
                return new RegExp('^(.*?)~' + this.paramsNamespace + '\\/([^~]*)(.*)$')
            }

        ,   getState: function(options) {
                var settings = _.extend({
                        coerce: false
                    }, options)
                ,   fragment = Backbone.history.getFragment()
                ,   matches

                // matches[1] = fragment, not including trailing ~[^\/]*/
                // matches[2] = params, not including leading ~[^\/]*/
                matches = fragment.match(this.reParams())
                return ( matches ) ? deparam(matches[2], settings.coerce) : {}
            }

            // Adds a 'state' into the browser history.
            //
            // If no arguments are passed, an empty state is created,
            // which is just a shortcut for pushState( {}, { mergeMode: 2 } )
            //
            // Usage:
            //
            // > router.pushState( [ params [, options ] ] )
            //
            // Arguments:
            //  params - (Object) A params object to merge into location.hash.
            //
            //  options.mergeMode - (Number) Merge behavior defaults to 0, and is as-follows:
            //    specified (unless a hash string beginning with # is specified, in which
            //    case merge behavior defaults to 2), and is as-follows:
            //
            //    * 0: params in the params argument will override any params in the
            //         current state.
            //    * 1: any params in the current state will override params in the params
            //         argument.
            //    * 2: params argument will completely replace current state.
            //
            //  options.traditional - (Boolean) A Boolean indicating whether to perform a
            //      traditional "shallow" serialization
            //
            // Returns:
            //
            //  'true' if state changed
            //
        ,   pushState: function(params, options) {
                var settings = _.extend({
                        traditional: false
                    ,   mergeMode: !params ? 2 : 0
                    }, options)
                ,   fragment = Backbone.history.getFragment()
                ,   matches
                ,   currentParams
                ,   newParams
                ,   paramsStr
                ,   changed = false
                ,   tail = ''

                params || (params = {})

                matches = fragment.match(this.reParams())
                if ( matches ) {
                    fragment = matches[1]
                    currentParams = deparam(matches[2], true)
                    tail = matches[3]
                } else {
                    currentParams = {}
                }

                switch (settings.mergeMode) {
                    case 0:
                        newParams = _.extend({}, currentParams, params)
                        break
                    case 1:
                        newParams = _.extend({}, params, currentParams)
                        break
                    default:
                        newParams = params
                }
                if ( !_.isEqual(currentParams, newParams) ) {
                    paramsStr = BBNS.param(newParams, settings.traditional)
                    this.navigate(
                        ((paramsStr.length) ? fragment + '~' + this.paramsNamespace + '/' + paramsStr : fragment) + tail,
                        options)
                    changed = true
                }
                return changed
            }

            // Remove one or more keys from the current browser history 'state', creating
            // a new state.
            //
            // If no arguments are passed, an empty state is created, which is just a
            // shortcut for pushState( {}, { mergeMode: 2 } ).
            //
            // Usage:
            //
            // > router.removeState( [ key [, key ... ] ] )
            //
            // Arguments:
            //
            //  key - (String) One or more key values to remove from the current state,
            //    passed as individual arguments.
            //  key - (Array) A single array argument that contains a list of key values
            //    to remove from the current state.
            //
            // Returns:
            //
            //  'true' if state changed
            //
        ,   removeState: function( arr ) {
                var state = {}
                // If one or more arguments is passed..
                if ( !_.isUndefined(arr) ) {
                    // Get the current state.
                    state = this.getState()
                    // For each passed key, delete the corresponding property from the current
                    // state.
                    _.each( _.isArray( arr ) ? arr : slice.call(arguments), function(v){
                        delete state[v]
                    })
                }
                // Set the state, completely overriding any existing state.
                return this.pushState(state, { mergeMode: 2 })
            }

        })

        return Router

    })()

    BBNS.Router.extend = extend


    //  A class which we'll extend with the Backbone's events and then use as our app-wide dispatcher.
    BBNS.Events = {
        //  The t method is a shorthand for the usual Backbone.Events trigger method,
        //  but this one logs triggered events.
        t: function(eventName, options) {
            if (options == null) {
                options = {}
            }
            BBNS.log(6, "EVENT Triggered '" + eventName + "'", options)
            return this.trigger(eventName, options)
        }
    }

    //  Module class.
    BBNS.Module = (function() {

        var Module = function(options) {
            var args = slice.call(arguments)
            if ( options ) {
                if ( options.name ) this.name = options.name
                if ( options.uses ) this.uses = _.union(this.uses, options.uses)
                if ( options.models ) this.models = _.extend({}, this.models, options.models)
                if ( options.collections ) this.collections = _.extend({}, this.collections, options.collections)
                if ( options.routers ) this.routers = _.extend({}, this.routers, options.routers)
                if ( options.views ) this.views = _.extend({}, this.views, options.views)
            }
            if ( !_.isString(this.name) ) {
                BBNS.error('Module name must be a string')
            }
            if ( _.has(BBNS.app.modules, this.name) ) {
                BBNS.error('Module "' + this.name + '" already exists')
            }
            BBNS.app.modules[this.name] = this

            this.on('init:end', function() {
                return BBNS.app.events.t('module:init:end', this)
            }, this)

            this.on('init:start', function() {
                BBNS.app.events.t('module:init:start', this)
                this.initialize.apply(this, args)
                this.loaded = true
                return this.trigger('init:end')
            }, this)

            this.on('preinit:end', function() {
                return BBNS.app.events.t('module:preinit:end', this)
            }, this)

            this.preinitialize.apply(this, args)
            this.trigger('preinit:end')
        }

        _.extend(Module.prototype, Backbone.Events, {

            name: null

            // Required modules list
        ,   uses: []

            // Models
        ,   models: {}

            // Collections
        ,   collections: {}

            // Routers
        ,   routers: {}

            // Views
        ,   views: {}

            // Call at the beginning of the module initialization sequence.
        ,   preinitialize: function(){}

            // Defer initialization until doc ready and all uses modules are loaded.
            // Initialize is an empty function by default. Override it with your own
            // initialization logic.
        ,   initialize: function(){}


        })

        return Module

    })()

    BBNS.Module.extend = extend


    //  Sample master class called 'App' that holds everything together.
    BBNS.App = (function() {

        var App = function() {}

        _.extend(App.prototype, {

            //  Debug levels.
            debug: 0

            // Use Backbone's events in your master class.
        ,   events: _.extend(BBNS.Events, Backbone.Events)

            //  App modules
        ,   modules: {}

            //  DOM dependent init.
        ,   init: function() {
                BBNS.log('App init')
                this.events.t('init:start')
                this.events.once('dom:onload', function() {
                    BBNS.log('DOM loaded, proceeding')
                    this.domExists = true
                    this.events.t('init:dom:start')
                    this.loadModules()
                    if ( this.hasRouters ) {
                        this.events.t('router:history:start')
                    }
                    return this.events.t('init:dom:end')
                }, this)
                this.events.once('router:init:end', function() {
                    this.hasRouters = true
                }, this)
                return this.events.once('init:dom:end', function() {
                    return this.events.t('init:end')
                }, this)

            }

        ,   loadModules: function() {
                var toLoad = _.filter(this.modules, function(module) {
                        return !module.loaded
                    }, this)
                while ( toLoad.length ) {
                    var skipped = []
                    _.each(toLoad, function(module) {
                        if ( !_.find(module.uses, function(name) {
                                if ( !_.has(this.modules, name) ) {
                                    return BBNS.error('Module "' + name + '" is undefined')
                                }
                                return !this.modules[name].loaded
                            }, this) ) {
                            module.trigger('init:start')
                        } else {
                            skipped.push(module)
                        }
                    }, this)
                    if ( skipped.length == toLoad.length ) {
                        return BBNS.error("Can't load modules")
                    } else {
                        toLoad = skipped
                    }
                }
            }

        })
        return App

    })()


    var app = BBNS.app = new BBNS.App

    app.isTouch = 'ontouchstart' in document.documentElement

    app.events.once('router:history:start', function() {
        BBNS.log('Start the hash change handling')
        return Backbone.history.start({
            pushState: false
        })
    }, app)

    app.events.once('init:end', function() {
        BBNS.log('App init complete ', this)
    }, app)

    app.events.on('module:init:start', function(module) {
        BBNS.info('Module "' + module.name + '" initializing')
    }, app)

    app.init()


    $(function() {
        return BBNS.app.events.t('dom:onload')
    })


})(jQuery, Backbone, _);
