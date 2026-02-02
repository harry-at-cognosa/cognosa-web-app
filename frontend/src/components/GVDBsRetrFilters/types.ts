interface GVDBsRetrFiltersFieldBase {
  title: string;
  path: string;
  sub_type?: string | null;
  rf_field_id: string;
}

interface GVDBsRetrFiltersStringField extends GVDBsRetrFiltersFieldBase {
  type: "string";
  max_length: number;
}

interface GVDBsRetrFiltersSelectField extends GVDBsRetrFiltersFieldBase {
  type: "select";
  values: string[];
  max_select: number; // -1 means unlimited, otherwise >= 1 (validated on backend)
}

export type GVDBsRetrFiltersField =
  | GVDBsRetrFiltersStringField
  | GVDBsRetrFiltersSelectField;

export interface GVDBsRetrFiltersSchema {
  global_not_enabled: boolean;
  fields: GVDBsRetrFiltersField[];
}

export interface GVDBsRetrFiltersState {
  global_not_enabled: boolean | null;
  fields: GVDBsRetrFiltersField[] | null;
  setDataFromString: (gvdbs_def_retr_filters: string) => void;
}

export interface GVDBsRetrFiltersLoaded {
  isLoaded: boolean;
  setIsLoaded: (isLoaded: boolean) => void;
}

export interface GVDBsRetrFiltersValuesEntry {
  rf_field_id: string;
  values_list: string[];
}

export interface DocTasksGVDBsRetrFiltersRequest {
  global_not_value?: boolean;
  values: GVDBsRetrFiltersValuesEntry[];
}
