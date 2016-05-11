(function($, Backbone, _) {

    "use strict";

    var name_prefix = 'catalog_items'

    // Catalog Item View
    // --------------

    // The DOM element for a catalog item...
    //var CatalogItemView = Backbone.View.extend({
    var CatalogItemView = Backbone.StatefulView.extend({

        //... is a list tag.
        tagName:  "li"

    ,   className: "ex-catalog-item"

    ,   template: '#' + name_prefix + '-item-template'

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

        // The DOM events specific to an item.
    ,   events: {
            "click .ex-js-toggle-description": "onToggleDescription"
        ,   "mouseenter .ex-js-enter-show-description": "onShowDescription"
        ,   "mouseleave .ex-js-leave-hide-description": "onHideDescription"
        ,   "click .ex-js-open": "onOpen"
        ,   'click .ex-js-ignore': 'ignore'
        }

    ,   isHover: false
        // The CatalogItemView listens for changes to its model, re-rendering. Since there's
        // a one-to-one correspondence between a **CatalogItem** and a **CatalogItemView** in this
        // app, we set a direct reference on the model for convenience.
    ,   initialize: function(options) {
            this.thumbnailWidth = options.thumbnailWidth || 200
            this.thumbnailHeight = options.thumbnailHeight || 200

            this.$window = $(window)
            this.initializeTemplate()
            this.model.on('change', this.render, this)
            this.model.on('remove outdate', this.remove, this)
            _.bindAll(this, 'tryHideDescription', 'tryShowDescription')
            this._isImagesLoading = false
            this.trigger('initialized')
        }

    ,   states: {
            'ex-state-default': {}
        ,   'ex-state-description': {
                enter: ['showDescription']
            ,   leave: ['hideDescription']
            }
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: 'ex-state-default'}
            }
        ,   'ex-state-default': {
                'showDescription': {enterState: 'ex-state-description'}
            }
        ,   '*': {
                'outdate': {enterState: 'outdate'}
            }
        ,   'ex-state-description': {
                'hideDescription': {enterState: 'ex-state-default'}
            }
        }

        // Re-render the catalog item.
    ,   render: function() {
            var context = _.extend({
                    thumbnail_width: this.model.collection.getThumbnailWidth ? this.model.collection.getThumbnailWidth() : this.thumbnailWidth
                ,   thumbnail_height: this.model.collection.getThumbnailHeight ? this.model.collection.getThumbnailHeight() : this.thumbnailHeight
                }, this.model.getJSON())
            this.$el.html(this.template(context)).attr({
                'data-is-main': this.model.get("is_main")=='True' ? 'true' : 'false'
            })
            this.$el.html(this.template(context)).attr({
                'data-is-images-loading': this._isImagesLoading ? 'true' : 'false'
            })
            var imagesLoaded = new BBNS.ImagesLoaded(this.$("img"), {
                        context: this
                    //,   debug: 0
                    }
                ,   function( instance ) {
                        instance.off('loading', this.onImagesLoading)
                        if ( this._isImagesLoading ) {
                            this._isImagesLoading = false
                            this.$el.attr({
                                'data-is-images-loading': 'false'
                            })
                        }
                    })
            imagesLoaded.on('loading', this.onImagesLoading, this)
            return this
        }

    ,   stopListening: function() {
            this.model.off('change', this.render, this)
            this.model.off('remove outdate', this.remove, this)

            return Backbone.View.prototype.stopListening.call(this)
        }

    ,   remove: function() {
            this.trigger('outdate')
            return Backbone.View.prototype.remove.call(this)
        }

    ,   getPosition: function() {
            var offset = this.$el.offset()
            ,   x = offset.left - this.$window.scrollLeft()
            ,   y = offset.top - this.$window.scrollTop()
            ,   rX = (x + 0.5 * this.$el.width()) / this.$window.width()
            ,   rY = (y + 0.5 * this.$el.height()) / this.$window.height()
            return [rX < 0.333 ? 'left' : rX > 0.667 ? 'right' : 'center', rY < 0.333 ? 'top' : rY > 0.667 ? 'bottom' : 'center']
        }

    ,   showDescription: function() {
            // show description
            if ( ( this.model.get('short_characteristics') && !this.model.get('characteristics') ) ||
                ( this.model.get('short_lead') && !this.model.get('lead') ) ) {
                this.model.fetch()
            }
            var position = this.getPosition()
            this.$el.attr({
                'data-horizontal-position': position[0]
            ,   'data-vertical-position': position[1]
            })
        }

    ,   hideDescription: function() {
            // hide description
        }

    ,   onToggleDescription: function(e) {
            if ( this.currentState.indexOf('ex-state-description') == -1 ) {
                this.trigger('showDescription')
            } else {
                if ( this.getIsHover(e.pageX, e.pageY) ) {
                    this.doOpen()
                } else {
                    this.trigger('hideDescription')
                }
            }
        }

    ,   getIsHover: function(pageX, pageY) {
            var $thumbnail = this.$('.ex-js-thumbnail')
            ,   offset = $thumbnail.offset()
            ,   posX = pageX - offset.left
            ,   posY = pageY - offset.top
            return posX >= 0 && posY >=0 && posX <= $thumbnail.outerWidth() && posY <= $thumbnail.outerHeight()

        }

    ,   onHideDescription: function(e) {
            this.isHover = this.getIsHover(e.pageX, e.pageY)
            if ( this.currentState.indexOf('ex-state-default') == -1 ) {
                _.delay(this.tryHideDescription, 300)
            }
        }

    ,   onShowDescription: function(e) {
            this.isHover = this.getIsHover(e.pageX, e.pageY)
            if ( this.currentState.indexOf('ex-state-description') == -1 ) {
                _.defer(this.tryShowDescription)
            }
        }

    ,   doOpen: function() {
            var model = this.model.getJSON()
            if ( model.variants > 1 ) {
                this.model.collection.setGroup(model)
            } else {
                var external_url = _.find(model.characteristics, function(obj){
                    return obj.t.indexOf("external-url") != -1
                }, this)
                if ( external_url ) {
                    var redirectWindow = window.open(external_url.v, '_blank');
                    redirectWindow.location
                } else {
                    document.location.href = model.resource_uri
                }
            }
        }

    ,   onOpen: function(e) {
            this.doOpen()
            return false
        }

    ,   tryHideDescription: function() {
            if (!this.isHover)
                this.trigger('hideDescription')
        }

    ,   tryShowDescription: function() {
            if (this.isHover)
                this.trigger('showDescription')
        }

    ,   onImagesLoading: function(instance) {
            if ( !this._isImagesLoading ) {
                this._isImagesLoading = true
                this.$el.attr({
                    'data-is-images-loading': 'true'
                })
            }
        }

    ,   ignore: function() {
            return false
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "{% block module_name %}CatalogItemView{% endblock %}"

    ,   views: {
            CatalogItemView: CatalogItemView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);
