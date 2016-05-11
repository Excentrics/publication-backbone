(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'
    ,   catalogKey = '{{ catalog_key }}'

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "PaginationApplication"

    ,   preinitialize: function(options){

            var uses = [
                    catalogKey
                ,   'PaginationView'

            ]

            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){
            // catalog app
            var catalogApp = BBNS.app.modules[catalogKey]

            // set collection
            ,   CatalogItems = this.collections.CatalogItems = catalogApp.collections[catalogKey + '_CatalogItems']

            var AppView = BBNS.app.modules['PaginationView'].views['PaginationView'].extend({
                template: '#' + name_prefix + '-app-template'
            })

            this.views.app = new AppView({
                collection: CatalogItems
            ,   el: $(".js-" + name_prefix + "-" + catalogKey + "-app")
            }).render()

        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix + "_" + catalogKey
    })


})(jQuery, Backbone, _);
