import { useDefaultGVDBsRetrFiltersStore } from "./useDefaultGVDBsRetrFiltersStore";
import { useModalGVDBsRetrFiltersStore } from "./useModalGVDBsRetrFiltersStore";
import type { GVDBsRetrFiltersField } from "./types";
import GVDBsRetrFiltersFieldString from "./GVDBsRetrFiltersFields/GVDBsRetrFiltersFieldString";
import GVDBsRetrFiltersFieldSelect from "./GVDBsRetrFiltersFields/GVDBsRetrFiltersFieldSelect";
import GVDBsRetrFiltersFieldGlobalNot from "./GVDBsRetrFiltersFields/GVDBsRetrFiltersFieldGlobalNot";

interface FieldProps {
  field: GVDBsRetrFiltersField;
  valueList: string[];
  onChange: (name: string, value: string) => void;
}

function FieldList({ field, valueList, onChange }: FieldProps) {
  if (field.type === "string") {
    // make single string for now
    return (
      <GVDBsRetrFiltersFieldString
        field={field}
        value={valueList[0] || ""}
        onChange={onChange}
      />
    );
  }
  if (field.type === "select") {
    return (
      <GVDBsRetrFiltersFieldSelect
        field={field}
        value={valueList[0]}
        onChange={onChange}
      />
    );
  }

  return null;
}

export default function GVDBsRetrFilters() {
  const defStore = useDefaultGVDBsRetrFiltersStore();
  const modalStore = useModalGVDBsRetrFiltersStore();
  const { global_not_enabled, fields } = defStore;
  const { global_not_value, rf_field_id__values } = modalStore;
  if (
    !(
      defStore.isLoaded &&
      modalStore.isLoaded &&
      global_not_enabled !== null &&
      fields !== null
    )
  )
    return null;

  function onChange(name: string, value: string) {
    if (name === "global_not_value")
      modalStore.setGlobalNotValue(Boolean(value));
    else {
      modalStore.setValues({
        ...rf_field_id__values,
        [name]: [value.toString()],
      });
    }
  }

  return (
    <div>
      {global_not_enabled ? (
        <div className="mb-2.5 flex justify-end">
          <GVDBsRetrFiltersFieldGlobalNot
            value={global_not_value}
            onChange={onChange}
          />
        </div>
      ) : null}
      <div className="grid grid-cols-1 gap-x-3.5 gap-y-2.5 sm:grid-cols-2">
        {fields.map((field) => (
          <FieldList
            key={"rffl__" + field.rf_field_id}
            field={field}
            valueList={rf_field_id__values[field.rf_field_id] || []}
            onChange={onChange}
          />
        ))}
      </div>
    </div>
  );
}
