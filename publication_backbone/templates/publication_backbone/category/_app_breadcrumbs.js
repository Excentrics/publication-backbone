(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'
    ,   categoryKey = '{{ category_key }}'
    ,   catalogKey = '{{ catalog_key }}'

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "BreadcrumbsApplication"

    ,   preinitialize: function(options){
            var uses = [
                'BreadcrumbsView'
            ]

            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){
            // category app
            var categoriesApp = BBNS.app.modules[categoryKey]
            ,   CategoryItems
            // Create main module view **AppView**
            ,   AppView = BBNS.app.modules['BreadcrumbsView'].views['BreadcrumbsView']
            ,   appViewOptions = {
                   el: $("#" + name_prefix + "-app")
                }
            ,   catalogApp = BBNS.app.modules[catalogKey]

            this.once('categories:ready', function() {
                _.extend(appViewOptions, { collection: CategoryItems })
                if ( !_.isUndefined(catalogApp) ) {
                    var initWithCatalog = function() {
                        this.views.app = new AppView(_.extend(appViewOptions, { CatalogItems: catalogApp.collections[catalogKey + '_CatalogItems'] })).render()
                    }
                    if ( catalogApp.loaded ) {
                        initWithCatalog.call(this)
                    } else {
                        // if catalog not loaded defer view init
                        catalogApp.once('init:end', initWithCatalog, this)
                    }
                } else {
                    this.views.app = new AppView(appViewOptions).render()
                }
            }, this)
            if ( !_.isUndefined(categoriesApp) ) {
                var initWithCategories = function() {
                    // set collection
                    CategoryItems = this.collections.CategoryItems = categoriesApp.collections['CategoryItems']
                    this.trigger('categories:ready')
                }
                if ( categoriesApp.loaded ) {
                    initWithCategories.call(this)
                } else {
                    // if categories not loaded defer view init
                    categoriesApp.once('init:end', initWithCategories, this)
                }
            } else {
                CategoryItems = this.collections.CategoryItems = null
                this.trigger('categories:ready')
            }

        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix
    })


})(jQuery, Backbone, _);
