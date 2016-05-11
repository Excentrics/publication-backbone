(function($, Backbone, _) {

    "use strict";

    // Ordering Algorithm Model
    // ----------

    var OrderingAlgorithm = Backbone.Model.extend({

        idAttribute: "id"

    ,   set: function(key, val, options) {
            this._jsonCache = null
            return Backbone.Model.prototype.set.call(this, key, val, options)
        }

    ,   getJSON: function() {
            if ( !this._jsonCache ) {
                this._jsonCache = this.toJSON()
            }
            return this._jsonCache
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "OrderingAlgorithm"

    ,   models: {
            OrderingAlgorithm: OrderingAlgorithm
        }
    })

    var App = new Module()

})(jQuery, Backbone, _);