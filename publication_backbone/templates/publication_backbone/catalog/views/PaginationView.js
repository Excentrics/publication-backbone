(function($, Backbone, _) {

    "use strict";

    var name_prefix = '{{ name }}'

    // The Pagination View
    // ---------------

    var PaginationView = Backbone.StatefulView.extend({

        template: '#' + name_prefix + '-app-template'

        // Cache the template function for a single item.
    ,   initializeTemplate: function() {
            this.template = _.template($(this.template).html());
        }

        // Digg-style pagination settings
    ,   leadingPageRangeDisplayed: 8
    ,   trailingPageRangeDisplayed: 8
    ,   leadingPageRange: 6
    ,   trailingPageRange: 6
    ,   numPagesOutsideRange: 2
    ,   adjacentPages: 2

    ,   events: {
            'click .js-prev': 'gotoPrev'
        ,   'click .js-next': 'gotoNext'
        ,   'click .js-page': 'gotoPage'
        ,   'click .ex-js-ignore': 'ignore'
        }

    ,   initialize: function(options) {
            this.initializeTemplate()
            this.trigger('initialized')
            this.collection.on('reset update collection:change:offset', this.render, this)
        }

    ,   render: function() {
            var inLeadingRange = false
            ,   inTrailingRange = false
            ,   pagesOutsideLeadingRange = _.range(0)
            ,   pagesOutsideTrailingRange = _.range(0)
            ,   currentPage = this.collection.getCurrentPage()
            ,   numPages = this.collection.getPageCount()
            ,   pageNumbers
            if ( numPages <= this.leadingPageRangeDisplayed + this.numPagesOutsideRange + 1 ) {
                inLeadingRange = inTrailingRange = true
                pageNumbers = _.filter(_.range(1, numPages + 1), function(n){
                    return n > 0 && n <= numPages
                })
            } else if ( currentPage <= this.leadingPageRange ) {
                inLeadingRange = true
                pageNumbers = _.filter(_.range(1, this.leadingPageRangeDisplayed + 1), function(n){
                    return n > 0 && n <= numPages
                })
                pagesOutsideLeadingRange = _.map(_.range(0, -1 * this.numPagesOutsideRange, -1), function(n){
                    return n + numPages
                })
            } else if ( currentPage > numPages - this.trailingPageRange ) {
                inTrailingRange = true
                pageNumbers = _.filter(_.range(numPages - this.trailingPageRangeDisplayed + 1, numPages + 1), function(n){
                    return n > 0 && n <= numPages
                })
                pagesOutsideTrailingRange = _.map(_.range(0, this.numPagesOutsideRange), function(n){
                    return n + 1
                })
            } else {
                pageNumbers = _.filter(_.range(currentPage - this.adjacentPages, currentPage + this.adjacentPages + 1), function(n){
                    return n > 0 && n <= numPages
                })
                pagesOutsideLeadingRange = _.map(_.range(0, -1 * this.numPagesOutsideRange, -1), function(n){
                    return n + numPages
                })
                pagesOutsideTrailingRange = _.map(_.range(0, this.numPagesOutsideRange), function(n){
                    return n + 1
                })
            }

            var context = {
                hasNext: this.collection.hasNext()
            ,   hasPrevious: this.collection.hasPrevious()
            ,   pageNumbers: pageNumbers
            ,   currentPage: currentPage
            ,   inLeadingRange: inLeadingRange
            ,   pagesOutsideTrailingRange: pagesOutsideTrailingRange
            ,   inTrailingRange: inTrailingRange
            ,   pagesOutsideLeadingRange: pagesOutsideLeadingRange
            //{% comment %},   $parent: this.$el{% endcomment %}
            }
            this.$el.html(this.template(context))
            return this
        }

    ,   gotoPrev: function() {
            this.collection.previousPage()
            return false
        }

    ,   gotoNext: function() {
            this.collection.nextPage()
            return false
        }

    ,   gotoPage: function(e) {
            e.preventDefault()
            var page = $(e.currentTarget).data('page')
            this.collection.gotoPage(page)
        }

    ,   ignore: function(e) {
            return false
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

        name: "PaginationView"

    ,   views: {
            PaginationView: PaginationView
        }

    })

    var App = new Module()

})(jQuery, Backbone, _);