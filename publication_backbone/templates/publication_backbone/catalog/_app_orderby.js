(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'
    ,   catalogKey = '{{ catalog_key }}'

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "OrderBy"

    ,   preinitialize: function(options){

            var uses = [
                    catalogKey
                ,   'OrderByView'
            ]

            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){
            // catalog app
            var catalogApp = BBNS.app.modules[catalogKey]
            // set collection
            ,   CatalogItems = this.collections.CatalogItems = catalogApp.collections[catalogKey + '_CatalogItems']
            ,   OrderByView = BBNS.app.modules['OrderByView'].views['OrderByView'].extend({
                    template: '#' + name_prefix + '-app-template'
                })

            this.views.orderBy = new OrderByView({
                collection: CatalogItems
            ,   el: $(".js-" + name_prefix + "-" + catalogKey + "-app")
            }).render()

        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix
    })


})(jQuery, Backbone, _);
