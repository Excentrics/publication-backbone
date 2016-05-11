(function($, Backbone, _) {
    // Rubrics Collection
    // ---------------
       "use strict";

        function sortIter (num){
            return num
        }

        var RubricItemsList = Backbone.Collection.extend({

        //model: Rubric

        _rootCache: null

    ,   _inFetching: 0

    ,   initialize: function() {
            // External events sender
            this.on('collection:finishCascadeUpdate:tagged', function() {
                var tagged = this.getTagged()
                this.trigger('collection:change:tagged', tagged, this)
            }, this)

            // fetch event dispatcher
            this.on('request', function( model_or_collection ){
                if ( model_or_collection == this ){
                    this._inFetching++
                    if ( this._inFetching == 1 ) {
                        this.trigger('collection:fetch:start', this)
                    }
                }
            }, this)
            this.on('sync error', function( model_or_collection ){
                if ( model_or_collection == this ){
                    this._inFetching--
                    if ( !this._inFetching ) {
                        this.trigger('collection:fetch:stop', this)
                    }
                }
            }, this)
       }

    ,   server_api: {
            "format": "json"
        ,   "cache_id": function() {
                return Math.round(new Date().getTime())
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

    ,   isFetching: function() {
            return !!this._inFetching
        }

    ,   getTagged: function() {
            if ( _.isUndefined(this._taggedCache) ) {
                this._taggedCache = _.compact(_.map(
                    this.filter(function(rubric){ return rubric.get('tagged') })
                ,   function(model){ return model.get('id') }
                ))
            }
            return this._taggedCache
        }

    ,   setTagged: function(ids, options) {
            ids || (ids = [])
            var tagged = this.getTagged()
            ,   toSet = _.difference(ids, tagged)
            ,   toUnset = _.difference(tagged, ids)
            ,   model
            ,   changed = false
            if ( toSet.length || toUnset.length ) {
                this._taggedCache = ids
                changed = true
                if (!options || !options.silent) {
                    this.trigger('collection:startCascadeUpdate:tagged')
                    _.each(toUnset, function( id ){
                        model = this.get(id)
                        if ( model ) {
                            model.set({tagged: false}, {cascadeUpdateTagged: true})
                        }
                    }, this)
                    _.each(toSet, function( id ){
                        model = this.get(id)
                        if ( model ) {
                            model.set({tagged: true}, {cascadeUpdateTagged: true})
                        }
                    }, this)
                    this.trigger('collection:finishCascadeUpdate:tagged')
                    this.fetch()
                }
            }
            return changed
        }

    ,   _category_id: null

    ,   getCategoryId: function() {
            return this._category_id
        }

    ,   setCategoryId: function(id, options) {
            var changed = false
            if ( this._category_id != id ) {
                var settings = _.extend({
                    tagged_ids: []
                }, options)
                this._category_id = id
                changed = true
                this._taggedCache = settings.tagged_ids
                if ( !settings.silent ) {
                    this.trigger('collection:change:category', id, this)
                    this.fetch({reset: true})
                }
            }
            return changed
        }

    ,   _real_rubrics_ids: null
    ,   _potential_rubrics_ids: null

    ,   isPotentialTest: function(id) {
            var result
            if ( !_.isNull(this._potential_rubrics_ids) ) {
                result = _.indexOf(this._potential_rubrics_ids, id, true) != -1
            } else {
                result = null
            }
            return result
        }

    ,   isRealTest: function(id) {
            var result
            if ( !_.isNull(this._real_rubrics_ids) ) {
                result = _.indexOf(this._real_rubrics_ids, id, true) != -1
            } else {
                result = null
            }
            return result
        }

    ,   setSelectionAssistant: function(potential_rubrics_ids, real_rubrics_ids, options) {
            var changed = false
            if ( !_.isEqual(this._potential_rubrics_ids, potential_rubrics_ids) || !_.isEqual(this._real_rubrics_ids, real_rubrics_ids) ) {
                changed = true
                this._potential_rubrics_ids = _.isArray(potential_rubrics_ids) ? _.sortBy(potential_rubrics_ids, sortIter) : potential_rubrics_ids
                this._real_rubrics_ids = _.isArray(real_rubrics_ids) ? _.sortBy(real_rubrics_ids, sortIter) : real_rubrics_ids
                if (!options || !options.silent) {
                    if ( !this.isFetching() ) {
                        this.trigger('collection:startCascadeUpdate:is_potential_and_is_real')
                        this.forEach(function(model){
                            var id = model.get('id')
                            model.set({
                                is_potential: this.isPotentialTest(id)
                            ,   is_real: this.isRealTest(id)
                            })
                        }, this)
                        this.trigger('collection:finishCascadeUpdate:is_potential_and_is_real')
                    } else {
                        this.forEach(function(model){
                            var id = model.get('id')
                            model.set({
                                is_potential: this.isPotentialTest(id)
                            ,   is_real: this.isRealTest(id)
                            }, { silent: true })
                        }, this)
                    }
                }
            }

            return changed
        }

    // ---------------------------

    ,   url: function() {
            var model = this.model
            ,   modelUrlRoot = model && model.prototype && model.prototype.urlRoot
            ,   url = this.urlRoot || modelUrlRoot
            ,   tagged = this.getTagged()
            ,   category_id = this.getCategoryId()
            if ( !_.isNull(category_id) ) {
                url = modelUrlRoot + 'selected/' + category_id + '/'
            }
            if ( tagged && tagged.length ) {
                url += 'set/' + tagged.join( ';' ) + '/'
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
                    delete model._isChildrenTaggedCache
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
                this._rootCache = new this.model({}, {collection: this})
                this._rootCache.set({
                    'children_ids': _.map(this.where({'parent_id': null}), function( model ){
                        return model.get('id')
                    })
                ,   'has_extra': true
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

        name: "RubricItemsList"

    ,   collections: {
            RubricItemsList: RubricItemsList
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);