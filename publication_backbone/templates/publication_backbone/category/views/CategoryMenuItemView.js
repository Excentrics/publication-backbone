(function($, Backbone, _) {

    "use strict";

    // The Category Menu Item View
    // ---------------
    var CategoryMenuItemView = Backbone.StatefulView.extend({

        //... is a list tag.
        tagName:  "li"

    ,   template: '#category-menu-item-template'

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

        // The DOM events specific to an item.
    ,   events: {
            "click .ex-js-menu-item-container": "onClick"
        ,   "mouseenter .ex-js-menu-item-container": "onMouseEnter"
        ,   "mouseleave .ex-js-menu-item-container": "onMouseLeave"

        }

    //,   model: CategoryItem

    ,   isHover: false

    ,   initialize: function(options) {
            this.childrenView = options.childrenView || CategoryMenuItemView

            this.initializeTemplate()

            this.collection = this.model.collection

            var rootModel = this.model.collection.getRoot()

            this.children = []

            this.parent = options.parent ? options.parent : null

            _.each(this.model.getChildren(), function( model ){
                var view = new this.childrenView({model: model, parent: this, childrenView: this.childrenView})
                this.children.push(view)
            }, this)

            this.isActual = false
            this.isUpdateLock = false
            this.isRootModel = this.model == rootModel

            this.$details = $()

            this.collection.on('collection:startCascadeUpdate:selected', this.lockUpdate, this)
            this.collection.on('collection:finishCascadeUpdate:selected', this.unlockUpdate, this)

            this.model.on('change', this.change, this)
            this.model.on('remove outdate', this.clear, this)

            this.on('transition', function(leaveState, enterState) {
                if ( enterState != 'ex-state-outdate' ) {
                    this.model.set({currentState: enterState}, {silent: true})
                }
            }, this)

            _.bindAll(this, 'outsideClickHandler', 'doSelect', 'tryClose', 'tryOpen')

            this.toState(this.model.get('currentState'))

        }

    ,   states: {
            'ex-state-closed': {}
        ,   'ex-state-opened': {
                enter: ['doOpen']
            ,   leave: ['doClose']
            }
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: 'ex-state-closed'}
            }
        ,   '*': {
                'outdate': {enterState: 'ex-state-outdate'}
            }
        ,   'ex-state-closed': {
                'open': {enterState: 'ex-state-opened'}
            }
        ,   'ex-state-opened': {
                'close': {enterState: 'ex-state-closed'}
            }

        }

        // Re-render the rubric item.
    ,   render: function() {
            var isNotActual = !this.isActual || _.find(this.children, function( view ){ return !view.isActual })
            if ( isNotActual ) {
                _.each(this.children, function( view ){ view.$el.detach() }, this)
                var parent = this.model.getParent()
                ,   context = _.extend(_.clone(this.model.getJSON()), {
                            parent: (parent) ? parent.getJSON() : null
                        ,   children: _.map(this.model.getChildren(), function( model ) { return model.getJSON() })
                        })
                ,   level = this.model.getLevel()
                // redraw element
                var elAttr = {
                    'data-slug': this.model.get('slug')
                ,   'data-class-name': this.model.get('class_name')
                ,   'data-lvl': level
                ,   'data-status': this.model.get('status') || ''
                }
                if ( this.children.length ) {
                    elAttr['data-has-children'] = true
                }

                this.$el.empty().append($(this.template(context))).attr(elAttr)

                // delegate events
                this.delegateEvents()

                this.$details = (parent) ? this.$('.ex-js-details') : this.$el.closest('.ex-js-details')
                _.each(this.children, function( view ){ this.$details.append(view.render().$el) }, this)

                this.isActual = true
                // render
            } else {
                _.each(this.children, function( view ){ view.render() })
                // re-render
            }

            return this
        }

    ,   change: function() {
            this.isActual = false
            if ( !this.isUpdateLock ) {
                this.render()
            }
        }

    ,   lockUpdate: function() {
            this.isUpdateLock = true
        }

    ,   unlockUpdate: function() {
            this.isUpdateLock = false
            if ( this.isRootModel ) {
                this.render()
            }
        }

    ,   clear: function() {
            if ( this.isRootModel ) {
                this.stopListening()
            } else {
                this.remove()
            }
        }

    ,   stopListening: function() {
            this.collection.off('collection:startCascadeUpdate:selected', this.lockUpdate, this)
            this.collection.off('collection:finishCascadeUpdate:selected', this.unlockUpdate, this)

            this.model.off('change', this.change, this)
            this.model.off('remove outdate', this.clear, this)

            return Backbone.View.prototype.stopListening.call(this)
        }

    ,   remove: function() {
            this.trigger('outdate')
            return Backbone.View.prototype.remove.call(this)
        }

    ,   onClick: function() {
            if ( !this.isHover && this.model.getChildren().length ) {
                this.isHover = true
                this.tryOpen()
            } else {
                _.defer(this.doSelect)
                this.tryClose({force: true})
            }
            $(document.body).trigger('click')
            return false
        }

    ,   onMouseEnter: function() {
            if ( this.isMobile() ) {
                return
            }
            this.isHover = true
            this.tryOpen()
            return false

        }

    ,   onMouseLeave: function() {
            if ( this.isMobile() ) {
                return
            }
            this.isHover = false
            _.delay(this.tryClose, 600)
            return false
        }

    ,   outsideClickHandler: function(e) {
            this.tryClose({force: true})
        }

    ,   doSelect: function() {
            this.model.set('status', 'selected')
        }

    ,   doOpen: function() {
            if ( this.$details.length ) {
                var $window = $(window)
                ,   offset = this.$details.offset()
                ,   screenHeight = $window.height()
                ,   elTop = offset.top - $window.scrollTop()
                ,   elHeight = this.$details.outerHeight()
                ,   screenWidth = $window.width()
                ,   elLeft = offset.left - $window.scrollLeft()
                ,   elWidth = this.$details.outerWidth()
                ,   hDirection = ( elLeft + elWidth > screenWidth ) && ( elWidth * 2 <= elLeft ) ? 'rtl' : 'ltr'
                ,   vDirection = ( elTop + elHeight > screenHeight ) && ( elHeight <= elTop ) ? 'btt' : 'ttb'
                this.$details.attr({
                    'data-horizontal-direction': hDirection
                ,   'data-vertical-direction': vDirection
                })
            }
            if ( this.model.getLevel() == 1 ) {
                if ( this.isMobile() ) {
                    this.backdrop = $('<div class="ex-dropdown-backdrop"/>').insertBefore(this.parent.$el).on('click', this.outsideClickHandler)
                } else {
                    $(document).on('click', this.outsideClickHandler)
                }
            }
        }

    ,   doClose: function() {
            if ( this.$details.length ) {
                this.$details.removeAttr("data-horizontal-direction data-vertical-direction")
            }
            if ( this.model.getLevel() == 1 ) {
                if ( this.backdrop ) {
                    $(this.backdrop).off('click', this.outsideClickHandler).remove()
                    delete this.backdrop
                } else {
                    $(document).off('click', this.outsideClickHandler)
                }
            }
        }

    ,   tryClose: function(options){
            var settings = _.extend({
                    direction: "all"
                ,   force: false
                }, options)
            ,   doClose = false
            if ( !this.isHover || settings.force ) {
                if ( settings.direction == "parent" ) {
                    doClose = true
                } else {
                    var openedChildren = _.find(this.children, function( view ){
                        return view.currentState.indexOf('ex-state-opened') != -1
                    })
                    doClose = !openedChildren || openedChildren.tryClose({"direction": "children", force: settings.force})
                }
                if ( doClose ) {
                    this.isHover = false
                    this.trigger('close')
                    if ( (settings.direction != "children") && this.parent &&
                            (this.parent.currentState.indexOf('ex-state-closed') == -1) && this.parent.parent ) {
                        var openedSibling = _.find(this.parent.children, function( view ){
                            return view.currentState.indexOf('ex-state-opened') != -1
                        })
                        if ( !openedSibling ) {
                            this.parent.tryClose({"direction": "parent", force: settings.force})
                        }
                    }
                }
            }
            return doClose
        }

    ,   tryOpen: function(){
            if ( ( this.currentState.indexOf('ex-state-opened') == -1 ) && this.parent ) {
                var that = this
                ,   openedSibling = _.find(this.parent.children, function( view ){
                        return ( that != view ) && ( view.currentState.indexOf('ex-state-opened') != -1 )
                    })
                if ( openedSibling ) {
                    openedSibling.tryClose({"direction": "children", force: true})
                }
                this.parent.tryOpen()
                this.trigger('open')
            }
            return this.currentState.indexOf('ex-state-opened') != -1
        }

    ,   isMobile: function(){
            return BBNS.app.isTouch || ( $(window).width() < 980 )
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "CategoryMenuItemView"

    ,   views: {
            CategoryMenuItemView: CategoryMenuItemView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);
