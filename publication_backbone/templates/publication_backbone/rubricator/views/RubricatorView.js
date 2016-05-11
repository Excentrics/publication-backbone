(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ rubricator_name }}'


    var RubricatorView = Backbone.StatefulView.extend({

        template: '#' + name_prefix + '-app-template'

    ,   initialize: function(options) {
            this.rubricItemView = options.rubricItemView

            var $details = this.$el.find('.ex-details')
            if ( $details.length ) {
                this.$details = $details
                // duplicate state class
                this.on('transition', function(leaveState, enterState) {
                    this.$details.removeClass(this._detailsStateClassName || '')
                    this._detailsStateClassName = (this.states[enterState].className || enterState)
                    this.$details.addClass(this._detailsStateClassName)
                }, this)
            } else {
                this.$details = this.$el
            }

            this.collection.on('reset update', this.addAll, this)

            this.collection.on('collection:fetch:start', function(){
                this.trigger('fetch:start')
            }, this)

            this.collection.on('collection:fetch:stop', function(){
                this.trigger('fetch:stop')
            }, this)

            this.trigger('initialized')
            // this.collection.reset...
        }

    ,   addAll: function() {
            var view = new this.rubricItemView({
                    template: '#' + name_prefix + '-item-template'
                ,   rubrics: this.collection
                ,   childrenView: this.rubricItemView
                })

            view.setElement( this.$details ).render()
        }

    ,   states: {
            'ex-state-default': {}
        ,   'ex-state-loading': {}
        }

    ,   transitions: {
            'init': {
                'initialized': {enterState: 'ex-state-default'}
            }
        ,   'ex-state-default': {
                'fetch:start': {enterState: 'ex-state-loading'}
            }
        ,   'ex-state-loading': {
                'fetch:stop': {enterState: 'ex-state-default'}
            }
        }

    })


    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "RubricatorView"

    ,   views: {
            RubricatorView: RubricatorView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);