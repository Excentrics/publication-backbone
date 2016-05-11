(function($, Backbone, _) {

    "use strict";

    // Create quick reference variables for speed access to core prototypes.
    var slice = [].slice

    // Nested View Model
    // ----------

    var NestedView = Backbone.Model.extend({

        idAttribute: "id"

    ,   defaults: {
            isShown: false
        }

    ,   initialize: function() {
            var view = this.get('view')
            view.model.on('remove', this.removeSelf, this)
            view.on('all', this.dispatchEventThrough, this)
            this.on('remove outdate', function() {
                var view = this.get('view')
                view.model.off('remove', this.removeSelf)
                view.off('all', this.dispatchEventThrough)
            }, this)
        }

    ,   removeSelf: function() {
            if (this.collection) {
                this.collection.remove(this)
            }
        }

    ,   dispatchEventThrough: function(event) {
            if (this.collection) {
                this.collection.trigger.apply(this.collection, [event].concat(this, slice.call(arguments, 1)) )
            }
        }

    ,   getIndex: function() {
            var model = this.get('view').model
            return model.collection ? model.collection.indexOf(model) : -1
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "NestedView"

    ,   models: {
            NestedView: NestedView
        }
    })

    var App = new Module()

})(jQuery, Backbone, _);