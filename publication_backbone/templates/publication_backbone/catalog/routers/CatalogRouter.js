(function($, Backbone, _) {

    "use strict";

    // The Catalog Router
    // --------------
    var CatalogRouter = BBNS.Router.extend({

        routes: {
            '*fragment': 'sync'
        }

    ,   rubricatorKey: 'rb'

    ,   categoryKey: 'ct'

    ,   offsetKey: 'offset'

    ,   limitKey: 'limit'

    ,   orderingAlgorithmKey: 'order_by'

    ,   groupKey: 'grp'

    ,   relationKey: 'rel'

    ,   subjectKey: 'subj'

    ,   defaults: {}

    ,   CatalogItems: null

    ,   initialize: function(options){
            // rubrics
            this.defaults[this.rubricatorKey] = this.CatalogItems.getRubrics()
            this.CatalogItems.on('collection:change:rubrics', function(rubrics_ids, target) {
                if ( target != this ) {
                    var params = {}
                    ,   offset = this.CatalogItems.getOffset()
                    ,   group_id = this.CatalogItems.getGroupId()
                    if ( offset != this.defaults[this.offsetKey] ) {
                        params[this.offsetKey] = offset
                    } else {
                        params[this.offsetKey] = []
                    }
                    if ( group_id != this.defaults[this.groupKey] ) {
                        params[this.groupKey] = group_id
                    } else {
                        params[this.groupKey] = []
                    }
                    if ( rubrics_ids != this.defaults[this.rubricatorKey] ) {
                        params[this.rubricatorKey] = rubrics_ids
                    } else {
                        params[this.rubricatorKey] = []
                    }
                    this.pushState(params)
                }
            }, this)

            // category
            this.defaults[this.categoryKey] = this.CatalogItems.getCategoryId()
            this.CatalogItems.on('collection:change:category', function(category_id, target) {
                if ( target != this ) {
                    var rubrics_ids = this.CatalogItems.getRubrics()
                    ,   offset = this.CatalogItems.getOffset()
                    ,   group_id = this.CatalogItems.getGroupId()
                    ,   relations_ids = this.CatalogItems.getRelationsIds()
                    ,   subjects_ids = this.CatalogItems.getSubjectsIds()
                    ,   params = {}
                    if ( rubrics_ids != this.defaults[this.rubricatorKey] ) {
                        params[this.rubricatorKey] = rubrics_ids
                    } else {
                        params[this.rubricatorKey] = []
                    }
                    if ( offset != this.defaults[this.offsetKey] ) {
                        params[this.offsetKey] = offset
                    } else {
                        params[this.offsetKey] = []
                    }
                    if ( group_id != this.defaults[this.groupKey] ) {
                        params[this.groupKey] = group_id
                    } else {
                        params[this.groupKey] = []
                    }
                    if ( relations_ids != this.defaults[this.relationKey] ) {
                        params[this.relationKey] = relations_ids.length ? relations_ids : ['']
                    } else {
                        params[this.relationKey] = []
                    }
                    if ( subjects_ids != this.defaults[this.subjectKey] ) {
                        params[this.subjectKey] = subjects_ids.length ? subjects_ids : ['']
                    } else {
                        params[this.subjectKey] = []
                    }
                    _.each(this.CatalogItems.getRanges(), function(range, key) {
                        var defaultRangeValue = this.defaults[key]
                        ,   value = range.value
                        if ( !_.isEqual(value, defaultRangeValue) ) {
                            params[key] = value || []
                        } else {
                            params[key] = []
                        }
                    }, this)
                    if ( category_id != this.defaults[this.categoryKey] ) {
                        params[this.categoryKey] = category_id
                    } else {
                        params[this.categoryKey] = []
                    }
                    this.pushState(params)
                }
            }, this)

            // limit
            this.defaults[this.limitKey] = this.CatalogItems.getLimit()
            this.CatalogItems.on('collection:change:limit', function(limit, target) {
                if ( target != this ) {
                    var params = {}
                    if ( limit != this.defaults[this.limitKey] ) {
                        params[this.limitKey] = limit
                        this.pushState(params)
                    } else {
                        this.removeState(this.limitKey)
                    }
                }
            }, this)

            // offset
            this.defaults[this.offsetKey] = this.CatalogItems.getOffset()
            this.CatalogItems.on('collection:change:offset', function(offset, target) {
                if ( target != this ) {
                    var params = {}
                    if ( offset != this.defaults[this.offsetKey] ) {
                        params[this.offsetKey] = offset
                        this.pushState(params)
                    } else {
                        this.removeState(this.offsetKey)
                    }
                }
            }, this)

            // ranges
            _.each(this.CatalogItems.getRanges(), function(range, key) {
                this.defaults[key] = range.value
            }, this)
            this.CatalogItems.on('collection:change:range:value', function(key, value, target) {
                if ( target != this ) {
                    var params = {}
                    ,   defaultRangeValue = this.defaults[key]
                    if ( !_.isEqual(value, defaultRangeValue) ) {
                        params[key] = value || []
                        this.pushState(params)
                    } else {
                        this.removeState(key)
                    }
                }
            }, this)

            // ordering algorithm
            this.defaults[this.orderingAlgorithmKey] = this.CatalogItems.getOrderingAlgorithmId()
            this.CatalogItems.on('collection:change:order_by', function(order_by_id, target) {
                if ( target != this ) {
                    var params = {}
                    if ( order_by_id != this.defaults[this.orderingAlgorithmKey] ) {
                        params[this.orderingAlgorithmKey] = order_by_id
                        this.pushState(params)
                    } else {
                        this.removeState(this.orderingAlgorithmKey)
                    }
                }
            }, this)

            // group
            this.defaults[this.groupKey] = this.CatalogItems.getGroupId()
            this.CatalogItems.on('collection:change:group', function(group_id, target) {
                if ( target != this ) {
                    var offset = this.CatalogItems.getOffset()
                    ,   params = {}
                    if ( offset != this.defaults[this.offsetKey] ) {
                        params[this.offsetKey] = offset
                    } else {
                        params[this.offsetKey] = []
                    }
                    if ( group_id != this.defaults[this.groupKey] ) {
                        params[this.groupKey] = group_id
                    } else {
                        params[this.groupKey] = []
                    }
                    this.pushState(params)
                }
            }, this)

            // relations
            this.defaults[this.relationKey] = this.CatalogItems.getRelationsIds()
            this.CatalogItems.on('collection:change:relations', function(relations_ids, target) {
                if ( target != this ) {
                    if ( relations_ids != this.defaults[this.relationKey] ) {
                        params[this.relationKey] = relations_ids.length ? relations_ids : ['']
                    } else {
                        params[this.relationKey] = []
                    }
                    this.pushState(params)
                }
            }, this)

            // subjects
            this.defaults[this.subjectKey] = this.CatalogItems.getSubjectsIds()
            this.CatalogItems.on('collection:change:subjects', function(subjects_ids, target) {
                if ( target != this ) {
                    if ( subjects_ids != this.defaults[this.subjectKey] ) {
                        params[this.subjectKey] = subjects_ids.length ? subjects_ids : ['']
                    } else {
                        params[this.subjectKey] = []
                    }
                    this.pushState(params)
                }
            }, this)

        }

    ,   sync: function() {
            var state = this.getState({coerce: true})
            ,   rubrics_ids = state[this.rubricatorKey]
            ,   category_id = _.has(state, this.categoryKey) ? state[this.categoryKey] || null : this.defaults[this.categoryKey]
            ,   limit = _.has(state, this.limitKey) ? state[this.limitKey] : this.defaults[this.limitKey]
            ,   offset = _.has(state, this.offsetKey) ? state[this.offsetKey] : this.defaults[this.offsetKey]
            ,   order_by_id = state[this.orderingAlgorithmKey] || this.defaults[this.orderingAlgorithmKey]
            ,   group_id = _.has(state, this.groupKey) ? state[this.groupKey] || null : this.defaults[this.groupKey]
            ,   relations_ids = _.has(state, this.relationKey) ? _.compact(state[this.relationKey]) : this.defaults[this.relationKey]
            ,   subjects_ids = _.map(
                    _.has(state, this.subjectKey) ? _.compact(state[this.subjectKey]) : this.defaults[this.subjectKey]
                ,   function(id){ return '' + id }
                )
            ,   changed
            ,   changedCategory
            ,   changedRubrics
            ,   changedLimit
            ,   changedOffset
            ,   changedOrderBy
            ,   changedGroup
            ,   changedRelations
            ,   changedSubjects

            if ( _.isUndefined(rubrics_ids) ) {
                if ( category_id == this.defaults[this.categoryKey] ) {
                    rubrics_ids = this.defaults[this.rubricatorKey]
                } else {
                    rubrics_ids = []
                }

            }

            // category
            changed = changedCategory = this.CatalogItems.setCategory({id: category_id}, {silent: true})
            // rubrics
            changed = (changedRubrics = this.CatalogItems.setRubrics(rubrics_ids, {silent: true})) || changed
            // limit
            changed = (changedLimit = this.CatalogItems.setLimit(limit, {silent: true})) || changed
            // order_by
            changed = (changedOrderBy = this.CatalogItems.setOrderingAlgorithm({id: order_by_id}, {silent: true})) || changed
            // group
            changed = (changedGroup = this.CatalogItems.setGroup({id: group_id}, {silent: true})) || changed
            // offset
            changed = (changedOffset = this.CatalogItems.goTo(offset, {silent: true})) || changed
            // relations
            changed = (changedRelations = this.CatalogItems.setRelations(
                _.map(relations_ids, function(id){ return this.get(id) || {id: id} }, this.CatalogItems.getRelations())
            ,   {silent: true})) || changed
            // subjects
            changed = (changedSubjects = this.CatalogItems.setSubjects(
                _.map(subjects_ids, function(id){ return this.get(id) || {id: id} }, this.CatalogItems.getSubjects())
            ,   {silent: true})) || changed

            // ranges
            _.each(this.CatalogItems.getRanges(), function(range, key) {
                var rangeValue = state[key]
                ,   changedRange
                if ( _.isUndefined(rangeValue) ) {
                    if ( category_id == this.defaults[this.categoryKey] ) {
                        rangeValue = this.defaults[key]
                    } else {
                        rangeValue = null
                    }
                }
                changed = (changedRange = this.CatalogItems.setRangeValue(key, rangeValue, {silent: true})) || changed
                if ( changedRange && rangeValue ) {
                    this.CatalogItems.trigger('collection:change:range:value', key, rangeValue, this)
                }
            }, this)

            if ( changed ) {
                if ( changedCategory ) {
                    this.CatalogItems.trigger('collection:change:category', category_id, this)
                } else if ( changedRubrics ) {
                    this.CatalogItems.trigger('collection:change:rubrics', rubrics_ids, this)
                } else if ( changedLimit ) {
                    this.CatalogItems.trigger('collection:change:limit', limit, this)
                } else if ( changedOffset ) {
                    this.CatalogItems.trigger('collection:change:offset', offset, this)
                } else if ( changedRelations ) {
                    this.CatalogItems.trigger('collection:change:relations', relations_ids, this)
                } else if ( changedSubjects ) {
                    this.CatalogItems.trigger('collection:change:subjects', subjects_ids, this)
                } else if ( changedGroup ) {
                    var group = this.CatalogItems.getGroup()
                    group.trigger('change:id', group, group_id)
                    group.trigger('change', group)
                    this.CatalogItems.trigger('collection:change:group', group_id, this)
                } else if ( changedOrderBy ) {
                    this.CatalogItems.trigger('collection:change:order_by', order_by_id, this)
                }
                this.CatalogItems.fetch({reset: changedOrderBy})
            }
            return false
        }

    })



    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CatalogRouter"

    ,   routers: {
            CatalogRouter: CatalogRouter
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);