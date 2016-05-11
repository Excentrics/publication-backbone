(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'

    // The category Title
    var CategoryTitleElementView = Backbone.StatefulView.extend({

        template: '#' + name_prefix + '-app-template'
    ,   tagName: "li"

    ,   events: {
            "click .ex-js-open-category": "clickEvent"
        }

    ,   clickEvent: function(e){
            if (this.model.collection.length > 1){
                this.model.collection.trigger("setCategoryEvent", this)
                return false
            }
        }

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html())
        }

    ,   initialize: function(options) {
            this.CatalogItems = options.CatalogItems
            this.initializeTemplate()
            this.trigger('initialized')
        }

    ,   render: function() {
            var orderingAlgorithm = this.CatalogItems && this.CatalogItems.getOrderingAlgorithm()
            ,   subjects = this.CatalogItems && this.CatalogItems.getSubjects()
            ,   relations= this.CatalogItems && this.CatalogItems.getRelations()
            ,   context = _.extend({
                    is_single: 'true' ? this.model.collection.length == 1 : 'false'
                ,   orderingAlgorithm: orderingAlgorithm && orderingAlgorithm.get('id') ? orderingAlgorithm.toJSON() : null
                ,   subjects: subjects ? subjects.toJSON() : null
                ,   relations: relations ? relations.toJSON() : null
                }, this.model.toJSON())

            this.$el.toggleClass('active', this.model.selected)
            this.$el.html(this.template(context))

            return this
        }

    ,   states: {
            '': {}
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: ''}
            }
        }

    })

    // The Categories Title View
    // ---------------
    var CategoriesTitleView = Backbone.StatefulView.extend({

        initialize: function(options) {

            this.trigger('initialized')
            this.model.collections[this.model.catalogKey + '_CatalogItems'].on('reset update', this.updateView, this)

        }

    ,   updateView: function(){
            this.$el.empty()
            this.render()
        }

    ,   render: function() {
            var CatalogItems = this.model.collections[this.model.catalogKey + '_CatalogItems']
            ,   CategoryItems = this.model.collections[this.model.catalogKey + "_CategoryItems"]
            ,   selected_id = CatalogItems.getCategoryId()
            ,   categoryTitleElementView = BBNS.app.modules['CategoriesTitleView'].views['CategoryTitleElementView'].extend({
                    template: this.template
                })

            _.each(CategoryItems.models, function(item){
                item.selected = true ? item.id == selected_id : false
                var categoryTitleView = new categoryTitleElementView({
                    model: item
                ,   CatalogItems: CatalogItems
                })
                this.$el.append(categoryTitleView.render().el)
            }, this)

            if (CategoryItems.length == 1) {
                this.$el.addClass('list-unstyled is_single')
                this.$el.removeClass('nav nav-tabs')
            }

            return this
        }

    ,   states: {
            '': {}
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: ''}
            }
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoriesTitleView"

    ,   views: {
            CategoriesTitleView: CategoriesTitleView,
            CategoryTitleElementView: CategoryTitleElementView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);