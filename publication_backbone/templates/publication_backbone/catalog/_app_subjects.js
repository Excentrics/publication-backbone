(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'
    ,   catalogKey = '{{ catalog_key }}'

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "{% block module_name %}SubjectsApplication{% endblock %}"

    ,   preinitialize: function(options){

            var uses = [
                    catalogKey
                ,   'SubjectsView'
            ]

            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){
            // catalog app
            var catalogApp = BBNS.app.modules[catalogKey]
            // set collection
            ,   CatalogItems = this.collections.CatalogItems = catalogApp.collections[catalogKey + '_CatalogItems']

            // SubjectItemView
            var SubjectItemView = BBNS.app.modules['CatalogItemView'].views['CatalogItemView'].extend({
                template: '#' + name_prefix + '-item-template'
            })

            // Create main module view **AppView**
            var AppView = BBNS.app.modules['SubjectsView'].views['SubjectsView'].extend({
                selector: ".ex-js-" + name_prefix + "-list"
            })

            this.views.app = new AppView({
                collection: CatalogItems
            ,   el: $(".ex-js-" + name_prefix + "-" + catalogKey + "-app")
            ,   SubjectItemView: SubjectItemView
            }).render()

        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix + "_" + catalogKey
    })


})(jQuery, Backbone, _);
