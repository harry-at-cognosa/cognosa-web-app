import { Form } from "react-bootstrap";

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
    <Form.Check
      type="switch"
      className="fw-bold"
      label="NOT:"
      checked={value}
      onChange={(e) =>
        onChange("global_not_value", e.target.checked ? "1" : "")
      }
    />
  );
}
