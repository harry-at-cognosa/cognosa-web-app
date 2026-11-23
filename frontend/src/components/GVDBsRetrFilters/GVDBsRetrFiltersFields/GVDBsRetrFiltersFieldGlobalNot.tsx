import { Switch } from "@/components/ui/switch";

interface FieldProps {
  value: boolean | null;
  onChange: (name: string, value: string) => void;
}

export default function GVDBsRetrFiltersFieldGlobalNot({
  value,
  onChange,
}: FieldProps) {
  if (value === null) return null;
  return (
    <label className="flex items-center gap-2 text-sm font-semibold">
      <Switch
        checked={value}
        onCheckedChange={(checked) =>
          onChange("global_not_value", checked ? "1" : "")
        }
      />
      NOT:
    </label>
  );
}
