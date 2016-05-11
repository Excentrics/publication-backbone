
(function($, Backbone, _) {

    "use strict";


    function isTagged( model ) {
        return model.get('tagged')
    }

    // Rubric Item Model
    // ----------

    var RubricItem = Backbone.Model.extend({

        defaults: {
            tagged: false
            // Method must be "hierarchy", "facet" or "determinant"
        ,   method: "determinant"
        ,   branch: false
        ,   trunk: false
        ,   has_extra: false
        ,   children_ids: []
        ,   short_description: null
        ,   tags: null
        ,   description: null
        ,   currentState: 'ex-state-default'
        //,   is_potential: null
        //,   is_real: null
        }

    ,   idAttribute: "id"

    //{% comment %},   urlRoot: "{{ root.rubric.get_absolute_endpoint_url }}"{% endcomment %}

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
                if ( this.collection && this.get('resource_uri') ) {
                    this._parentCache = parent_id ? this.collection.get(parent_id) : this.collection.getRoot()
                }
            }
            return this._parentCache
        }

    ,   getChildren: function() {
            if ( _.isUndefined(this._childrenCache) ) {
                var children_ids = this.get('children_ids') || []
                ,   children = []
                if ( this.collection ) {
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

    ,   getSiblings: function() {
            var parent = this.getParent()
            return (parent) ? _.filter(
                    parent.getChildren(), function( model ){ return model.get('id') != this.get('id') }, this) : null
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

    ,   isChildrenTagged: function() {
            if ( _.isUndefined(this._isChildrenTaggedCache) ) {
                var children = this.getChildren()
                this._isChildrenTaggedCache = this.get('method') == 'determinant' ?
                    _.find(children, function( model ) {
                        return model.get('tagged') && _.find(model.getChildren(), isTagged, this)
                    }, this) :
                    _.find(children, isTagged, this)
            }
            return this._isChildrenTaggedCache
        }

    ,   set: function(key, value, options) {
            this._jsonCache = null
            var attrs
            ,   settings = {
                    cascadeUpdateTagged: false
                }
            ,   tagged
            ,   isTaggedChange = false
            ,   parent
            if (_.isObject(key) || key == null) {
                attrs = key
                settings = _.extend(settings, value)
            } else {
                attrs = {}
                attrs[key] = value
                settings = _.extend(settings, options)
            }
            // is potetial & is real tests for new models
            if ( !_.isUndefined(attrs.id) ) {
                attrs.is_potential = this.collection.isPotentialTest(attrs.id)
                attrs.is_real = this.collection.isRealTest(attrs.id)
            }
            // only local description & currentState after sync
            if ( settings.parse && settings.merge ) {
                attrs.description = this.get('description') || this.defaults.description
                attrs.currentState = this.get('currentState') || this.defaults.currentState
                if ( !_.has(attrs, 'trunk') ) {
                    attrs.trunk =  this.defaults.trunk
                }
                if ( !_.has(attrs, 'branch') ) {
                    attrs.branch =  this.defaults.branch
                }
                if ( !_.has(attrs, 'has_extra') ) {
                    attrs.has_extra =  this.defaults.has_extra
                }
                if ( !_.has(attrs, 'children_ids') ) {
                    attrs.children_ids =  this.defaults.children_ids
                }
                if ( !_.has(attrs, 'tagged') ) {
                    attrs.tagged =  this.defaults.tagged
                }
                if ( !_.has(attrs, 'tags') ) {
                    attrs.tags =  this.defaults.tags
                }
            } else {
                // tagged
                if ( _.has(attrs, 'tagged') ){
                    var oldTagged = this.get('tagged')
                    tagged = attrs['tagged']
                    isTaggedChange = (parent = this.getParent()) && (tagged != oldTagged)
                }
                if ( isTaggedChange ) {
                    var cuSettings = _.extend({}, settings, {cascadeUpdateTagged: true})
                    if ( !settings.cascadeUpdateTagged ) {
                        delete this.collection._taggedCache
                        if ( !settings.silent ) {
                            this.collection.trigger('collection:startCascadeUpdate:tagged', this, settings)
                        }
                    }
                    if ( tagged ) {
                        if ( parent.get('method') == 'hierarchy' ) {
                            _.each(_.filter(this.getSiblings(), function( model ){ return model.get('tagged') }, this),
                                    function( model ){ model.set({tagged: false}, cuSettings) }
                            )
                        }
                        parent.set({tagged: true}, cuSettings)
                    } else {
                        _.each(this.getChildren(), function( model ){ model.set({tagged: false}, cuSettings) }, this)
                    }
                    delete parent._isChildrenTaggedCache
                    var grandparent = parent.getParent()
                    if ( grandparent && grandparent.get('method') == 'determinant' ) {
                        delete grandparent._isChildrenTaggedCache
                        grandparent.trigger('determinant:grandchildren:change:tagged', this)
                    }
                }
            }

            var result = Backbone.Model.prototype.set.call(this, key, value, options)
            if ( isTaggedChange && !settings.cascadeUpdateTagged && !settings.silent ) {
                this.collection.trigger('collection:finishCascadeUpdate:tagged', this, settings)
                if ( !settings.parse || !settings.merge ) {
                    this.collection.fetch({silent: true})
                }
            }
            return result
        }

    ,   toggle: function() {
            this.set({tagged: !this.get("tagged")})
        }

    ,   unsetChildren: function() {
            if ( this.collection ) {
                this.collection.trigger('collection:startCascadeUpdate:tagged', this)
                delete this.collection._taggedCache
                _.each(this.getChildren(), function( model ){
                    model.set({tagged: false}, {cascadeUpdateTagged: true})
                })
                this.collection.trigger('collection:finishCascadeUpdate:tagged', this)
                this.collection.fetch({silent: true})
            }
        }

    })



    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "RubricItem"

    ,   models: {
            RubricItem: RubricItem
        }
    })

    var App = new Module()

})(jQuery, Backbone, _);