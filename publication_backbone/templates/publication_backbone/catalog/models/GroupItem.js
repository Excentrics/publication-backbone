(function($, Backbone, _) {

    "use strict";

    // Group Item Model
    // ----------

    var GroupItem = Backbone.Model.extend({

        defaults: {
            short_characteristics: null
        ,   characteristics: null
        ,   short_marks: null
        ,   marks: null
        }

    ,   idAttribute: "id"

    ,   url: function() {
            var url = this.get('resource_uri')
            if ( !url ) {
                url = this.urlRoot
                if ( url && this.has( 'id' ) ) {
                    url = url + '-/' + this.get( 'id' ) + '/'
                }
            }
            return url || null
        }

    ,   server_api: {
            "format": "json"
        }

    ,   parse: function( data ) {
            return data && data.objects && ( _.isArray( data.objects ) ? data.objects[ 0 ] : data.objects ) || data
        }

    ,   sync: function( method, model, options ) {
            var self = this
            // Some values could be functions, let's make sure
            // to change their scope too and run them
            var queryAttributes = {}
            _.each(_.result(self, "server_api"), function(value, key){
                if( _.isFunction(value) ) {
                    value = _.bind(value, self)
                    value = value()
                }
                if ( !_.isNull(value) ) {
                    queryAttributes[key] = value
                }
            })
            // Allows the passing in of {data: {foo: 'bar'}} at request time to overwrite server_api defaults
            if ( options.data ){
                options.data = decodeURIComponent($.param(_.extend(queryAttributes, options.data)))
            } else {
                options.data = decodeURIComponent($.param(queryAttributes))
            }
            return Backbone.Model.prototype.sync.call(this, method, model, options)
        }

    ,   set: function(key, val, options) {
            this._jsonCache = null
            var attrs
            // Handle both `"key", value` and `{key: value}` -style arguments.
            if (typeof key === 'object') {
                attrs = key
                options = val
            } else {
                (attrs = {})[key] = val
            }
            options || (options = {})

            // only local description
            if ( options.parse && options.merge ) {
                attrs.characteristics = this.get('characteristics') || this.defaults.characteristics
                attrs.marks = this.get('marks') || this.defaults.marks
            }

            return Backbone.Model.prototype.set.call(this, key, val, options)
        }

    ,   getJSON: function() {
            if ( !this._jsonCache ) {
                this._jsonCache = this.toJSON()
            }
            return this._jsonCache
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "GroupItem"

    ,   models: {
            GroupItem: GroupItem
        }
    })

    var App = new Module()

})(jQuery, Backbone, _);