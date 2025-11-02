import { Form } from "react-bootstrap";
import type { createTableStore, TableCellValue } from "../TableStoreFactory";
import getColor from "../../api/getColor";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  col: string;
}

export default function EditCellElement({ useStore, col }: Props) {
  const tableStore = useStore();
  if (!tableStore.data) return null;
  const columns = tableStore.data.columns;
  if (!(columns && tableStore.editRow)) return null;
  const value = tableStore.editRow[col];
  const value_str = value?.toString() || "";
  const cellType = columns[col].type;
  function onChange(value: TableCellValue) {
    tableStore.setEditRow({ ...tableStore.editRow, [col]: value });
  }
  const key = "edit_cell_element__" + col;
  const dummy_username = ["email", "user_name", "username", "user"].includes(
    col
  ) ? (
    <input
      type="text"
      style={{ display: "none", position: "absolute" }}
      autoComplete="username"
    />
  ) : null;

  if (cellType === "boolean")
    return (
      <Form.Check
        checked={!!value}
        key={key}
        className="ms-2"
        onChange={(e) => onChange(e.target.checked)}
        autoComplete="off"
      ></Form.Check>
    );
  if (cellType === "number") {
    const select_values = columns[col].select;
    if (select_values === null)
      return (
        <Form.Control
          type="number"
          value={value as string | number}
          key={key}
          onChange={(e) => onChange(parseFloat(e.target.value) || null)}
          autoComplete="off"
        />
      );
    else
      return (
        <Form.Select
          value={value_str}
          onChange={(e) => onChange(Number(e.target.value))}
          autoComplete="off"
        >
          {select_values.map((row) => (
            <option key={row.value.toString()} value={row.value.toString()}>
              {row.name}
            </option>
          ))}
        </Form.Select>
      );
  }
  if (cellType === "string") {
    const select_values = columns[col].select;
    if (select_values === null)
      return (
        <>
          {dummy_username}
          <Form.Control
            type="text"
            value={(value === null ? "" : value) as string}
            key={key}
            onChange={(e) => onChange(e.target.value)}
            autoComplete="off"
          />
        </>
      );
    else
      return (
        <Form.Select
          value={value_str}
          onChange={(e) => onChange(e.target.value)}
          autoComplete="off"
        >
          {select_values.map((row) => (
            <option key={row.value.toString()} value={row.value.toString()}>
              {row.name}
            </option>
          ))}
        </Form.Select>
      );
  }
  if (cellType === "text")
    return (
      <Form.Control
        as="textarea"
        value={value as string}
        key={key}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        autoComplete="off"
      ></Form.Control>
    );
  if (cellType === "group_id_name") {
    const select_group_id_name = columns["group_id"].select;
    if (!select_group_id_name || !select_group_id_name.length)
      return <h3 style={{ color: "red" }}>No groups found!</h3>;
    return (
      <Form.Select
        value={value_str}
        onChange={(e) => onChange(Number(e.target.value))}
        autoComplete="off"
      >
        {select_group_id_name.map((gin) => (
          <option key={gin.value.toString()} value={gin.value.toString()}>
            {gin.name}
          </option>
        ))}
      </Form.Select>
    );
  }
  if (cellType === "api_settings_value") {
    const pk_value_str = tableStore.editRow["name"]?.toString() || "";
    if (pk_value_str === "webapp_main_color") {
      const all_values = tableStore.data.table_options.add_values[
        "webapp_main_color_values"
      ] as string[];
      return (
        <Form.Select
          value={value_str}
          onChange={(e) => onChange(e.target.value)}
          autoComplete="off"
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

    return (
      <Form.Control
        as="textarea"
        value={value_str}
        key={key}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        autoComplete="off"
      ></Form.Control>
    );
  }

  if (cellType === "groupadmin_user_password") {
    return (
      <>
        <input
          type="password"
          style={{ display: "none", position: "absolute" }}
          autoComplete="new-password"
        />
        <Form.Control
          type="password"
          value={(value === null ? "" : value) as string}
          key={key}
          onChange={(e) => onChange(e.target.value)}
          autoComplete="off"
        />
      </>
    );
  }

  return value?.toString();
}
