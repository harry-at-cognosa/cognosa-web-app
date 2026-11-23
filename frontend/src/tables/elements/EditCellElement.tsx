import { Check, CircleX } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Sel } from "@/components/Sel";
import type { createTableStore, TableCellValue } from "../TableStoreFactory";
import ApiSettingsValue from "../EditRenders/ApiSettingsValue";
import EditCellGVDBDefRetrParams from "../EditRenders/EditCellGVDBDefRetrParams";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  col: string;
}

// marks a Sel as invalid (it has no aria-invalid of its own)
export const SEL_INVALID = "border-destructive ring-3 ring-destructive/20";
// multi-line editors keep the row count they are given and can be dragged taller
export const TEXTAREA_CLASS = "field-sizing-fixed resize-y";

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
  const label = columns[col].display || col;
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
      <div key={"div_boolean__" + key} className="flex h-9 items-center gap-2.5">
        <Switch
          id={key}
          checked={!!value}
          key={"check_boolean__" + key}
          onCheckedChange={(checked) => onChange(checked)}
        ></Switch>
        {value ? (
          <Check className="size-5 text-ok" aria-label="yes"></Check>
        ) : (
          <CircleX className="size-5 text-err" aria-label="no"></CircleX>
        )}
      </div>
    );
  if (cellType === "number") {
    const select_values = columns[col].select;
    if (select_values === null)
      return (
        <Input
          id={key}
          type="number"
          value={(value ?? "") as string | number}
          key={key}
          onChange={(e) => onChange(parseFloat(e.target.value) || null)}
          autoComplete="off"
          aria-invalid={isInvalid || undefined}
          className="tabular-nums"
        />
      );
    else
      return (
        <Sel
          id={key}
          label={label}
          value={value_str}
          onChange={(v) => onChange(Number(v))}
          options={select_values.map((row) => ({
            value: row.value.toString(),
            label: row.name,
          }))}
          className={isInvalid ? SEL_INVALID : undefined}
        />
      );
  }
  if (cellType === "string") {
    const select_values = columns[col].select;
    if (select_values === null)
      return (
        <>
          {dummy_username}
          <Input
            id={key}
            type="text"
            value={(value === null || value === undefined ? "" : value) as string}
            key={key}
            onChange={(e) => onChange(e.target.value)}
            autoComplete="off"
            aria-invalid={isInvalid || undefined}
          />
        </>
      );
    else
      return (
        <Sel
          id={key}
          label={label}
          value={value_str}
          onChange={(v) => onChange(v)}
          options={select_values.map((row) => ({
            value: row.value.toString(),
            label: row.name,
          }))}
          className={isInvalid ? SEL_INVALID : undefined}
        />
      );
  }
  if (cellType === "text")
    return (
      <Textarea
        id={key}
        value={(value ?? "") as string}
        key={key}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        autoComplete="off"
        aria-invalid={isInvalid || undefined}
        className={TEXTAREA_CLASS}
      ></Textarea>
    );
  if (cellType === "group_id_name") {
    const select_group_id_name = columns["group_id"].select;
    if (!select_group_id_name || !select_group_id_name.length)
      return (
        <h3 className="font-heading text-xl font-semibold text-err">
          No groups found!
        </h3>
      );
    return (
      <Sel
        id={key}
        label={label}
        value={value_str}
        onChange={(v) => onChange(Number(v))}
        options={select_group_id_name.map((gin) => ({
          value: gin.value.toString(),
          label: gin.name,
        }))}
        className={isInvalid ? SEL_INVALID : undefined}
      />
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
        <Input
          id={key}
          type="password"
          value={(value === null || value === undefined ? "" : value) as string}
          key={key}
          onChange={(e) => onChange(e.target.value)}
          autoComplete="off"
          aria-invalid={isInvalid || undefined}
        />
      </>
    );
  }
  if (cellType === "gvdbs_retr_params") {
    return (
      <div className="rounded-[18px] border border-hair bg-(--box) p-4">
        <EditCellGVDBDefRetrParams
          valueStr={value_str}
          onChange={(newValueStr) => onChange(newValueStr)}
        />
      </div>
    );
  }
  if (cellType === "gvdbs_retr_filters")
    return (
      <Textarea
        id={key}
        value={(value ?? "") as string}
        key={key}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        autoComplete="off"
        aria-invalid={isInvalid || undefined}
        className={TEXTAREA_CLASS}
      ></Textarea>
    );
  return value?.toString();
}
