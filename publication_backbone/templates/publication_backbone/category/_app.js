{% with object_template_name='publication_backbone/category/_meta_object.json' category_template_name='publication_backbone/category/_object.json' %}

(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'
    ,   categoryUrlRoot = "{% url 'category_list' %}"
    ,   catalog_base_uri = "{% url 'publication_list' %}"
    ,   catalogKey = '{{ catalog_key }}'
    ,   menuOrientation = '{{ menu_orientation }}'

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoryApplication"

    ,   preinitialize: function(options){

            var uses = [
                'CategoryItem'
            ,   'CategoryItemsList'
            ,   'CategoryMenuItemView'
            ,   'CategoryMenuView'
            ]

            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){
            var CategoryItem = BBNS.app.modules['CategoryItem'].models['CategoryItem'].extend({
                    urlRoot: categoryUrlRoot
                })
            ,   CategoryItemsList = BBNS.app.modules['CategoryItemsList'].collections['CategoryItemsList'].extend({
                    model: CategoryItem
                ,   urlRoot: categoryUrlRoot
                })
            ,   CategoryItems = this.collections.CategoryItems = new CategoryItemsList

            CategoryItems.meta = {
                catalog_base_uri: catalog_base_uri
            }

            // CategoryMenuItemView
            var CategoryMenuItemView = BBNS.app.modules['CategoryMenuItemView'].views['CategoryMenuItemView'].extend({
                template: '#' + name_prefix + '-menu-item-template'
            })

            // Create main module view **AppView**
            var AppView = BBNS.app.modules['CategoryMenuView'].views['CategoryMenuView']
            this.views.app = new AppView({
                collection: CategoryItems

                // Instead of generating a new element, bind to the existing skeleton of
                // the App already present in the HTML.
            ,   el: $("#" + name_prefix + "-app")
            ,   orientation: menuOrientation
            ,   CategoryMenuItemView: CategoryMenuItemView
            })

            // Redirect to catalog location
            var catalogApp = BBNS.app.modules[catalogKey]
            ,   documentPath = this.getDocumentLocationPath()
            if ( _.isUndefined(catalogApp) ){
                CategoryItems.on('collection:change:selected collection:reselected', function(selected) {
                    if ( selected ){
                        if ( selected.get('class_name') == 'category' ) {
                            document.location.href = selected.get('catalog_resource_uri')
                        } else if ( selected.get('class_name') == 'categorylink' ) {
                            var href = selected.get('href')
                            if ( documentPath != href ) {
                                document.location.href = href
                            }
                        }
                    } else {
                        document.location.href = this.collections.CategoryItems.meta.catalog_base_uri
                    }
                }, this)
            } else {
                CategoryItems.on('collection:change:selected collection:reselected', function(selected) {
                    if ( selected && selected.get('class_name') == 'categorylink' ) {
                        document.location.href = selected.get('href')
                    }
                }, this)
            }

            // Run...
            var categoryItems = options && options.categoryItems || []
            CategoryItems.reset(categoryItems)

            {% if category %}
            CategoryItems.setSelected({% include category_template_name with object=category only %}, {silent: true})
            {% else %}
            var selected = CategoryItems.getSelected()
            if ( !selected ) {
                selected = CategoryItems.find( function( model ){
                    return model.get('class_name') == 'categorylink' && model.get('href') == documentPath
                }, this)
                if ( selected ) {
                    selected.set({status: 'selected'}, {doFetch: false})
                }
            }
            {% endif %}
        }

    ,   getDocumentLocationPath: function() {
            var href = window.location.href
            ,   host = window.location.host
            return href.substring(href.indexOf(host) + host.length)
        }

    })


    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix
    ,   categoryItems: [{% for object in object_list %}{% include object_template_name with object=object category=category only %}{% if not forloop.last %}, {% endif %}{% endfor %}]
    })


})(jQuery, Backbone, _);

{% endwith %}
