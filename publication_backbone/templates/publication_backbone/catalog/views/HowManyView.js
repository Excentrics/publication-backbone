(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'

    // The How Many View
    // ---------------
    var HowManyView = Backbone.StatefulView.extend({

        template: '#' + name_prefix + '-app-template'

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

    ,   pageRanges: [10, 20, 50, 100, 200] //[1, 2, 3, 5, 8, 13, 21, 34, 55]

    ,   events: {
            'click .js-howmany': 'changeCount'
        ,   'click .ex-js-ignore': 'ignore'
        ,   'click .js-dropdown-toggle': 'onToggle'
        }

    ,   initialize: function(options) {
            this.initializeTemplate()

            _.bindAll(this, 'outsideClickHandler')

            if (options && options.countPerPage){
                var count = options.countPerPage
                this.pageRanges = [count, count*2, count*5, count*10, count*20]
            }
            this.trigger('initialized')
            this.collection.on('reset update collection:change:limit', this.render, this)
        }

    ,   render: function() {
            var totalCount = this.collection.getTotalCount()
            ,   limit = this.collection.getLimit()
            ,   pageRanges = _.filter(this.pageRanges, function(n){
                    return n <= totalCount
                })

            pageRanges = _.sortBy(_.union(pageRanges, [limit]), function(n) {
                return n
            })
            var context = {
                    totalCount: totalCount
                ,   limit: limit
                ,   pageRanges: pageRanges
                }
            this.$el.html(this.template(context))
            return this
        }

    ,   remove: function() {
            this.trigger('outdate')
            return Backbone.View.prototype.remove.call(this)
        }

    ,   changeCount: function(e) {
            e.preventDefault()
            e.stopPropagation()
            var n = $(e.currentTarget).data('range')
            this.collection.setLimit(n)
            this.trigger('collapse')
        }

    ,   ignore: function() {
            return false
        }

    ,   outsideClickHandler: function(e) {
            this.trigger('collapse')
        }

    ,   onToggle: function(e) {
            if ( this.currentState.indexOf('ex-state-opened') == -1 ) {
                $(document.body).trigger('click')
                this.trigger('expand')
            } else {
                this.trigger('collapse')
            }
            return false
        }

    ,   states: {
            'ex-state-closed': {}
        ,   'ex-state-opened': {
                enter: ['doExpand']
            ,   leave: ['doCollapse']
            }
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: 'ex-state-closed'}
            }
        ,   'ex-state-closed': {
                'expand': {enterState: 'ex-state-opened'}
            }
        ,   'ex-state-opened': {
                'collapse': {enterState: 'ex-state-closed'}
            }
        ,   '*': {
                'outdate': {enterState: 'outdate'}
            }
        }

    ,   doCollapse: function() {
            // collapse
            if ( this.backdrop ) {
                $(this.backdrop).off('click', this.outsideClickHandler).remove()
                delete this.backdrop
            }
            $(document.body).off('click', this.outsideClickHandler)
        }

    ,   doExpand: function() {
            // expand
            if ( this.isMobile() ) {
                this.backdrop = $('<div class="ex-dropdown-backdrop"/>')
                .insertBefore(this.$el)
                .on('click', this.outsideClickHandler)
            }
            $(document.body).on('click', this.outsideClickHandler)
        }

    ,   isMobile: function(){
            return BBNS.app.isTouch || ( $(window).width() < 980 )
        }
    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "HowManyView"

    ,   views: {
            HowManyView: HowManyView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);
