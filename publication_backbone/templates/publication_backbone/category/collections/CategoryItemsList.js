(function($, Backbone, _) {

    "use strict";

    // Category Items Collection
    // ---------------

    var CategoryItemsList = Backbone.Collection.extend({

        // model: CategoryItem

        _rootCache: null

    ,   cacheTimeout: 60000

    ,   initialize: function() {
            // External events sender
            this.on('collection:finishCascadeUpdate:selected', function(model, options) {
                var selected = this.getSelected()
                this.trigger('collection:change:selected', selected, options )
            }, this)
        }

    ,   server_api: {
            "format": "json"
        ,   "cache_id": function() {
                return Math.round(new Date().getTime() / this.cacheTimeout)
            }
        }

    ,   parse: function( data ) {
            if ( data && data.meta ) {
                this.meta = data.meta
            }
            return data && data.objects
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
            return Backbone.Collection.prototype.sync.call(this, method, model, options)
        }

    ,   getSelected: function() {
            if ( _.isUndefined(this._selectedCache) ) {
                this._selectedCache = this.find(function(model){
                    return model.get('status') == 'selected'
                }) || null
            }
            return this._selectedCache
        }

    ,   setSelected: function(attributes, options) {
            attributes || (attributes = {})
            var changed = false
            ,   id = _.has(attributes, 'id') ? attributes.id : null
            ,   oldSelected = this.getSelected()
            ,   oldSelectedId = oldSelected && oldSelected.get('id') || null
            if ( oldSelectedId != id ) {
                var selected = _.isNull(id) ? null : this.get(id) || this.add( new this.model(attributes) )
                if ( selected ) {
                    selected.set({status: 'selected'}, options)
                } else {
                    oldSelected.set({status: null}, options)
                }
                changed = true
            }
            return changed
        }

    ,   url: function() {
            var model = this.model
            ,   url = this.urlRoot || ( model && model.prototype && model.prototype.urlRoot )
            ,   selected = this.getSelected()
            if ( selected ) {
                url += 'selected/' + selected.get('id') + '/'
            }
            return url || null
        }

    ,   reset: function(models, options) {
            this.trigger('beforeReset', this, options)
            this._notifyOutdate()
            return Backbone.Collection.prototype.reset.call(this, models, options)
        }

    ,   set: function(models, options) {
            var result
            if ( options.parse ) {
                this.trigger('beforeUpdate', this, options)
                this._notifyOutdate()
                result = Backbone.Collection.prototype.set.call(this, models, options)
                this.each(function (model) {
                    delete model._childrenCache
                    delete model._parentCache
                    delete model._levelCache
                    model._jsonCache = null
                }, this)
                this.trigger('update', this, options)
            } else {
                result = Backbone.Collection.prototype.set.call(this, models, options)
            }
            return result
        }

    ,   fetch: _.throttle(Backbone.Collection.prototype.fetch, 500)

    ,   getRoot: function() {
            if ( !this._rootCache ) {
                this._rootCache = new this.model
                this._rootCache.collection = this
                this._rootCache.set({
                    'children_ids': _.map(this.where({'parent_id': null}), function( model ){
                        return model.get('id')
                    })
                })
            }
            return this._rootCache
        }

    ,   _notifyOutdate: function() {
            this.each(function (model) {
                model.trigger('outdate', model)
            })
            if ( this._rootCache ) {
                this._rootCache.trigger('outdate', this._rootCache)
                this._rootCache = null
            }
        }



    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoryItemsList"

    ,   collections: {
            CategoryItemsList: CategoryItemsList
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);