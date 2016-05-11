{% extends 'publication_backbone/catalog/_app.js' %}


{% block module_name %}PromotionApplication{% endblock %}


{% block catalog_router_uses %}{% endblock %}


{% block rubricator_uses %}{% endblock %}


{% block catalog_item_view %}{{ block.super }}

            CatalogItemView = CatalogItemView.extend({
                doOpen: function() {
                    var model = this.model.getJSON()
                    if ( model.variants > 1 ) {
                        document.location.href = model.catalog_base_uri
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
            })

{% endblock %}


{% block rubricator_event_listener %}{% endblock %}


{% block category_event_listener %}{% endblock %}


{% block catalog_router_init %}{% endblock %}