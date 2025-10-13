import { Form } from "react-bootstrap";
import type { createTableStore, TableCellValue } from "../TableStoreFactory";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  col: string;
}

export default function EditCellElement({ useStore, col }: Props) {
  const tableStore = useStore();
  const columns = tableStore.data?.columns;
  if (!(columns && tableStore.editRow)) return null;
  const value = tableStore.editRow[col];
  const cellType = columns[col].type;
  function onChange(value: TableCellValue) {
    tableStore.setEditRow({ ...tableStore.editRow, [col]: value });
  }
  const key = "edit_cell_element__" + col;

  if (cellType === "boolean")
    return (
      <Form.Check
        checked={!!value}
        key={key}
        onChange={(e) => onChange(e.target.checked)}
      ></Form.Check>
    );
  if (cellType === "number")
    return (
      <Form.Control
        type="number"
        value={value as string | number}
        key={key}
        onChange={(e) => onChange(parseFloat(e.target.value) || null)}
      />
    );
  if (cellType === "string")
    return (
      <Form.Control
        type="text"
        value={value as string}
        key={key}
        onChange={(e) => onChange(e.target.value)}
      />
    );
  if (cellType === "text")
    return (
      <Form.Control
        as="textarea"
        value={value as string}
        key={key}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
      ></Form.Control>
    );
  return value?.toString();
}
