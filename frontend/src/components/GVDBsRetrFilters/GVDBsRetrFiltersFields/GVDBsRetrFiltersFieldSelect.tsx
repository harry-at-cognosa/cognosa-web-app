import { Form, InputGroup } from "react-bootstrap";
import type { GVDBsRetrFiltersField } from "../types";

interface FieldProps {
  field: GVDBsRetrFiltersField;
  value: string;
  onChange: (name: string, value: string) => void;
}

export default function GVDBsRetrFiltersFieldSelect({
  field,
  value,
  onChange,
}: FieldProps) {
  if (field.type !== "select") return null;
  const { rf_field_id, title, values } = field;
  const allValues = ["", ...values];
  return (
    <InputGroup className="mb-2">
      <InputGroup.Text
        className={"fw-bold justify-content-end bg-tc-300"}
        style={{ width: "16ch" }}
      >
        {title}
      </InputGroup.Text>
      <Form.Select
        className="fw-bold"
        value={value}
        onChange={(e) => onChange(rf_field_id, e.target.value)}
        autoComplete="off"
      >
        {allValues.map((value) => (
          <option key={`rffs__${rf_field_id}__option__${value}`} value={value}>
            {value}
          </option>
        ))}
      </Form.Select>
    </InputGroup>
  );
}
