{% load i18n beautiful_fields_tags %}
(function($, Backbone, _) {

    "use strict";

    // Utils
    // ----------

    function space125(value){
        var s125 = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1E3, 2E3, 5E3,
                    1E4, 2E4, 5E4, 1E5, 2E5, 5E5, 1E6, 2E6, 5E6, 1E7, 2E7, 5E7, 1E8, 2E8, 5E8, 1E9, 2E9, 5E9]
        ,   result = value
        ,   fv = Math.round(value * 1E3) / 1E3
        _.find(s125, function(v){
            return ( result = v ) >= fv
        })
        return result
    }

    function beautifulRound(value) {
        value = Math.round(value * 1E3) / 1E3
        if ( value ) {
            var s125 = space125(value)
            ,   rate = Math.round(value / s125 * 10) / 10
            return rate * s125
        } else {
            return 0
        }
    }

    function beautifulCeil(value) {
        value = Math.round(value * 1E3) / 1E3
        if ( value ) {
            var s125 = space125(value)
            ,   rate = Math.round(value / s125 * 10) / 10
            ,   result = rate * s125
            if ( result < value ) {
                result += s125 * 0.1
            }
            return result
        } else {
            return 0
        }
    }

    function beautifulFloor(value) {
        value = Math.round(value * 1E3) / 1E3
        if ( value ) {
            var s125 = space125(value)
            ,   rate = Math.round(value / s125 * 10) / 10
            ,   result = rate * s125
            if ( result > value ) {
                result -= s125 * 0.1
            }
            return result
        } else {
            return 0
        }
    }

    function initMarkers(start, end, options){
        var settings = _.extend({
                    scale: [0, 25, 50, 75, 100]
                }, options)
        ,   result = []
        ,   scale = settings.scale
        ,   j = scale.length - 1
            // position will be between 0 and 100
        ,   minp = scale[0]
        ,   maxp = scale[j]
            // The result should be inside range
        ,   shift = start < 0 ? 1 - start : 1
        ,   minv = Math.log(start + shift)
        ,   maxv = Math.log(end + shift)
            // calculate adjustment factor
        ,   factor = (maxv - minv) / (maxp - minp)
        for ( var i = 0; i <= j; i++ ) {
            var interval = scale[i]
            ,   value
            ,   raw = Math.exp(minv + factor * (interval - minp)) - shift
            if ( i == 0 ) {
                value = beautifulFloor(raw)
            } else if ( i != j ) {
                value = beautifulRound(raw)
            } else {
                value = beautifulCeil(raw)
            }
            result.push({
                interval: interval
            ,   value: value
            ,   label: value
            })
        }
        if ( result[0].value != start ){
            result[0].label = '<'
        }
        if ( result[j].value != end ){
            result[j].label = '>'
        }
        return result
    }

    function getSliderScaleOptions(start, end, nice){
        var scale = []
        ,   heterogeneity = []
        ,   markers = initMarkers(start, end)
        ,   j = markers.length - 1
        ,   m

        for ( var i = 0; i <= j; i++ ) {
            m = markers[i]
            scale.push(_.isNumber(m.label) ? nice(m.label) : m.label)
        }
        for ( var i = 1; i < j; i++ ) {
            m = markers[i]
            heterogeneity.push(m.interval + '/' + m.value)
        }

        return {
            'scale': scale
        ,   'heterogeneity': heterogeneity
        }
    }


    // Price View
    // ----------
    var PriceView = Backbone.StatefulView.extend({

        // Cache the template function for a single item.
        initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

    ,   initialize: function(options) {

            this.initializeTemplate()

            var that = this
            ,   model = this.model
            ,   sliderOptions = options && options.sliderOptions || {}

            ,   limits = model.get('limit')
            ,   start = limits[0]
            ,   end = limits[1]
            ,   format = sliderOptions.format
            ,   value = model.get('value') ? model.get('value').join(';') : limits.join(';')


            this.nice = $.formatNumber ?
                    function( value ){ return $.formatNumber( new Number(value), format || {} ).replace( /-/gi, "&minus;" ) } :
                    function( value ){ return new Number(value) }

            sliderOptions = _.extend(sliderOptions, getSliderScaleOptions(start, end, this.nice), {
                value: value
            ,   from: start
            ,   to: end
            ,   limits: false
            ,   labels: true
            ,   template: that.template
            ,   callback: function( value ){
                    var range
                    if ( !_.isNull(value) ) {
                        range = value.split(";")
                        range[0] = Number(range[0])
                        if (range.length < 2) {
                            range.push(range[0])
                        } else {
                            range[1] = Number(range[1])
                        }
                    } else {
                        range = null
                    }
                    model.set({value: range}, {setterObj: that})
                }
            })

            this.$slider = this.$el.slider(sliderOptions);

            model.on('change:value', function(model, value, options){
                if (!options || !_.has(options, 'setterObj') || options.setterObj != this) {
                    var range = this.model.get('value')
                    if ( range ) {
                        this.$slider.slider('value', range[0], range[1])
                    }
                }

            }, this)

            model.on('change:limit', function(model, value, options){
                var sliderOptions = getSliderScaleOptions(value[0], value[1], this.nice)
                this.$slider.slider("limit", value[0], value[1])

                this.$slider.slider("scale", sliderOptions["scale"])
                this.$slider.slider("heterogeneity", sliderOptions["heterogeneity"])

            }, this)


            this.trigger('initialized')
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

        name: "PriceView"

    ,   views: {
            PriceView: PriceView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);