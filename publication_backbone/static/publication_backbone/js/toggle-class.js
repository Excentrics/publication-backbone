/**
 * Created by pc on 20.01.2016.
 */
(function($, Backbone, _) {

    // The Module
    // --------------

    var Module = BBNS.Module.extend({

        name: "ToggleClassApp"
    ,   defaults: {
            buttonSelector: ".adapted-version"
        ,   cookieString: "adapted_version"
        ,   elementSelector: "body"
        ,   toggleClass: "adapted"
        }

    ,   initialize: function(options){
            // init settings
            this.cookieString = options && options.cookieString || this.defaults.cookieString
            this.elementSelector = options && options.elementSelector || this.defaults.elementSelector
            this.toggleClass = options && options.toggleClass || this.defaults.toggleClass
            this.cookie = BBNS.Cookie.get(this.cookieString)

            if (this.cookie!=undefined){

                this.current_state = this.cookie.get("value")=="true"? true : false

            }else{

                this.current_state = false
                BBNS.Cookie.add([{
                    name: this.cookieString,
                    value: false,
                    path: "/",
                    days: 14
                }])
                this.cookie = BBNS.Cookie.get(this.cookieString)

            }

            $(this.elementSelector).toggleClass(this.toggleClass, this.current_state==true)

        }

    ,   toggleState: function(){

            this.current_state = this.current_state==true ? false : true

            this.cookie.set({
                    value: this.current_state,
                    path: "/",
                    days: 14
                })

            this.cookie.save()

            $(this.elementSelector).toggleClass(this.toggleClass, this.current_state==true)

        }

    ,   addToggleButton : function(selector){

            var $el = $(selector)
                , that = this

            $el.on("click", function(event){
                that.toggleState()
                event.preventDefault()
            })
        }

    })

    // Finally, we kick things off by creating the **Module**.
    var App = new Module

})(jQuery, Backbone, _);