{% load publication_backbone_tags %}{% get_config as config %}
(function($, Backbone, _) {

    "use strict";

    var name_prefix = 'breadcrumbs'

    // Breadcrumbs View
    // ---------------
    var BreadcrumbsView = Backbone.StatefulView.extend({

       template: '#' + name_prefix + '-item-template'
        // The DOM events specific to an item.
    ,   events: {
            "click .ex-js-breadcrumb-item": "onCategoryClick"
        ,   "click .ex-js-breadcrumb-group-unset": "onGroupUnsetClick"
        }

    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

    ,   initialize: function(options) {

            this.throttledRender = _.throttle(this.render, 500, {leading: false})

            this.initializeTemplate()
            if ( this.collection ) {
                this.collection.on('reset update collection:change:selected', this.throttledRender, this)
            }
            this.CatalogItems = options && options.CatalogItems || null
            if ( this.CatalogItems ) {
                this.CatalogItems.getGroup().on('change', this.throttledRender, this)
                this.CatalogItems.getCategory().on('change', this.throttledRender, this)
                this.CatalogItems.getSubjects().on('reset update', this.throttledRender, this)
                this.CatalogItems.getRelations().on('reset update', this.throttledRender, this)
            }
            this.trigger('initialized')
        }

    ,   render: function() {
            var selected = this.collection && this.collection.getSelected() || null
            ,   breadcrumbsList
            if ( selected && selected.has('resource_uri') ){
                breadcrumbsList = selected.getParents()
                breadcrumbsList.push(selected)
            } else {
                breadcrumbsList = []
            }
            if ( !breadcrumbsList.length && this.CatalogItems ) {
                var category = this.CatalogItems.getCategory()
                if ( category.get('id') ) {
                    breadcrumbsList.push(category)
                }
            }
            var breadcrumbsListJSON = _.map(breadcrumbsList, function(item){ return item.toJSON() })
            ,   group = this.CatalogItems && this.CatalogItems.getGroup()
            ,   groupJSON = group && group.get('id') ? group.toJSON() : null
            ,   subjects = this.CatalogItems && this.CatalogItems.getSubjects()
            ,   subjectsJSON = subjects ?
                    _.filter(subjects.toJSON(), function(obj){ return _.has(obj, "resource_uri") }) : []
            ,   relations = this.CatalogItems && this.CatalogItems.getRelations()
            ,   relationsJSON = subjects ?
                    _.filter(relations.toJSON(), function(obj){ return _.has(obj, "resource_uri") }) : []
            ,   context = {
                    items: breadcrumbsListJSON
                ,   group: groupJSON
                ,   subjects: subjectsJSON
                ,   relations: relationsJSON
                }
            ,   r = /\s{2,}/g
            ,   titles = ['{{ config.PUBLICATION_BACKBONE_DEFAULT_CATALOG_TITLE }}'].concat(
                    _.map(breadcrumbsListJSON, function(item){ return item.name.replace(r, ' ') })
                ) // finally try find default catalog title

            if ( !_.isNull(groupJSON) && groupJSON.name ) {
                titles.push(groupJSON.name.replace(r, ' '))
            }
            if ( _.isUndefined(this.oldTitles) ) {
                this.oldTitles = titles.slice(0)
            }

            var i = this.oldTitles.length
            ,   start
            ,   end
            ,   title = document.title
            while ( i-- ) {
                start = title.indexOf(this.oldTitles[i])
                if ( start != -1 ) {
                    end = start + this.oldTitles[i].length
                    document.title = title.substring(0, start) + _.last(titles) + title.substring(end)
                    break
                }
            }
            this.oldTitles = titles

            this.$el.empty().append(this.template(context))
            return this
        }

    ,   onCategoryClick: function(e){
            e.preventDefault()
            var id = $(e.currentTarget).data('category-id')
            this.collection.setSelected({id: id})
            return false
        }

    ,   onGroupUnsetClick: function(){
            this.CatalogItems.setGroup()
            return false
        }

    })

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "BreadcrumbsView"

    ,   views: {
            BreadcrumbsView: BreadcrumbsView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);