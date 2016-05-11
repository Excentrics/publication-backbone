(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ rubricator_name }}'

    // The DOM element for a rubric...
    //var RubricView = Backbone.View.extend({
    var RubricItemView = Backbone.StatefulView.extend({

        //... is a list tag.
        tagName:  "li"

    ,   template: '#' + name_prefix + '-item-template'

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

        // The DOM events specific to an item.
    ,   events: {
            "click .ex-js-toggle": "onToggle"
        ,   "click .ex-js-set": "onSet"
        ,   "click .ex-js-unset-children": "onUnsetChildren"
        ,   "click .ex-js-toggle-description": "onToggleDescription"
        ,   "click .ex-js-hide-description": "onHideDescription"
        ,   "click .ex-js-expand-or-collapse": "onExpandOrCollapse"
        }

        // The RubricView listens for changes to its model, re-rendering. Since there's
        // a one-to-one correspondence between a **Rubric** and a **RubricView** in this
        // app, we set a direct reference on the model for convenience.
    ,   initialize: function(options) {
            this.Rubrics = options.rubrics

            this.childrenView = options.childrenView || RubricItemView

            this.initializeTemplate()

            var rootModel = this.Rubrics.getRoot()
            ,   settings = _.extend({
                model: rootModel
            }, options)

            this.model = settings.model
            this.collection = this.model.collection


            this.children = []
            _.each(this.model.getChildren(), function( model ){
                var view = new this.childrenView({
                    model: model
                ,   rubrics: this.Rubrics
                ,   childrenView: this.childrenView
                })
                this.children.push(view)
            }, this)


            this.isActual = false
            this.isUpdateLock = false
            this.isRootModel = this.model == rootModel

            this.details = $()

            this.collection.on('collection:startCascadeUpdate:tagged collection:startCascadeUpdate:is_potential_and_is_real', this.lockUpdate, this)
            this.collection.on('collection:finishCascadeUpdate:tagged', this.unlockUpdate, this)
            this.collection.on('collection:finishCascadeUpdate:is_potential_and_is_real', this.unlockPartialUpdate, this)
            this.collection.on('showDescription', this.singletonShowDescription, this)
            this.model.on('change determinant:grandchildren:change:tagged', this.change, this)
            this.model.on('remove outdate', this.clear, this)

            this.on('transition', function(leaveState, enterState) {
                if ( enterState != 'outdate' ) {
                    this.model.set({currentState: enterState}, {silent: true})
                }
            }, this)

            this.toState(this.model.get('currentState'))
        }

    ,   states: {
            'ex-state-default': {}
        ,   'ex-state-description': {
                enter: ['showDescription']
            ,   leave: ['hideDescription']
            }
        ,   'ex-state-collapsed': {
                enter: ['collapse']
            ,   leave: ['expand']
            }
        ,   'ex-state-collapsed ex-state-description': {
                enter: ['collapse', 'showDescription']
            ,   leave: ['expand', 'hideDescription']
            }
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: ''}
            }
        ,   'ex-state-default': {
                'showDescription': {enterState: 'ex-state-description'}
            ,   'collapse': {enterState: 'ex-state-collapsed'}
            }
        ,   '*': {
                'outdate': {enterState: 'outdate'}
            }
        ,   'ex-state-description': {
                'hideDescription': {enterState: 'ex-state-default'}
            ,   'collapse': {enterState: 'ex-state-collapsed ex-state-description'}
            }
        ,   'ex-state-collapsed': {
                'expand': {enterState: 'ex-state-default'}
            ,   'showDescription': {enterState: 'ex-state-collapsed ex-state-description'}
            }
        ,   'ex-state-collapsed ex-state-description': {
                'expand': {enterState: 'ex-state-description'}
            ,   'hideDescription': {enterState: 'ex-state-collapsed'}
            }
        }


        // Re-render the rubric item.
    ,   render: function() {
            var isNotActual = !this.isActual || _.find(this.children, function( view ){ return !view.isActual })
            if ( isNotActual ) {
                _.each(this.children, function( view ){ view.$el.detach() }, this)
                var parent = this.model.getParent()
                ,   children = _.map(this.model.getChildren(), function( model ) { return model.getJSON() })
                ,   isChildrenTagged = this.model.isChildrenTagged()
                ,   context = _.extend(_.clone(this.model.getJSON()), {
                            parent: (parent) ? parent.getJSON() : null
                        ,   children: children
                        ,   isChildrenTagged: isChildrenTagged
                        })
                ,   elAttr = {
                    'data-slug': this.model.get('slug')
                ,   'data-method': this.model.get('method')
                ,   'data-is-checked': this.model.get('tagged') ? "true" : "false"
                ,   'data-is-children-checked': isChildrenTagged ? "true" : "false"
                }
                if ( this.children.length ) {
                    elAttr['data-has-children'] = "true"
                }
                if ( this.model.get('branch') ) {
                    elAttr['data-branch'] = "true"
                }
                if ( this.model.get('trunk') ) {
                    elAttr['data-trunk'] = "true"
                }
                var tags = this.model.get('tags')
                if ( tags ) {
                    elAttr['data-tags'] = tags
                }
                var is_potential = this.model.get('is_potential')
                if ( !_.isNull(is_potential) ) {
                    elAttr['data-is-potential'] = is_potential ? "true" : "false"
                }
                var is_real = this.model.get('is_real')
                if ( !_.isNull(is_real) ) {
                    elAttr['data-is-real'] = is_real ? "true" : "false"
                }

                this.$el.empty().append($(this.template(context))).attr(elAttr)

                // delegate events
                this.delegateEvents()

                if (this.model.get('has_extra') || this.model.get('tagged')) {
                    this.details = (parent) ? this.$('.ex-details') : this.$el.closest('.ex-details')
                    _.each(this.children, function( view ){ this.details.append(view.render().$el) }, this)
                }
                this.isActual = true
                // render
            } else {
                _.each(this.children, function( view ){ view.render() })
                // re-render
            }
            return this
        }

    ,   partialRender: function () {
            if ( !this.isActual ) {
                var elAttr = {}
                ,   is_potential = this.model.get('is_potential')
                ,   is_real = this.model.get('is_real')
                if ( !_.isNull(is_potential) ) {
                    elAttr['data-is-potential'] = is_potential ? "true" : "false"
                }
                if ( !_.isNull(is_real) ) {
                    elAttr['data-is-real'] = is_real ? "true" : "false"
                }
                this.$el.attr(elAttr)
            }
            _.each(this.children, function( view ){ view.partialRender() })
            this.isActual = true
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

    ,   unlockPartialUpdate: function() {
            this.isUpdateLock = false
            if ( this.isRootModel ) {
                this.partialRender()
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
            this.collection.off('collection:startCascadeUpdate:tagged collection:startCascadeUpdate:is_potential_and_is_real', this.lockUpdate, this)
            this.collection.off('collection:finishCascadeUpdate:tagged', this.unlockUpdate, this)
            this.collection.off('collection:finishCascadeUpdate:is_potential_and_is_real', this.unlockPartialUpdate, this)
            this.collection.off('showDescription', this.singletonShowDescription, this)
            this.model.off('change determinant:grandchildren:change:tagged', this.change, this)
            this.model.off('remove outdate', this.clear, this)
            return Backbone.View.prototype.stopListening.call(this)
        }

    ,   remove: function() {
            this.trigger('outdate')
            return Backbone.View.prototype.remove.call(this)
        }

    // Toggle the `"tagged"` state of the model.
    ,   onToggle: function() {
            this.model.toggle()
            $(document.body).trigger('click')
            return false
        }

    ,   onSet: function() {
            this.model.set('tagged', true)
            $(document.body).trigger('click')
            return false
        }

    ,   onUnsetChildren: function() {
            this.model.unsetChildren()
            $(document.body).trigger('click')
            return false
        }

    ,   showDescription: function() {
            this.collection.trigger('showDescription', this)
            if ( this.model.get('short_description') && !this.model.get('description') ) {
                this.model.fetch()
            }
            // show description
        }

    ,   hideDescription: function() {
            this.collection.trigger('hideDescription', this)
            // hide description
        }

    ,   onToggleDescription: function() {
            if ( this.currentState.indexOf('ex-state-description') == -1 ) {
                $(document.body).trigger('click')
                this.trigger('showDescription')
            } else {
                this.trigger('hideDescription')
            }
            return false
        }

    ,   onHideDescription: function() {
            this.trigger('hideDescription')
            return false
        }

    ,   singletonShowDescription: function(view) {
            if ( (this != view) && (this.currentState.indexOf('ex-state-description') != -1) ) {
                this.trigger('hideDescription')
            }
        }

    ,   collapse: function() {
            // collapse
        }

    ,   expand: function() {
            // expand
        }

    ,   onExpandOrCollapse: function() {
            if ( this.currentState.indexOf('ex-state-collapsed') == -1 ) {
                if ( this.model.get('tagged') || this.model.get('has_extra') ) {
                    this.trigger('collapse')
                } else {
                    this.model.set('tagged', true)
                }
            } else {
                this.trigger('expand')
            }
            return false
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "RubricItemView"

    ,   views: {
            RubricItemView: RubricItemView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);