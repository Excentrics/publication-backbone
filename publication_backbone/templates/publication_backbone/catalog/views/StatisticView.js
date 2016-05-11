(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'

    // The Statistic View
    // ---------------
    var StatisticView = Backbone.StatefulView.extend({

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
            var totalCount = this.collection.getTotalCount()
            ,   pageCount = this.collection.getPageCount()
            ,   offset = this.collection.getOffset()
            ,   itemsCount = this.collection.length
            ,   context = {
                    totalCount: totalCount
                ,   pageCount: pageCount
                ,   offset: offset
                ,   itemsCount: itemsCount
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

        name: "StatisticView"

    ,   views: {
            StatisticView: StatisticView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);