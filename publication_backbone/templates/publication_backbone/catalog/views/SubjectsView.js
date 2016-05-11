(function($, Backbone, _) {

    "use strict";

    var name_prefix = 'subjects'

    // Subjects View
    // ---------------

    // Our overall **AppView** is the top-level piece of UI.
    var SubjectsView = Backbone.StatefulView.extend({

        initialize: function(options) {
            this.SubjectItemView = options.SubjectItemView

            var $itemsList = this.$(this.selector)
            if ( $itemsList.length ) {
                this.$itemsList = $itemsList
                // duplicate state class
                this.on('transition', function(leaveState, enterState) {
                    this.$itemsList.removeClass(this._itemsListStateClassName || '')
                    this._itemsListStateClassName = (this.states[enterState].className || enterState)
                    this.$itemsList.addClass(this._itemsListStateClassName)
                }, this)
            } else {
                this.$itemsList = this.$el
            }

            this.collection.on('collection:change:subjects', this.render, this)
            this.trigger('initialized')
        }

    ,   selector: ".ex-js-" + name_prefix + "-list"

    ,   render: function(){

            var views = this.collection.getSubjects().map(function(model) {
                var view = new this.SubjectItemView({
                    model: model
                ,   thumbnailWidth: this.collection.getThumbnailWidth()
                ,   thumbnailHeight: this.collection.getThumbnailHeight()
                })

                return view.render().el
            }, this)

            this.$itemsList.empty().append(views)

            return this
        }

    ,   states: {
            'ex-state-default': {}
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: 'ex-state-default'}
            }
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "SubjectsView"

    ,   views: {
            SubjectsView: SubjectsView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);