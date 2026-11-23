import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Sel } from "@/components/Sel";
import { cn } from "@/lib/utils";
import type { createTableStore, TableCellValue } from "../TableStoreFactory";
import EditCellGVDBDefRetrParams from "./EditCellGVDBDefRetrParams";
import getColor from "../../api/getColor";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
  col: string;
  onChange: (value: TableCellValue) => void;
}

const SEL_INVALID = "border-destructive ring-3 ring-destructive/20";

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
  const label = data.columns[col]?.display || col;

  if (pk_value_str === "webapp_main_color") {
    const all_values = data.table_options.add_values[
      "webapp_main_color_values"
    ] as string[];
    // each item carries a swatch of its ramp (v1.0.1: the option's background)
    return (
      <Select value={value_str} onValueChange={(v) => onChange(v)}>
        <SelectTrigger
          id={key}
          aria-label={label}
          className={cn("w-full min-w-0", isInvalid && SEL_INVALID)}
        >
          <SelectValue placeholder=" " />
        </SelectTrigger>
        <SelectContent>
          {all_values.map((color) => (
            <SelectItem key={key + "__" + color} value={color}>
              <span
                aria-hidden
                className="size-3.5 flex-none rounded-full"
                style={{ backgroundColor: getColor(color, 300) }}
              />
              {color}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    );
  }
  if (pk_value_str === "suppress_retrieval_parameters") {
    const all_values = (data.table_options.add_values[
      "suppress_retrieval_parameters_values"
    ] as string[]) || ["FALSE", "TRUE"];
    return (
      <Sel
        id={key}
        label={label}
        value={value_str.trim().toUpperCase() === "TRUE" ? "TRUE" : "FALSE"}
        onChange={(v) => onChange(v)}
        options={all_values.map((v) => ({ value: v, label: v }))}
        className={isInvalid ? SEL_INVALID : undefined}
      />
    );
  }
  // Chat: number of earlier turns resent to the LLM (validated on the server)
  if (pk_value_str === "chat_history_turns") {
    return (
      <Input
        id={key}
        type="number"
        min={1}
        step={1}
        value={value_str}
        key={key}
        onChange={(e) => onChange(e.target.value)}
        autoComplete="off"
        aria-invalid={isInvalid || undefined}
        className="tabular-nums"
      />
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
    <Textarea
      id={key}
      value={value_str}
      key={key}
      onChange={(e) => onChange(e.target.value)}
      rows={3}
      autoComplete="off"
      aria-invalid={isInvalid || undefined}
      className="field-sizing-fixed resize-y"
    ></Textarea>
  );
}
