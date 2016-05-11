(function($, Backbone, _) {

    "use strict";

    var name_prefix = 'catalog_items'

    // Catalog Items View
    // ---------------

    // Our overall **AppView** is the top-level piece of UI.
    var CatalogItemsView = Backbone.StatefulView.extend({

        initialize: function(options) {
            this.CatalogItemView = options.CatalogItemView

            var $itemsList = this.$(this.selector)
            if ( $itemsList.length ) {
                this.$itemsList = $itemsList
                // duplicate state class
                this.on('transition', function(leaveState, enterState) {
                    this.$itemsList.removeClass(this._itemsListStateClassName || '')
                    this._itemsListStateClassName = (this.states[enterState].className || enterState)
                    this.$itemsList.addClass(this._itemsListStateClassName)
                }, this)
            } else {
                this.$itemsList = this.$el
            }

            this.itemsViews = new this.NestedViewsList

            this.itemsViews.on('showDescription', this.singletonShowDescription, this)

            this.collection.on('reset', this.addAll, this)
            this.collection.on("add", this.addOne, this)
            this.collection.on('update', this.mergeAll, this)

            this.collection.on('collection:fetch:start', function(){
                this.trigger('fetch:start')
            }, this)

            this.collection.on('collection:fetch:stop', function(){
                this.trigger('fetch:stop')
            }, this)

            this.trigger('initialized')
        }

    ,   selector: ".ex-js-" + name_prefix + "-list"

    ,   NestedViewsList: null

    ,   addOne: function(model, collection, options) {
            this.itemsViews.add([{
                id: model.get('id')
            ,   view: new this.CatalogItemView({model: model})
            }], {sort: false})
        }

    ,   addAll: function() {
            var nestedViews = this.collection.map(function(model) {
                return {
                    id: model.get('id')
                ,   view: new this.CatalogItemView({model: model})
                ,   isShown: true
                }
            }, this)
            this.itemsViews.reset(nestedViews)
            var views = this.itemsViews.map(function(model) {
                return model.get('view').render().el
            })
            this.$itemsList.append(views)
        }

    ,   mergeAll: function() {
            this.itemsViews.sort()
            var shown = this.itemsViews.filter(function(model){
                    return model.get('isShown')
                })
            ,   i = 0
            ,   j
            ,   n = this.itemsViews.length
            ,   range
            ,   views
            ,   prepareElement = function(index){
                    var model = this.itemsViews.at(index)
                    model.set('isShown', true)
                    return model.get('view').render().el
                }
            if ( shown.length < n ) {
                _.each(shown, function(model) {
                    j = model.getIndex()
                    range = _.range(i, j)
                    if ( range.length ) {
                        views = _.map(range, prepareElement, this)
                        model.get('view').$el.before(views)
                    }
                    i = j + 1
                }, this)
                range = _.range(i, n)
                if ( range.length ) {
                    views = _.map(range, prepareElement, this)
                    this.$itemsList.append(views)
                }
            }
        }

    ,   singletonShowDescription: function(model) {
            var currentView = model.get('view')
            this.itemsViews.map(function(model){
                var view = model.get('view')
                if ( (view.currentState.indexOf('description') != -1) && view != currentView ) {
                    view.trigger('hideDescription')
                }
            }, this)
        }

    ,   render: function(){
            return this
        }

    ,   states: {
            'ex-state-default': {}
        ,   'ex-state-loading': {
                leave: ['focusOnContent']
            }
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: 'ex-state-default'}
            }
        ,   'ex-state-default': {
                'fetch:start': {enterState: 'ex-state-loading'}
            }
        ,   'ex-state-loading': {
                'fetch:stop': {enterState: 'ex-state-default'}
            }
        }

    ,   focusOnContent: function(){
            var $window = $(window)
            ,   offset = this.$el.offset()
            ,   elTop = offset.top - $window.scrollTop()
            ,   screenHeight = $window.height()
            ,   elHeight = this.$el.height()
            if ( ( elTop < 0 && elTop < 0.667 * (screenHeight - elHeight) ) || elTop > screenHeight ) {
                var dY = Math.min(Math.round(0.25 * screenHeight), Math.abs(elTop))
                $("html, body").animate({ scrollTop: offset.top - dY }, "slow")
            }
        }
    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CatalogItemsView"

    ,   preinitialize: function(options){
            this.uses = _.union(this.uses, [
                'NestedViewsList'
            ])
        }

    ,   initialize: function(options){
            var NestedViewsList = BBNS.app.modules['NestedViewsList'].collections['NestedViewsList']
            this.views.CatalogItemsView = CatalogItemsView.extend({
                NestedViewsList: NestedViewsList
            })
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);