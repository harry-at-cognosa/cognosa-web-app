import { Form } from "react-bootstrap";
import type { createTableStore, TableCellValue } from "../TableStoreFactory";
import EditCellGVDBDefRetrParams from "./EditCellGVDBDefRetrParams";
import getColor from "../../api/getColor";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  col: string;
  onChange: (value: TableCellValue) => void;
}

export default function ApiSettingsValue({ onChange, useStore, col }: Props) {
  const tableStore = useStore();
  const { editRow, data } = tableStore;
  if (!(editRow && data)) return null;
  const editRowErrorMark = tableStore.editRowErrorMark[col];
  const isInvalid = tableStore.showCreateOrUpdateDialog
    ? editRowErrorMark
    : false;
  const pk_value_str = editRow["name"]?.toString() || "";
  const value = editRow[col];
  const value_str = value?.toString() || "";
  const key = "edit_cell_element__" + col;

  if (pk_value_str === "webapp_main_color") {
    const all_values = data.table_options.add_values[
      "webapp_main_color_values"
    ] as string[];
    return (
      <Form.Select
        value={value_str}
        onChange={(e) => onChange(e.target.value)}
        autoComplete="off"
        isInvalid={isInvalid}
      >
        {all_values.map((color) => (
          <option
            key={key + "__" + color}
            value={color}
            style={{ backgroundColor: getColor(color, 300) }}
          >
            {color}
          </option>
        ))}
      </Form.Select>
    );
  }
  if (pk_value_str === "gvdbs_def_retr_params") {
    return (
      <EditCellGVDBDefRetrParams
        valueStr={value_str}
        onChange={(newValueStr) => onChange(newValueStr)}
      />
    );
  }

  return (
    <Form.Control
      as="textarea"
      value={value_str}
      key={key}
      onChange={(e) => onChange(e.target.value)}
      rows={3}
      autoComplete="off"
      isInvalid={isInvalid}
    ></Form.Control>
  );
}
