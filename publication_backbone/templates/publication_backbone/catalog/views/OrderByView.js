(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'

    // The Order By View
    // ---------------
    var OrderByView = Backbone.StatefulView.extend({

        template: '#' + name_prefix + '-app-template'

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

    ,   events: {
            'click .ex-js-order-by': 'changeAlgorithm'
        ,   'click .ex-js-ignore': 'ignore'
        ,   'click .ex-js-dropdown-toggle': 'onToggle'
        }

    ,   initialize: function(options) {
            this.initializeTemplate()
            _.bindAll(this, 'outsideClickHandler')
            this.trigger('initialized')
            this.collection.on('reset update collection:change:order_by', this.render, this)
        }

    ,   render: function() {
            var orderBy = this.collection.getOrderingAlgorithm()
            ,   context = {
                    orderBy: orderBy ? orderBy.toJSON() : null
                ,   algorithms: this.collection.getOrderingAlgorithmsList().toJSON()
                }
            this.$el.html(this.template(context))
            return this
        }

    ,   remove: function() {
            this.trigger('outdate')
            return Backbone.View.prototype.remove.call(this)
        }

    ,   changeAlgorithm: function(e) {
            e.preventDefault()
            e.stopPropagation()
            var algorithm = $(e.currentTarget).data('algorithm')
            this.collection.setOrderingAlgorithm(this.collection.getOrderingAlgorithmsList().get(algorithm).toJSON())
            this.trigger('collapse')
        }

    ,   ignore: function() {
            return false
        }

    ,   outsideClickHandler: function(e) {
            this.trigger('collapse')
        }

    ,   onToggle: function() {
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
            if ( this.backdrop ) {
                $(this.backdrop).off('click', this.outsideClickHandler).remove()
                delete this.backdrop
            }
            $(document.body).off('click', this.outsideClickHandler)
        }

    ,   doExpand: function() {
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

        name: "OrderByView"

    ,   views: {
            OrderByView: OrderByView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);
