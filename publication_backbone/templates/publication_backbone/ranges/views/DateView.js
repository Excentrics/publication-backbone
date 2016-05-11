{% load i18n beautiful_fields_tags %}
(function($, Backbone, _) {

    "use strict";

    // Utils
    // ----------

    function initMarkers(start, end, today, options){
        var scale = [
                "{% trans 'now' %}"
            ,   "{% trans 'week' %}<sup title='{% trans 'week ago' %}'><i class='fa fa-history'></i></sup>"
            ,   "{% trans 'month' %}<sup title='{% trans 'month ago' %}'><i class='fa fa-history'></i></sup>"
            ,   "{% trans 'year' %}<sup title='{% trans 'year ago' %}'><i class='fa fa-history'></i></sup>"
            ,   "{% trans 'past' %}"
        ]
        ,   degrees = [604800, 2592000, 31536000]
        ,   future_shift = today-start

        if (future_shift > 0) {
            scale.unshift("{% trans 'future' %}")
            degrees.unshift(0)
            for ( var i = 0; i < degrees.length; i++ ) { degrees[i] = degrees[i] + future_shift }
        }

        var
            settings = _.extend({
                    scale: scale,
                }, options)
        ,   result = []
        ,   scale = settings.scale
        ,   sl = scale.length - 1
        ,   dl = degrees.length - 1
            // position will be between 0 and 100
        ,   minp = scale[0]
        ,   maxp = scale[sl]

        // The result should be inside range
        result.push({
                interval: 0
            ,   value: start
            ,   label: scale[0]
            })
            for ( var i = 0; i <= dl; i++ ) {
                if (start + degrees[i] <= end){
                    result.push({
                        interval: 0
                    ,   value: start + degrees[i]
                    ,   label: scale[i + 1]
                    })
                }
            }

        result.push({
                interval: 100
            ,   value: end
            ,   label: scale[sl]
            })

        var rl =  result.length - 1
        ,   k = 100.0 / rl

        for ( var i = 1; i < rl; i++ ) {
            result[i].interval = Math.floor(k * i)
        }

        return result
    }

    function getSliderScaleOptions(start, end, today, nice){
        var scale = []
        ,   heterogeneity = []
        ,   markers = initMarkers(start, end, today)
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


    // Date View
    // ----------
    var DateView = Backbone.StatefulView.extend({

        // Cache the template function for a single item.
        initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

    ,   initialize: function(options) {

            this.initializeTemplate()

            var that = this
            ,   model = this.model
            ,   sliderOptions = options && options.sliderOptions || {}
            ,   today = model.get('today')
            ,   limits = model.get('limit')
            ,   start = limits[0]
            ,   end = limits[1]
            ,   format = sliderOptions.format
            ,   value = model.get('value') ? model.get('value').join(';') : limits.join(';')


            this.nice = $.formatNumber ?
                    function( value ){ return $.formatNumber( new Number(value), format || {} ).replace( /-/gi, "&minus;" ) } :
                    function( value ){ return new Number(value) }

            sliderOptions = _.extend(sliderOptions, getSliderScaleOptions(start, end, today, this.nice), {
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
            ,   calculate: function( raw_value ){
                    var value = (-1)*raw_value
                    ,   dateTime = new Date(parseInt(value, 10) * 1000)
                    ,   hours = "0" + dateTime.getHours()
                    ,   minutes = "0" + dateTime.getMinutes()
                    ,   day = "0" + dateTime.getDate()
                    ,   month = "0" + (dateTime.getMonth() + 1)
                    ,   year = dateTime.getFullYear()
                    return day.substr(-2) + '.' + month.substr(-2) + '.' + year +
                            '<sup>&nbsp;' + hours.substr(-2) + ':' + minutes.substr(-2) + '</sup>'
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

        name: "DateView"

    ,   views: {
            DateView: DateView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);