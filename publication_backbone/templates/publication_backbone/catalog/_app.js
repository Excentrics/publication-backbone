{% load beautiful_fields_tags publication_backbone_tags %}{% get_config as config %}{% with object_template_name='publication_backbone/catalog/_meta_object.json' relation_template_name='publication_backbone/catalog/_relation.json' subject_template_name='publication_backbone/catalog/_subject.json' group_template_name='publication_backbone/publicationgroup_detail.json' category_template_name='publication_backbone/category_detail.json' order_by_template_name='publication_backbone/orderingalgorithm_detail.json' %}
(function($, Backbone, _) {

    "use strict";


    var name_prefix = '{{ name }}'
    ,   cartKey = 'cart'
    ,   catalogUrlRoot = "{% url 'publication_list' %}"
    ,   catalogListUrlRoot = {% if category %}"{% url 'publication_list' path=category.path %}"{% else %}catalogUrlRoot{% endif %}


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "{% block module_name %}CatalogApplication{% endblock %}"

    ,   preinitialize: function(options){

            var uses = [
                'CatalogItemsList'{% block catalog_router_uses %}
            ,   'CatalogRouter'{% endblock %}
            ,   'CatalogItemView'
            ,   'CatalogItemsView'
            ,   'CatalogItem'
            ,   'GroupItem'
            ]

{% block rubricator_uses %}
            if ( options && options.rubricatorKey ) {
                uses.push(options.rubricatorKey)
            }
{% endblock rubricator_uses %}

            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){

            var CatalogItem = BBNS.app.modules['CatalogItem'].models['CatalogItem'].extend({
                    urlRoot: catalogUrlRoot
                })
            ,   GroupItem = BBNS.app.modules['GroupItem'].models['GroupItem']
            ,   CategoryItem = _.has(BBNS.app.modules, 'CategoryItem') ? BBNS.app.modules['CategoryItem'].models['CategoryItem'] : null
            ,   OrderingAlgorithm = _.has(BBNS.app.modules, 'OrderingAlgorithm') ? BBNS.app.modules['OrderingAlgorithm'].models['OrderingAlgorithm'] : null
            ,   CatalogItemsList = BBNS.app.modules['CatalogItemsList'].collections['CatalogItemsList'].extend({
                    model: CatalogItem
                ,   groupModel: GroupItem
                ,   categoryModel: CategoryItem
                ,   orderingAlgorithmModel: OrderingAlgorithm
                ,   subjectModel: CatalogItem
                ,   urlRoot: catalogListUrlRoot
                })
            ,   CatalogItems = this.collections.CatalogItems = this.collections[name_prefix + "_CatalogItems"] = new CatalogItemsList

            CatalogItems.meta = {
                limit: {{ page_obj.limit }}
            ,   offset: {{ page_obj.offset }}
            ,   total_count: {{ page_obj.paginator.count }}
            ,   orphans: {{ page_obj.paginator.orphans }}
            ,   ranges: options.ranges
            ,   today: {{ today|fast_floatformat:-2 }}
            ,   thumbnail_width: {{ thumbnail_width }}
            ,   thumbnail_height: {{ thumbnail_height }}
            ,   potential_rubrics_ids: [{{ potential_rubrics_ids|join:', ' }}]
            ,   real_rubrics_ids: [{{ real_rubrics_ids|join:', ' }}]
            }

            CatalogItems.on('collection:fetch:start', function(){
                BBNS.app.events.t('catalog:fetch:start', this)
            }, this)

            CatalogItems.on('collection:fetch:stop', function(){
                BBNS.app.events.t('catalog:fetch:stop', this)
            }, this)

            {% if category %}
            CatalogItems.setCategory({% include category_template_name with object=category %}, {silent: true})
            {% endif %}{% if set %}
            CatalogItems.setRubrics([{{ set|join:', ' }}], {silent: true})
            {% endif %}{% if publication_group %}
            CatalogItems.setGroup({% include group_template_name with object=publication_group %}, {silent: true})
            {% endif %}{% if subj %}
            CatalogItems.setSubjects([{% for object in subj %}{% include subject_template_name with object=object thumbnail_geometry=thumbnail_geometry thumbnail_background=thumbnail_background only %}{% if not forloop.last %}, {% endif %}{% endfor %}], {silent: true})
            {% endif %}{% if rel %}
            CatalogItems.setRelations([{% for object in rel %}{% include relation_template_name with object=object only %}{% if not forloop.last %}, {% endif %}{% endfor %}], {silent: true})
            {% endif %}{% if order_by %}
            CatalogItems.setOrderingAlgorithm({% include order_by_template_name with object=order_by %}, {silent: true})
            {% endif %}
            CatalogItems.getOrderingAlgorithmsList().reset([{% for ordering_mode in ordering_modes %}{% include order_by_template_name with object=ordering_mode %}{% if not forloop.last %}, {% endif %}{% endfor %}], {silent: true})

{% comment %}
            // External cart interface
            /*var cartApp = BBNS.app.modules[cartKey]
            if ( cartApp ) {
                CatalogItem.prototype.getInCart = function() {
                    var item = cartApp.getCartItem(this.id)
                    return item && item.get('quantity') || 0
                }

                CatalogItems.on('addToCart', function(model, quantity){
                    cartApp.addToCart(model.get('id'), quantity)
                }, this)

                cartApp.on('cart:reset', function(cart) {
                    CatalogItems.each(function(model){
                        model.set('in_cart', model.getInCart())
                    }, this)
                }, this)
            }*/
{% endcomment %}

{% block catalog_item_view %}
            // CatalogItemView
            var CatalogItemView = BBNS.app.modules['CatalogItemView'].views['CatalogItemView'].extend({
                template: '#' + name_prefix + '-item-template'
            })
{% endblock catalog_item_view %}

            // Create main module view **AppView**
            var AppView = BBNS.app.modules['CatalogItemsView'].views['CatalogItemsView'].extend({
                selector: ".ex-js-" + name_prefix + "-list"
            })
            this.views.app = new AppView({
                collection: CatalogItems

                // Instead of generating a new element, bind to the existing skeleton of
                // the App already present in the HTML.
            ,   el: $("#" + name_prefix + "-app")

            ,   CatalogItemView: CatalogItemView
            })

{% block rubricator_event_listener %}
            // if rubricator app then listen rubricator_app event 'rubricator:change:tagged'
            var rubricatorKey = options && options.rubricatorKey || null
            ,   rubricatorApp = BBNS.app.modules[rubricatorKey]
            ,   Rubrics = null
            if ( rubricatorApp ){
                Rubrics = rubricatorApp.collections.Rubrics
                Rubrics.on('collection:change:tagged', function(ids) {
                    CatalogItems.setRubrics(ids)
                }, this)

                CatalogItems.on('collection:change:rubrics', function(ids) {
                    if ( ids && ids.length ) {
                        Rubrics.setTagged(ids)
                    } else {
                        var changed = Rubrics.setTagged(ids, {silent: true})
                        if ( changed ) {
                            Rubrics.fetch()
                        }
                    }
                }, this)

                // ------------------------
                CatalogItems.on('collection:fetch:stop', function(){
                    Rubrics.setSelectionAssistant(CatalogItems.getPotentialRubricIds(), CatalogItems.getRealRubricIds())
                }, this)

                Rubrics.setSelectionAssistant(CatalogItems.getPotentialRubricIds(), CatalogItems.getRealRubricIds())
            }
{% endblock rubricator_event_listener %}

{% block category_event_listener %}
            // if category app then listen category_app event 'category:change:selected'
            var categoryKey = options && options.categoryKey || null
            ,   categoryApp = BBNS.app.modules[categoryKey]
            ,   CategoryItems = null
            if ( categoryApp ){
                CategoryItems = categoryApp.collections.CategoryItems
                var defaultCategorySelected = CategoryItems.getSelected()
                ,   defaultCategorySelectedId = defaultCategorySelected && defaultCategorySelected.get('id')
                ,   defaultCatalogCategoryId = CatalogItems.getCategoryId()

                CategoryItems.on('collection:change:selected', function(selected, options) {
                    if ( !selected || selected.get('class_name') == 'category' ) {
                        var id = selected && selected.get('id')
                        ,   category_id = id != defaultCategorySelectedId ? id : defaultCatalogCategoryId
                        CatalogItems.setCategory({id: category_id})
                    }
                }, this)

                CatalogItems.on('collection:change:category', function(id) {
                    if ( Rubrics ) {
                        var changed = Rubrics.setCategoryId(id, {silent: true, tagged_ids: CatalogItems.getRubrics()})
                        if ( changed ) {
                            Rubrics.fetch({reset: true})
                        }
                    }
                    CategoryItems.setSelected({id: id != defaultCatalogCategoryId ? id : defaultCategorySelectedId})
                }, this)
            }
{% endblock category_event_listener %}

            // Run...
            var catalogItems = options && options.catalogItems || []
            CatalogItems.reset(catalogItems)

{% block catalog_router_init %}
            // Catalog router
            var CatalogRouter = BBNS.app.modules['CatalogRouter'].routers['CatalogRouter'].extend({
                    CatalogItems: CatalogItems
                ,   paramsNamespace: name_prefix
                })
            this.routers.CatalogRouter = new CatalogRouter
{% endblock catalog_router_init %}

        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
        name: name_prefix
    ,   rubricatorKey: {% if rubricator_name %}"{{ rubricator_name }}"{% else %}null{% endif %}
    ,   categoryKey: "{{ config.PUBLICATION_BACKBONE_CATEGORY_KEY }}"
    ,   catalogItems: [{% for object in object_list %}{% include object_template_name with object=object position=page_obj.offset|add:forloop.counter0 category=category thumbnail_geometry=thumbnail_geometry thumbnail_background=thumbnail_background only %}{% if not forloop.last %}, {% endif %}{% endfor %}]
    ,   ranges: {% templatetag openbrace %}{% for range_name, range in ranges.items %}{% if range %}"{{ range_name }}": {% templatetag openbrace %}
"value": [{% if range.value.0|yesno:"2,1," %}{{ range.value.0|fast_floatformat:-2 }}{% else %}null{% endif %}, {% if range.value.1|yesno:"2,1," %}{{ range.value.1|fast_floatformat:-2 }}{% else %}null{% endif %}],
"limit": [{% if range.limit.0|yesno:"2,1," %}{{ range.limit.0|fast_floatformat:-2 }}{% else %}null{% endif %}, {% if range.limit.1|yesno:"2,1," %}{{ range.limit.1|fast_floatformat:-2 }}{% else %}null{% endif %}]
{% templatetag closebrace %}{% if not forloop.last %}, {% endif %}{% endif %}{% endfor %}{% templatetag closebrace %}
    })


})(jQuery, Backbone, _);

{% endwith %}