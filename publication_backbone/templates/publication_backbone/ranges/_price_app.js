{% load beautiful_fields_tags %}

(function($, Backbone, _) {

    "use strict";


    var name_prefix = '{{ name }}'
    ,   catalogKey = '{{ catalog_key }}'
    ,   LIMIT = [0, 1e9]

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "Slider"

    ,   preinitialize: function(options){
            var uses = [
                'RangeModel'
            ,   'PriceView'
            ]
            uses.push(catalogKey)
            this.uses = _.union(this.uses, uses)
        }

    ,   initialize: function(options){
            var catalogApp = BBNS.app.modules[catalogKey]
            ,   CatalogItems = this.collections.CatalogItems = catalogApp.collections[catalogKey + '_CatalogItems']
            ,   Price = new BBNS.app.modules['RangeModel'].models['RangeModel']({
                    value: CatalogItems.getRangeValue(name_prefix)
                ,   limit: CatalogItems.getRangeLimit(name_prefix)
                })
            ,   PriceView = BBNS.app.modules['PriceView'].views['PriceView'].extend({
                    template: '#' + name_prefix + '-app-template'
                })

            // External events sender
            Price.on('change:value', function(model, value, options) {
                if ( !options || !options.target || !(options.target == this) ) {
                    CatalogItems.setRangeValue(name_prefix, value)
                }
            }, this)

            CatalogItems.on('collection:change:range:value', function(key, value) {
                var limit = Price.get("limit")
                if ( (key == name_prefix) && value && (value[0] >= limit[0]) && (value[1] <= limit[1]) ) {
                    Price.set("value", value)
                }
            }, this)

            CatalogItems.on('reset update', function() {
                Price.set("limit", CatalogItems.getRangeLimit(name_prefix))
                Price.set("value", CatalogItems.getRangeValue(name_prefix))
            }, this)

            var AppView = Backbone.StatefulView.extend({

                    initialize: function(options) {
                        this.addSlider()

                        CatalogItems.on('reset update', function() {
                            var limit = CatalogItems.getRangeLimit(name_prefix)
                            if ( (limit[0] != limit[1]) && !_.isEqual(limit, LIMIT) ) {
                                this.trigger('enable')
                            } else {
                                this.trigger('disable')
                            }
                        }, this)

                        this.trigger('initialized')

                        var limit = CatalogItems.getRangeLimit(name_prefix)
                        if ( (limit[0] != limit[1]) && !_.isEqual(limit, LIMIT) ) {
                            this.trigger('enable')
                        }
                    }

                ,   addSlider: function() {
                        this.priceView = new PriceView({
                            model: Price
                        ,   el: $("#id_" + name_prefix)
                        ,   sliderOptions: options.sliderOptions
                        })
                    }

                ,   states: {
                        'ex-state-enabled': {}
                    ,   'ex-state-disabled': {}
                    }

                ,   transitions: {
                        'init': {
                            'initialized': {enterState: 'ex-state-disabled'}
                        }
                    ,   'ex-state-disabled': {
                            'enable': {enterState: 'ex-state-enabled'}
                        }
                    ,   'ex-state-enabled': {
                            'disable': {enterState: 'ex-state-disabled'}
                        }
                    }
                })

            this.views.app = new AppView({
                // Instead of generating a new element, bind to the existing skeleton of
                // the App already present in the HTML.
                el: $("#"+ this.name +"-app")
            })

        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module({
            name: name_prefix
        ,   sliderOptions: {
                format: { format: "#,##0.##", locale: "{{ LANGUAGE_CODE }}" }
            ,   step: 1
            ,   skin: '{% include "publication_backbone/ranges/partials/_price_skin.html" %}'
            ,   dimension: '{% include "publication_backbone/ranges/partials/_price_dimension.html" %}'
            ,   round: 2
        }
    })


})(jQuery, Backbone, _);
