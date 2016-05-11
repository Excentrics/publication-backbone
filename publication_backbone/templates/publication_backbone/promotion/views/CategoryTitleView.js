(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'

    // The Category Title View
    // ---------------
    var CategoryTitleView = Backbone.StatefulView.extend({

        template: '#' + name_prefix + '-app-template'

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

    ,   initialize: function(options) {
            this.initializeTemplate()
            this.trigger('initialized')
            this.collection.on('reset update', this.render, this)
        }

    ,   render: function() {
            var category = this.collection.getCategory()
            ,   group = this.collection.getGroup()
            ,   subjects = this.collection.getSubjects()
            ,   relations = this.collection.getRelations()
            ,   orderingAlgorithm = this.collection.getOrderingAlgorithm()
            ,   context = {
                    category: category.get('id') ? category.toJSON() : null
                ,   group: group.get('id') ? group.toJSON() : null
                ,   subjects: _.filter(subjects.toJSON(), function(obj){ return _.has(obj, "resource_uri") })
                ,   relations: _.filter(relations.toJSON(), function(obj){ return _.has(obj, "resource_uri") })
                ,   orderingAlgorithm: orderingAlgorithm.get('id') ? orderingAlgorithm.toJSON() : null
                }
            this.$el.html(this.template(context))
            return this
        }

    ,   states: {
            '': {}
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: ''}
            }
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoryTitleView"

    ,   views: {
            CategoryTitleView: CategoryTitleView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);