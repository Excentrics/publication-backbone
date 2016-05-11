(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'
    ,   catalogKey = '{{ catalog_key }}'

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoriesTitleApplication"

    ,   preinitialize: function(options){

            var uses = [
                    catalogKey
                ,   'CategoriesTitleView'

            ]

            this.uses = _.union(this.uses, uses)
        }

    ,   setCategoryEvent: function(options){

            var cat = options.model.toJSON()

            this.collections[catalogKey + '_CatalogItems'].setCategory(cat)
        }

    ,   initialize: function(options){
            this.catalogKey = catalogKey
            // catalog app
            var catalogApp = BBNS.app.modules[catalogKey]
            ,   CategoryList = BBNS.app.modules['CategoryItemsList'].collections['CategoryItemsList']

            // set collection
            ,   CatalogItems = this.collections.CatalogItems = catalogApp.collections[catalogKey + '_CatalogItems']

            ,   CategoryItems = this.collections.CategoryItems = this.collections[catalogKey + "_CategoryItems"] = new CategoryList(options.categoryItems)

            //CategoryItems.reset(options.categoryItems)

            this.listenTo(CategoryItems, "setCategoryEvent", this.setCategoryEvent)
            //CategoryItems.on("setCategoryEvent", this.setCategoryEvent)

            // Create main module view **AppView**

            var AppView = BBNS.app.modules['CategoriesTitleView'].views['CategoriesTitleView'].extend({
                template: '#' + name_prefix + '-app-template'
            })

            this.views.app = new AppView({
                model: this
            ,   el: $(".js-" + name_prefix + "-" + catalogKey + "-app")
            }).render()

        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix + "_" + catalogKey
        ,   categoryItems: [{% for object in categories_list %}{% include category_template_name with object=object only %}{% if not forloop.last %}, {% endif %}{% endfor %}]
    })


})(jQuery, Backbone, _);
