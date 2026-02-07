from typing import Literal
from qdrant_client.models import Filter, FieldCondition, MatchText, MatchValue, Condition
from common.features.gvdbs_retr_filters import RequestGVDBsRetrFiltersValuesEntry, RunTasksGVDBsRetrFilters


class QdrantFilters:
    def __init__(self, retr_filters: RunTasksGVDBsRetrFilters):
        self.retr_filters = retr_filters
        self.global_not_value = bool(self.retr_filters.global_not_value)
        self.common_entries: list[RequestGVDBsRetrFiltersValuesEntry] = []
        # Ledra specific entries and values:
        self.ledra_base_alt: Literal['', 'base', 'alt'] = ''
        self.ledra_entries: list[RequestGVDBsRetrFiltersValuesEntry] = []

        self._choose_specific_filter_entries()

    def _choose_specific_filter_entries(self):
        for entry in self.retr_filters.values:
            rf_field_id = entry.rf_field_id
            field = self.retr_filters.rf_field_id__field.get(rf_field_id)
            values_list = entry.values_list
            
            if (field is None) or (not values_list):
                continue
            if field.sub_type and field.sub_type.startswith('ledra_'):
                self.ledra_entries.append(entry)
                if field.sub_type == "ledra_base_alt":
                    if entry.values_list == ['base']:
                        self.ledra_base_alt = "base"                        
                    elif entry.values_list == ['alt']:
                        self.ledra_base_alt = "alt"
            else:
                self.common_entries.append(entry)

    def _get_common_conditions(self) -> list[Condition]:
        # Get list of common (not specific) conditions
        conditions: list[Condition] = []
        for entry in self.common_entries:
            field = self.retr_filters.rf_field_id__field[entry.rf_field_id]
            values_list = entry.values_list
            # Multiple values - create OR logic using should
            or_conditions: list[Condition] = []
            for value in values_list:
                if field.type == 'string':
                    or_conditions.append(
                        FieldCondition(
                            key=field.path, 
                            match=MatchText(text=value)
                        )
                    )
                elif field.type == 'select':
                    or_conditions.append(
                        FieldCondition(
                            key=field.path, 
                            match=MatchValue(value=value)
                        )
                    )
            # Combine with OR logic
            if or_conditions:
                conditions.append(Filter(should=or_conditions))
            
        return conditions

    def convert_from_retr_filters(self) -> Filter | None:
        """
        Convert RunTasksGVDBsRetrFilters to Qdrant Filter object.
        """
        if not self.retr_filters or not self.retr_filters.values:
            return None
        conditions: list[Condition] = self._get_common_conditions()
        conditions.extend(self._get_specific_conditions__ledra())

        if not conditions:
            return None
        
        # Apply global NOT logic if needed
        if self.global_not_value:
            # Use must_not to negate all conditions
            return Filter(must_not=conditions)
        else:
            # Use must to require all conditions (AND logic between different fields)
            return Filter(must=conditions)

    
    def _get_specific_conditions__ledra(self) -> list[Condition]:
        """
        Get specific conditions for Ledra.
        
        1) if sub_type = "ledra_base_alt" then:
        1.1) if values_list = ["base"] it will use documents with key not exists/filled: metadata.alt_product_id
        1.2) if values_list = ["alt"] it will use documents with key filled: metadata.alt_product_id
        1.3) ignore other values_list variants

        2) if sub_type = "ledra_product_id" then:
        2.1) if ledra_base_alt mentioned before is base, then use key="metadata.base_product_id"
        2.2) if ledra_base_alt mentioned before is alt, then use key="metadata.alt_product_id"
        2.3) in other cases, use both keys "metadata.base_product_id" "metadata.alt_product_id" as OR clause.
        """
        conditions = []
        base_and_alt = self.ledra_base_alt == ''
        only_base = self.ledra_base_alt == 'base'
        only_alt = self.ledra_base_alt == 'alt'
        ### Base/Alt switch:
        if only_base:  # Documents where metadata.alt_product_id not exists or empty
            condition = FieldCondition(
                key="metadata.alt_product_id",
                is_empty=True
            )
            conditions.append(condition)
        elif only_alt:  # Documents where metadata.alt_product_id exists and is filled
            condition = FieldCondition(
                key="metadata.alt_product_id",
                is_empty=False
            )
            conditions.append(condition)
        
        for entry in self.ledra_entries:
            rf_field_id = entry.rf_field_id
            field = self.retr_filters.rf_field_id__field[rf_field_id]
            values_list = entry.values_list
            if field.sub_type == "ledra_base_alt":  # already checked
                continue
            
            # Handle ledra_product_id special case
            elif field.sub_type == "ledra_product_id":
                # use metadata -> "base_product_id" or "alt_product_id" or both
                field_path_list: list[str] = []
                if base_and_alt or only_base:
                    field_path_list.append("metadata.base_product_id")
                if base_and_alt or only_alt:
                    field_path_list.append("metadata.alt_product_id")
                # Multiple values - create OR logic using should
                or_conditions: list[Condition] = []
                for field_path in field_path_list:
                    for value in values_list:
                        or_conditions.append(
                            FieldCondition(
                                key=field_path, 
                                match=MatchText(text=value)
                            )
                        )
                # Combine with OR logic
                if or_conditions:
                    conditions.append(Filter(should=or_conditions))
                
        return conditions