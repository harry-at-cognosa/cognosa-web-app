import { Container, Form } from "react-bootstrap";
import type { createTableStore, TableCellValue } from "../TableStoreFactory";
import { Check, XCircle } from "react-bootstrap-icons";
import ApiSettingsValue from "../EditRenders/ApiSettingsValue";
import EditCellGVDBDefRetrParams from "../EditRenders/EditCellGVDBDefRetrParams";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  col: string;
}

export default function EditCellElement({ useStore, col }: Props) {
  const tableStore = useStore();
  if (!tableStore.data) return null;
  const columns = tableStore.data.columns;
  if (!(columns && tableStore.editRow)) return null;
  const editRowErrorMark = tableStore.editRowErrorMark[col];
  const isInvalid = tableStore.showCreateOrUpdateDialog
    ? editRowErrorMark
    : false;
  const value = tableStore.editRow[col];
  const value_str = value?.toString() || "";
  const cellType = columns[col].type;
  function onChange(value: TableCellValue) {
    tableStore.setEditRow({ ...tableStore.editRow, [col]: value });
    if (editRowErrorMark) tableStore.setEditRowErrorMark(col, false);
  }
  const key = "edit_cell_element__" + col;
  const dummy_username = ["email", "user_name", "username", "user"].includes(
    col,
  ) ? (
    <input
      type="text"
      style={{ display: "none", position: "absolute" }}
      autoComplete="username"
    />
  ) : null;

  if (cellType === "boolean")
    return (
      <div key={"div_boolean__" + key} className="d-flex">
        <Form.Check
          type="switch"
          checked={!!value}
          key={"check_boolean__" + key}
          className="ms-2"
          onChange={(e) => onChange(e.target.checked)}
          autoComplete="off"
        ></Form.Check>
        {Boolean(value) ? (
          <Check size={"24px"} style={{ color: "green" }}></Check>
        ) : (
          <XCircle size={"24px"} style={{ color: "red" }}></XCircle>
        )}
      </div>
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
          isInvalid={isInvalid}
        />
      );
    else
      return (
        <Form.Select
          value={value_str}
          onChange={(e) => onChange(Number(e.target.value))}
          autoComplete="off"
          isInvalid={isInvalid}
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
            isInvalid={isInvalid}
          />
        </>
      );
    else
      return (
        <Form.Select
          value={value_str}
          onChange={(e) => onChange(e.target.value)}
          autoComplete="off"
          isInvalid={isInvalid}
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
        isInvalid={isInvalid}
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
        isInvalid={isInvalid}
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
    return (
      <ApiSettingsValue onChange={onChange} useStore={useStore} col={col} />
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
          isInvalid={isInvalid}
        />
      </>
    );
  }
  if (cellType === "gvdbs_retr_params") {
    return (
      <Container style={{ padding: "20px" }}>
        <EditCellGVDBDefRetrParams
          valueStr={value_str}
          onChange={(newValueStr) => onChange(newValueStr)}
        />
      </Container>
    );
  }
  if (cellType === "gvdbs_retr_filters")
    return (
      <Form.Control
        as="textarea"
        value={value as string}
        key={key}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        autoComplete="off"
        isInvalid={isInvalid}
      ></Form.Control>
    );
  return value?.toString();
}
