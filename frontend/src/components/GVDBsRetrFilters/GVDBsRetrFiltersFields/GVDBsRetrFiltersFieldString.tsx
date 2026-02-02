import { Form, InputGroup } from "react-bootstrap";
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
  return (
    <InputGroup className="mb-2">
      <InputGroup.Text
        className={"fw-bold justify-content-end bg-tc-300"}
        style={{ width: "16ch" }}
      >
        {field.title}
      </InputGroup.Text>
      <Form.Control
        type="string"
        className="fw-bold"
        value={value || ""}
        onChange={(e) => onChange(field.rf_field_id, e.target.value)}
      />
    </InputGroup>
  );
}
