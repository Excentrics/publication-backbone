(function($, Backbone, _) {

    "use strict";

    // Catalog Item Model
    // ----------

    var CatalogItem = Backbone.Model.extend({

        defaults: {
            short_characteristics: null
        ,   characteristics: null
        ,   short_marks: null
        ,   marks: null
        ,   short_lead: null
        ,   lead: null
        ,   variants: 1
        }

    ,   cacheTimeout: 60000

    ,   initialize: function() {
            var attributes = {
                in_cart: _.isFunction(this.getInCart) ? this.getInCart() : null
            }
            this.set(attributes, {'silent': true})
        }

    ,   idAttribute: "id"

    //{% comment %},   urlRoot: "{% if path %}{% url publication_list path=path %}{% else %}{% url publication_list %}{% endif %}"{% endcomment %}

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
            // format
            "format": "json"

            // cache id
        ,   "cache_id": function() {
                return Math.round(new Date().getTime() / this.cacheTimeout)
            }
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
                attrs.lead = this.get('lead') || this.defaults.lead
                if ( !_.has(attrs, 'variants') ) {
                    attrs.variants =  this.defaults.variants
                }
            }

            return Backbone.Model.prototype.set.call(this, key, val, options)
        }

    ,   getJSON: function() {
            if ( !this._jsonCache ) {
                this._jsonCache = this.toJSON()
            }
            return this._jsonCache
        }

    ,   getInCart: null

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CatalogItem"

    ,   models: {
            CatalogItem: CatalogItem
        }
    })

    var App = new Module()

})(jQuery, Backbone, _);