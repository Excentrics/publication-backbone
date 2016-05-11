// RubricItem
{% include "publication_backbone/rubricator/models/RubricItem.js" %}

// RubricItemList
{% include "publication_backbone/rubricator/collections/RubricItemsList.js" %}

// RubricItemView
{% include "publication_backbone/rubricator/views/RubricItemView.js" with rubricator_name=rubricator_name only %}

// RubricatorView
{% include "publication_backbone/rubricator/views/RubricatorView.js" with rubricator_name=rubricator_name only %}
