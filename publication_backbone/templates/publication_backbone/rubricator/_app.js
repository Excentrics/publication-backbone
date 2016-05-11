{% load i18n beautiful_fields_tags publication_backbone_tags %}{% get_config as config %}{% with level=0 objects=''|make_list %}{% comment %}
{% endcomment %}{% with meta_tree_nodes_template_name='publication_backbone/rubricator/_meta_tree_nodes.json' object_template_name='publication_backbone/rubricator/_meta_tree_object.json' %}{% include meta_tree_nodes_template_name with rubrics=object_list tagged_rubrics=root.get_children_dict template_name=meta_tree_nodes_template_name level=level objects=objects rubrics_parent=root.rubric attrs=root.attrs only %}{% comment %}


{% endcomment %}

(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'
    ,   categoryKey = '{{ config.PUBLICATION_BACKBONE_CATEGORY_KEY }}'
    ,   rubricUrlRoot = "{{ root.rubric.get_absolute_endpoint_url }}"
    ,   rubricListUrlRoot = {% if category %}"{% url 'rubric_list' path=category.path %}"{% else %}rubricUrlRoot{% endif %}
    ,   rubricMethod = {% if root.rubric.get_classification_method %}"{{ root.rubric.get_classification_method }}"{% else %}null{% endif %}


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "Rubricator"

    ,   preinitialize: function(options){

            var uses = [
                'RubricItem'
            ,   'RubricItemsList'
            ,   'RubricItemView'
            ,   'RubricatorView'
            ]

            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){
            var Rubric = this.models.Rubric = BBNS.app.modules['RubricItem'].models['RubricItem'].extend({
                    urlRoot: rubricUrlRoot,
                    method: rubricMethod
                })
            ,   RubricItemsList = BBNS.app.modules['RubricItemsList'].collections['RubricItemsList'].extend({
                    model: Rubric,
                    urlRoot: rubricListUrlRoot
                })
            ,   Rubrics = this.collections.Rubrics = new RubricItemsList

            {% if category %}
            Rubrics.setCategoryId({{ category.id }}, {silent: true})
            {% endif %}

            // RubricItemView & AppView
            var RubricItemView = BBNS.app.modules['RubricItemView'].views['RubricItemView']
            ,   AppView = BBNS.app.modules['RubricatorView'].views['RubricatorView']
            this.views.app = new AppView({
                collection: Rubrics

                // Instead of generating a new element, bind to the existing skeleton of
                // the App already present in the HTML.
            ,   el: $("#" + name_prefix + "-app")
            ,   rubricItemView: RubricItemView
            })

            // if category app then listen category_app event 'category:change:selected'
            var categoryApp = BBNS.app.modules[categoryKey]
            if ( categoryApp ){
                var CategoryItems = categoryApp.collections.CategoryItems
                ,   defaultCategorySelected = CategoryItems.getSelected()
                ,   defaultCategorySelectedId = defaultCategorySelected && defaultCategorySelected.get('id')
                ,   defaultRubricsCategoryId = Rubrics.getCategoryId()

                CategoryItems.on('collection:change:selected', function(selected) {
                    if ( !selected || selected.get('class_name') == 'category' ) {
                        var id = selected && selected.get('id')
                        Rubrics.setCategoryId(id != defaultCategorySelectedId ? id : defaultRubricsCategoryId)
                    }
                }, this)
            }

            // Run...
            var rubrics = options && options.rubrics || []
            Rubrics.reset(rubrics)
        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix
        ,   rubrics: [{% for object in objects %}{% include object_template_name with object=object only %}{% if not forloop.last %}, {% endif %}{% endfor %}]
    })


})(jQuery, Backbone, _);

{% endwith %}{% endwith %}