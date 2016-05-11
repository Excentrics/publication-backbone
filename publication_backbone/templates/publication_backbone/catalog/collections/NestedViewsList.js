(function($, Backbone, _) {

    "use strict";

    // Nested Views Collection
    // ---------------

    var NestedViewsList = Backbone.Collection.extend({

        comparator: function(nestedView) {
            return nestedView.getIndex()
        }

    ,   reset: function(models, options) {
            this.trigger('beforeReset', this, options)
            this._notifyOutdate()
            return Backbone.Collection.prototype.reset.call(this, models, options)
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

        name: "NestedViewsList"

    ,   preinitialize: function(options){
            this.uses = _.union(this.uses, [
                'NestedView'
            ])
        }

    ,   initialize: function(options){
            var NestedView = BBNS.app.modules['NestedView'].models['NestedView']
            this.collections.NestedViewsList = NestedViewsList.extend({
                model: NestedView
            })
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);