(function($, Backbone, _) {

    "use strict";

    // Category Menu View
    // ---------------

    // Our overall **AppView** is the top-level piece of UI.
    var CategoryMenuView = Backbone.StatefulView.extend({

        initialize: function(options) {
            this.CategoryMenuItemView = options.CategoryMenuItemView
            this.orientation = options.orientation // default "horizontal"

            var $details = this.$el.find('.ex-details')
            this.$details = $details.length ? $details : this.$el

            var elAttr = {
                'data-orientation': this.orientation
            }
            this.$el.attr(elAttr)

            this.collection.on('reset update', this.addAll, this)

            this.trigger('initialized')
            // this.collection.reset...
        }

    ,   addAll: function() {
            var view = new this.CategoryMenuItemView({
                    model: this.collection.getRoot()
                ,   childrenView: this.CategoryMenuItemView
                })
            view.setElement( this.$details ).render()
        }

    ,   states: {
            '': {}
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: ''}
            }
        }

    //,   debugStateMachine: true

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoryMenuView"

    ,   views: {
            CategoryMenuView: CategoryMenuView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);