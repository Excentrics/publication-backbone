(function($, Backbone, _) {

    "use strict";

    // Range Model
    // ----------
    var RangeModel = Backbone.Model.extend({

        defaults: {
            value: null
        ,   limit: null
        }

    })

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "RangeModel"

    ,   models: {
            RangeModel: RangeModel
        }
    })

    var App = new Module()

})(jQuery, Backbone, _);