import { Sel } from "@/components/Sel";
import type { GVDBsRetrFiltersField } from "../types";

interface FieldProps {
  field: GVDBsRetrFiltersField;
  value: string;
  onChange: (name: string, value: string) => void;
}

// a field that holds a value is tinted, so set filters stand out in the form
const SET_MARK = "border-tint-edge bg-tint font-semibold text-tint-fg";

export default function GVDBsRetrFiltersFieldSelect({
  field,
  value,
  onChange,
}: FieldProps) {
  if (field.type !== "select") return null;
  const { rf_field_id, title, values } = field;
  const id = `rf-${rf_field_id}`;
  const isSet = Boolean(value && value.trim());
  return (
    <div className="min-w-0">
      <label className="lbl" htmlFor={id}>
        {title}
      </label>
      <Sel
        id={id}
        label={title}
        value={value || ""}
        onChange={(v) => onChange(rf_field_id, v)}
        // the empty item clears the filter (v1.0.1: the blank first option)
        emptyLabel=""
        options={values.map((v) => ({ value: v, label: v }))}
        className={isSet ? SET_MARK : undefined}
      />
    </div>
  );
}
