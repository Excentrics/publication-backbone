(function($, Backbone, _) {

    "use strict";

    // Catalog Items Collection
    // ---------------

    var CatalogItemsList = Backbone.Collection.extend({

        // model: CatalogItem
        // groupModel: GroupItem
        // categoryModel: CategoryItem
        // orderingAlgorithmModel: OrderingAlgorithm
        // subjectModel: CatalogItem

        cacheTimeout: 60000

    ,   initialize: function() {
            this.meta = {}
            this.groupModel || ( this.groupModel = Backbone.Model )
            this._group = new this.groupModel
            this.categoryModel || ( this.categoryModel = Backbone.Model )
            this._category = new this.categoryModel

            this.subjectModel || ( this.subjectModel = Backbone.Model )
            this._subjects = new (Backbone.Collection.extend({
                model: this.subjectModel
            ,   set: function(models, options) { // todo: remove if Backbone.js higher 1.2.1 version
                    this.trigger('beforeUpdate', this, options)
                    var result = Backbone.Collection.prototype.set.call(this, models, options)
                    this.trigger('update', this, options)
                    return result
                }
            }))

            this.relationModel || ( this.relationModel = Backbone.Model )
            this._relations = new (Backbone.Collection.extend({
                model: this.relationModel
            ,   set: function(models, options) { // todo: remove if Backbone.js higher 1.2.1 version
                    this.trigger('beforeUpdate', this, options)
                    var result = Backbone.Collection.prototype.set.call(this, models, options)
                    this.trigger('update', this, options)
                    return result
                }
            }))

            this.orderingAlgorithmModel || ( this.orderingAlgorithmModel = Backbone.Model )
            this._orderingAlgorithm = new this.orderingAlgorithmModel
            this._orderingAlgorithmsList = new (Backbone.Collection.extend({
                model: this.orderingAlgorithmModel
            }))

            // fetch event dispatcher
            this._inFetching = 0
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

    ,   parse: function( data ) {
            if ( data ) {
                if ( data.meta ) {
                    this.meta = data.meta
                }
                if ( data.group ) {
                    this._group.set(data.group)
                } else {
                    this._group.clear()
                }
                if ( data.category ) {
                    this._category.set(data.category)
                } else {
                    this._category.clear()
                }
                if ( data.order_by ) {
                    this._orderingAlgorithm.set(data.order_by)
                } else {
                    this._orderingAlgorithm.clear()
                }
                if ( data.ordering_algorithms ) {
                    this._orderingAlgorithmsList.set(data.ordering_algorithms)
                } else {
                    this._orderingAlgorithmsList.reset()
                }
                if ( data.subjects ) {
                    this._subjects.set(data.subjects)
                } else {
                    this._subjects.reset()
                }
                if ( data.relations ) {
                    this._relations.set(data.relations)
                } else {
                    this._relations.reset()
                }
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

    //{% comment %},   urlRoot: "{% if path %}{% url product_list path=path %}{% else %}{% url product_list %}{% endif %}"{% endcomment %}

    ,   url: function() {
            var model = this.model
            ,   modelUrlRoot = model && model.prototype && model.prototype.urlRoot
            ,   url = this.urlRoot || modelUrlRoot
            ,   rubrics_ids = this.getRubrics()
            ,   category_id = this.getCategoryId()
            ,   subjects_ids = this.getSubjectsIds()
            ,   relations_ids = this.getRelationsIds()
            if ( !_.isNull(category_id) ) {
                url = modelUrlRoot + 'selected/' + category_id + '/'
            }
            if ( rubrics_ids && rubrics_ids.length ) {
                url += 'set/' + _.compact(rubrics_ids).join( ';' ) + '/'
            }
            if ( subjects_ids.length ) {
                url += 'subj/' + subjects_ids.join( ';' ) + '/'
            }
            if ( relations_ids.length ) {
                url += 'rel/' + relations_ids.join( ';' ) + '/'
            }
            return url || null
        }

    ,   server_api: function() {
            // ranges
            var result = this._getRanges()
            _.extend(result, {
                // offset
                'offset': function() { return this.getOffset() }

                // number of items to return per request
            ,   'limit': function() { return this.getLimit() }

                // orphans
            ,   'orphans': function() { return this.meta.orphans || 0 }

                // order by
            ,   'order_by': function() { return this.getOrderingAlgorithmId() }

                // group id
            ,   'group_id': function() { return this.getGroupId() }

                // format
            ,   'format': "json"

                // cache id
            ,   "cache_id": function() {
                    return Math.round(new Date().getTime() / this.cacheTimeout)
                }

            })
            return result
        }

    ,   getRanges: function(){
            return this.meta.ranges || {}
        }

    ,   _getRanges: function(){
            var result = {}
            ,   ranges = this.getRanges()
            _.each(ranges, function(r, k){
                if ( r.value ){
                    result[k] = r.value.join("%3B")
                }
            }, this)
            return result
        }

    ,   reset: function(models, options) {
            this.trigger('beforeReset', this, options)
            this._notifyOutdate()
            return Backbone.Collection.prototype.reset.call(this, models, options)
        }

    ,   comparator: function(model) {
            return model.get("is_main") == 'True' ? -500 + model.get("position") : model.get("position")
        }

    ,   set: function(models, options) { // todo: remove if Backbone.js higher 1.2.1 version
            this.trigger('beforeUpdate', this, options)
            var result = Backbone.Collection.prototype.set.call(this, models, options)
            this.trigger('update', this, options)
            return result
        }

    ,   fetch: _.throttle(Backbone.Collection.prototype.fetch, 500)

    ,   hasNext: function() {
            return this.meta.total_count &&
                    (this.meta.total_count > this.meta.offset + this.meta.limit + this.meta.orphans)
        }

    ,   hasPrevious: function() {
            return this.meta.total_count &&
                    (this.meta.offset > 0)
        }

    ,   nextPage: function(options) {
            this.meta.offset += this.meta.limit
            if (!options || !options.silent) {
                this.trigger('collection:change:offset', this.meta.offset, this)
                this.fetch()
            }
            return true
        }

    ,   previousPage: function(options) {
            this.meta.offset -= this.meta.limit
            if (!options || !options.silent) {
                this.trigger('collection:change:offset', this.meta.offset, this)
                this.fetch()
            }
            return true
        }

    ,   goTo: function(offset, options) {
            var changed = false
            if ( this.meta.offset != offset ) {
                changed = true
                this.meta.offset = offset
                if (!options || !options.silent) {
                    this.trigger('collection:change:offset', offset, this)
                    this.fetch()
                }
            }
            return changed
        }

    ,   gotoPage: function(page, options) {
            return this.goTo(this.meta.limit * (page - 1), options)
        }

    ,   getTotalCount: function() {
            return this.meta.total_count || 0
        }

    ,   getOffset: function() {
            return this.meta.offset || 0
        }

    ,   getLimit: function() {
            return this.meta.limit || 25
        }

    ,   setLimit: function(limit, options) {
            var changed = false
            if ( this.meta.limit != limit ) {
                changed = true
                this.meta.limit = limit
                if (!options || !options.silent) {
                    this.trigger('collection:change:limit', limit, this)
                    this.fetch()
                }
            }
            return changed
        }

    ,   getThumbnailWidth: function() {
            return this.meta.thumbnail_width || 200
        }

    ,   getThumbnailHeight: function() {
            return this.meta.thumbnail_height || 200
        }

    ,   getToday: function() {
            // todo: replace 0 by default
            return this.meta.today || 0
        }

    ,   getPotentialRubricIds: function() {
            return this.meta.potential_rubrics_ids || []
        }

    ,   getRealRubricIds: function() {
            return this.meta.real_rubrics_ids || []
        }

    ,   setRangeValue: function(key, value, options) {
            var changed = false
            if ( this.meta.ranges ) {
                var oldRangeValue = this.meta.ranges[key].value
                if ( !_.isEqual(value, oldRangeValue) ) {
                    changed = true
                    this.meta.ranges[key].value = value
                    if (!options || !options.silent) {
                        this.trigger('collection:change:range:value', key, value, this)
                        this.fetch()
                    }
                }
            }
            return changed
        }

    ,   getRangeValue: function(key) {
            return this.meta.ranges[key].value || null
        }

    ,   getRangeLimit: function(key) {
            return this.meta.ranges[key].limit || null
        }

    ,   getPageCount: function() {
            var numPages = 0
            if ( this.meta.total_count ) {
                numPages = Math.ceil(Math.max(1, this.meta.total_count - this.meta.orphans) / this.meta.limit)
            }
            return numPages
        }

    ,   getCurrentPage: function() {
            var currentPage = NaN
            if ( this.meta.total_count ) {
                currentPage = Math.floor(this.meta.offset / this.meta.limit) + 1
            }
            return currentPage
        }

    ,   _rubrics_ids: []

    ,   getRubrics: function() {
            return this._rubrics_ids
        }

    ,   setRubrics: function(ids, options) {
            ids || (ids = [])
            var changed = false
            if ( !_.isEqual(this._rubrics_ids, ids) ) {
                changed = true
                this._group.clear(options)
                this._rubrics_ids = ids
                if (!options || !options.silent) {
                    this.meta.offset = 0
                    this.trigger('collection:change:rubrics', ids, this)
                    this.fetch()
                }
            }
            return changed
        }

    ,   getCategoryId: function() {
            return this._category.has('id') ? this._category.get('id') : null
        }

    ,   setCategory: function(attributes, options) {
            attributes || (attributes = {})
            var changed = false
            ,   id = _.has(attributes, 'id') ? attributes.id : null
            if ( id != this.getCategoryId() ) {
                changed = true
                var settings = _.extend({
                    rubrics_ids: []
                }, options)
                this._rubrics_ids = settings.rubrics_ids
                _.each(this.getRanges(), function(r){
                    r.value = null
                }, this)
                this._group.clear(options)
                this._relations.reset(null, options)
                this._subjects.reset(null, options)
                if ( _.isNull(id) ) {
                    this._category.clear(options)
                } else {
                    this._category.set(attributes, options)
                }
                if ( !settings.silent ) {
                    this.meta.offset = 0
                    this.trigger('collection:change:category', id, this)
                    this.fetch()
                }
            } else {
                this._category.set(attributes, options)
            }
            return changed
        }

    ,   getCategory: function() {
            return this._category
        }

    ,   getSubjects: function() {
            return this._subjects
        }

    ,   getSubjectsIds: function() {
            return this._subjects.pluck('id')
        }

    ,   setSubjects: function(subjects, options) {
            subjects || (subjects = [])
            var changed = false
            ,   ids = _.pluck(subjects, 'id')
            ,   oldIds = this.getSubjectsIds()
            if ( ids.length != oldIds.length || ids.length != _.intersection(ids, oldIds).length ) {
                changed = true
                this._subjects.set(subjects, options)
                if ( !options || !options.silent ) {
                    this.trigger('collection:change:subjects', ids, this)
                    this.fetch()
                }
            }
            return changed
        }

    ,   getRelations: function() {
            return this._relations
        }

    ,   getRelationsIds: function() {
            return this._relations.pluck('id')
        }

    ,   setRelations: function(relations, options) {
            relations || (relations = [])
            var changed = false
            ,   ids = _.pluck(relations, 'id')
            ,   oldIds = this.getRelationsIds()
            if ( ids.length != oldIds.length || ids.length != _.intersection(ids, oldIds).length ) {
                changed = true
                this._relations.set(relations, options)
                if ( !options || !options.silent ) {
                    this.trigger('collection:change:relations', ids, this)
                    this.fetch()
                }
            }
            return changed
        }

    ,   getOrderingAlgorithmId: function() {
            return this._orderingAlgorithm.has('id') ? this._orderingAlgorithm.get('id') : null
        }

    ,   getOrderingAlgorithm: function() {
            return this._orderingAlgorithm
        }

    ,   setOrderingAlgorithm: function(attributes, options) {
            attributes || (attributes = {})
            var changed = false
            ,   id = _.has(attributes, 'id') ? attributes.id : null
            if ( id != this.getOrderingAlgorithmId() ) {
                changed = true
                if ( _.isNull(id) ) {
                    this._orderingAlgorithm.clear(options)
                } else {
                    this._orderingAlgorithm.set(attributes, options)
                }
                if ( !options || !options.silent ) {
                    this.trigger('collection:change:order_by', id, this)
                    this.fetch({reset: true})
                }
            } else {
                this._orderingAlgorithm.set(attributes, options)
            }
            return changed
        }

    ,   getOrderingAlgorithmsList: function() {
            return this._orderingAlgorithmsList
        }

    ,   getGroupId: function() {
            return this._group.has('id') ? this._group.get('id') : null
        }

    ,   getGroup: function() {
            return this._group
        }

    ,   setGroup: function(attributes, options) {
            attributes || (attributes = {})
            var changed = false
            ,   id = _.has(attributes, 'id') ? attributes.id : null
            if ( id != this.getGroupId() ) {
                changed = true
                if ( _.isNull(id) ) {
                    this._group.clear(options)
                } else {
                    this._group.set(attributes, options)
                }
                if ( !options || !options.silent ) {
                    this.meta.offset = 0
                    this.trigger('collection:change:group', id, this)
                    this.fetch()
                }
            } else {
                this._group.set(attributes, options)
            }
            return changed
        }

    ,   _notifyOutdate: function() {
            this.each(function(model) {
                model.trigger('outdate', model)
            })
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CatalogItemsList"

    ,   collections: {
            CatalogItemsList: CatalogItemsList
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);