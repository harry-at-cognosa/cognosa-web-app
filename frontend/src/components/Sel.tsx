import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { Select as SelectPrimitive } from "radix-ui";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";

export interface Opt {
  value: string;
  label: string;
}

// Radix Select refuses an item whose value is "" (it reserves "" for "nothing
// selected, show the placeholder"). "All" and "not set" therefore need a
// sentinel item that is mapped back to "" here. See ISSUES.md.
const NONE = "__none__";

interface SelProps {
  value: string;
  onChange: (value: string) => void;
  options: Opt[];
  /** adds an item that clears the value; its text is also the placeholder */
  emptyLabel?: string;
  /** "field" = form field; "pill" = composer setting pill with its label inside */
  variant?: "field" | "pill";
  label?: string;
  icon?: ReactNode;
  disabled?: boolean;
  id?: string;
  className?: string;
  size?: "sm" | "default";
}

export function Sel({ value, onChange, options, emptyLabel, variant = "field", label, icon, disabled, id, className, size }: SelProps) {
  return (
    <Select value={value} onValueChange={(v) => onChange(v === NONE ? "" : v)} disabled={disabled}>
      {variant === "pill" ? (
        <SelectPrimitive.Trigger id={id} className={cn("pill", className)} aria-label={label}>
          {icon}
          {label && <span className="k">{label}</span>}
          <span className="v">
            <SelectValue placeholder={emptyLabel} />
          </span>
          <SelectPrimitive.Icon asChild>
            <ChevronDown className="size-4" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
      ) : (
        <SelectTrigger id={id} size={size} className={cn("w-full min-w-0", className)} aria-label={label}>
          <SelectValue placeholder={emptyLabel ?? " "} />
        </SelectTrigger>
      )}
      <SelectContent className="max-w-[calc(100vw-24px)]">
        {emptyLabel !== undefined && (
          <SelectItem value={NONE} className="text-muted-foreground">
            {emptyLabel || "—"}
          </SelectItem>
        )}
        {options.map((o) => (
          <SelectItem key={o.value} value={o.value}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
