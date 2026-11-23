import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { GVDBsRetrFiltersField } from "../types";

interface FieldProps {
  field: GVDBsRetrFiltersField;
  value: string;
  onChange: (name: string, value: string) => void;
}

export default function GVDBsRetrFiltersFieldString({
  field,
  value,
  onChange,
}: FieldProps) {
  const id = `rf-${field.rf_field_id}`;
  const isSet = Boolean(value && value.trim());
  return (
    <div className="min-w-0">
      <label className="lbl" htmlFor={id}>
        {field.title}
      </label>
      <Input
        id={id}
        type="text"
        value={value || ""}
        onChange={(e) => onChange(field.rf_field_id, e.target.value)}
        className={cn(
          isSet && "border-tint-edge bg-tint font-semibold text-tint-fg",
        )}
      />
    </div>
  );
}
