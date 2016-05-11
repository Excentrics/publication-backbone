{% load publication_backbone_tags %}
{% include "publication_backbone/promotion/_app.js" with name=name object_list=object_list page_obj=page_obj category=category order_by=order_by ordering_modes=ordering_modes rubricator_name=rubricator_name ranges=ranges publication_group=publication_group set=set subj=subj rel=rel thumbnail_geometry=thumbnail_geometry thumbnail_width=thumbnail_width thumbnail_height=thumbnail_height thumbnail_background=thumbnail_background potential_rubrics_ids=potential_rubrics_ids real_rubrics_ids=real_rubrics_ids today=today only %}

