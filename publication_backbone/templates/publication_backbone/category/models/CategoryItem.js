(function($, Backbone, _) {

    "use strict";

    // Category Item Model
    // ----------

    var CategoryItem = Backbone.Model.extend({

        defaults: {
            children_ids: []
        ,   status: null
        ,   short_description: null
        ,   description: null
        ,   currentState: 'ex-state-closed'
        }

    ,   idAttribute: "id"

    ,   server_api: {
            "format": "json"
        }

    ,   url: function() {
            var url = this.get('resource_uri')
            if ( !url ) {
                url = this.urlRoot
                if ( url && this.has( 'id' ) ) {
                    url = url + this.get( 'id' ) + '/'
                }
            }
            return url || null
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

    ,   getParent: function() {
            if ( _.isUndefined(this._parentCache) ) {
                var parent_id = this.get('parent_id')
                if (this.has('id') && this.collection) {
                    this._parentCache = parent_id ? this.collection.get(parent_id) : this.collection.getRoot()
                }
            }
            return this._parentCache
        }

    ,   getParents: function() {
            var parent
            if ( this.get('parent_id') && (parent = this.getParent()) ){
                var parents = parent.getParents()
                parents.push(parent)
                return parents
            } else {
                return []
            }
        }

    ,   getChildren: function() {
            if ( _.isUndefined(this._childrenCache) ) {
                var children_ids = this.get('children_ids') || []
                ,   children = []
                if (this.collection) {
                    for (var key in children_ids) {
                        var child = this.collection.get(children_ids[key])
                        if (child) {
                            children.push(child)
                            if ( _.isUndefined(child._parentCache) ) {
                                child._parentCache = this
                            }
                        }
                    }
                }
                this._childrenCache = children
            }
            return this._childrenCache
        }

    ,   getLevel: function() {
            if ( _.isUndefined(this._levelCache) ) {
                var parent = this.getParent()
                this._levelCache = (parent) ? parent.getLevel() + 1 : 0
            }
            return this._levelCache
        }

    ,   getJSON: function() {
            if ( !this._jsonCache ) {
                this._jsonCache = this.toJSON()
            }
            return this._jsonCache
        }

    ,   set: function(key, value, options) {
            this._jsonCache = null
            var attrs
            ,   settings = {
                    cascadeUpdateSelected: false
                ,   doFetch: true
                }
            ,   status
            ,   isStatusChange = false
            ,   isReselected = false
            if (_.isObject(key) || key == null) {
                attrs = key
                settings = _.extend(settings, value)
            } else {
                attrs = {}
                attrs[key] = value
                settings = _.extend(settings, options)
            }

            // only local description & currentState after sync
            if ( settings.parse && settings.merge ) {
                attrs.description = this.get('description') || this.defaults.description
                attrs.currentState = this.get('currentState') || this.defaults.currentState
                if ( !_.has(attrs, 'children_ids') ) {
                    attrs.children_ids =  this.defaults.children_ids
                }
                if ( !_.has(attrs, 'status') ) {
                    attrs.status =  this.defaults.status
                }
            } else {
                // status
                if ( _.has(attrs, 'status') ){
                    var oldStatus = this.get('status')
                    status = attrs['status']
                    isStatusChange = this.has('id') && (status != oldStatus)
                    isReselected = (status == 'selected') && (status == oldStatus)
                }
                if ( isStatusChange ) {
                    var cuSettings = _.extend({}, settings, {cascadeUpdateSelected: true})
                    ,   parent = this.getParent()
                    if ( !settings.cascadeUpdateSelected ) {
                        delete this.collection._selectedCache
                        if ( !settings.silent ) {
                            this.collection.trigger('collection:startCascadeUpdate:selected', this, settings)
                        }
                    }
                    if ( status ) {
                        if ( status == 'selected' ) {
                            var oldSelected = this.collection.getSelected()
                            this.collection._selectedCache = this
                            if ( oldSelected ) {
                                oldSelected.set({status: null}, cuSettings)
                            }
                        }
                        if ( parent ) {
                            parent.set({status: 'ancestor'}, cuSettings)
                        }
                    } else {
                        if ( parent ) {
                            parent.set({status: null}, cuSettings)
                        }
                    }


                }
                if ( isReselected ) {
                    this.collection.trigger('collection:reselected', this, settings)
                }
            }

            var result = Backbone.Model.prototype.set.call(this, key, value, options)

            if ( isStatusChange && !settings.cascadeUpdateSelected && !settings.silent ) {
                this.collection.trigger('collection:finishCascadeUpdate:selected', this, settings)
                if ( settings.doFetch && (!settings.parse || !settings.merge) ) {
                    this.collection.fetch({silent: true})
                }
            }

            return result
        }


    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoryItem"

    ,   models: {
            CategoryItem: CategoryItem
        }
    })

    var App = new Module()

})(jQuery, Backbone, _);
