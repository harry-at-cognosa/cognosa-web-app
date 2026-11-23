import { useId } from "react";
import { Input } from "@/components/ui/input";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";
import type { SearchType } from "./types";
import { useModalGVDBsRetrParamsStore } from "./useModalGVDBsRetrParamsStore";

const SearchTypeName = [
  ["similarity", "Similarity"],
  ["mmr", "MMR"],
  ["similarity_score_threshold", "Similarity Score Threshold"],
];

interface Props {
  onChange?: (valueStr: string) => void;
}

/**
 * The one Retrieval Parameters editor: Search Type and k / fetch_k /
 * lambda_mult / score_threshold, on the modal store. Used in the popover on
 * Queries and in the admin forms.
 */
export default function GVDBsRetrParams({ onChange }: Props) {
  const modalStore = useModalGVDBsRetrParamsStore();
  const idPrefix = useId();

  const search_type = modalStore.search_type;
  const isSIM = search_type === "similarity";
  const isMMR = search_type === "mmr";
  const isSST = search_type === "similarity_score_threshold";
  const sk__sim = modalStore.search_kwargs__similarity;
  const sk__mmr = modalStore.search_kwargs__mmr;
  const sk__sst = modalStore.search_kwargs__similarity_score_threshold;
  if (
    !search_type ||
    sk__sim?.k === undefined ||
    sk__mmr?.k === undefined ||
    sk__mmr?.fetch_k === undefined ||
    sk__mmr?.lambda_mult === undefined ||
    sk__sst?.k === undefined ||
    sk__sst?.score_threshold === undefined
  )
    return null;

  const handleSearchTypeChange = (newSearchType: SearchType) => {
    modalStore.setSearchType(newSearchType);
    if (onChange) onChange(modalStore.getJSON());
  };

  const handleKandFetchKChange = (name: "k" | "fetch_k", value: string) => {
    let value_int = parseInt(value, 10);
    if (isNaN(value_int)) return;
    if (value_int <= 0) value_int = 1;
    if (isSIM && name === "k") modalStore.setKwargsFieldSIM(name, value_int);
    if (isMMR) modalStore.setKwargsFieldMMR(name, value_int);
    if (isSST && name === "k") modalStore.setKwargsFieldSST(name, value_int);
    if (onChange) onChange(modalStore.getJSON());
  };

  const handleLMandSTChange = (
    name: "lambda_mult" | "score_threshold",
    value: string,
  ) => {
    let value_float = Number(value);
    if (isNaN(value_float)) return;
    if (value_float < 0) value_float = 0;
    if (value_float > 1) value_float = 1;
    if (name === "lambda_mult") modalStore.setKwargsFieldMMR(name, value_float);
    else modalStore.setKwargsFieldSST(name, value_float);
    if (onChange) onChange(modalStore.getJSON());
  };

  const lbl = (enabled: boolean) => cn("lbl", !enabled && "opacity-70");

  return (
    <div>
      <span className="lbl" id={`${idPrefix}-st`}>
        Search Type
      </span>
      <ToggleGroup
        type="single"
        aria-labelledby={`${idPrefix}-st`}
        value={search_type}
        // Radix lets the pressed item be un-pressed (value ""); a search type is required
        onValueChange={(v) => v && handleSearchTypeChange(v as SearchType)}
        className="w-full flex-wrap"
      >
        {SearchTypeName.map(([value, label]) => (
          <ToggleGroupItem key={value} value={value} className="grow">
            {label}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
      <div className="mt-3 grid grid-cols-2 gap-x-3 gap-y-2.5">
        <div>
          <label className="lbl" htmlFor={`${idPrefix}-k`}>
            k
          </label>
          <Input
            id={`${idPrefix}-k`}
            type="number"
            className="tabular-nums"
            value={isSIM ? sk__sim.k : isMMR ? sk__mmr.k : sk__sst.k}
            onChange={(e) => handleKandFetchKChange("k", e.target.value)}
            min={1}
          />
        </div>
        <div>
          <label className={lbl(isMMR)} htmlFor={`${idPrefix}-fetch_k`}>
            fetch_k
          </label>
          <Input
            id={`${idPrefix}-fetch_k`}
            type="number"
            className="tabular-nums"
            value={isMMR ? sk__mmr.fetch_k : ""}
            disabled={!isMMR}
            onChange={(e) => handleKandFetchKChange("fetch_k", e.target.value)}
            min={1}
          />
        </div>
        <div>
          <label className={lbl(isMMR)} htmlFor={`${idPrefix}-lambda_mult`}>
            lambda_mult
          </label>
          <Input
            id={`${idPrefix}-lambda_mult`}
            type="number"
            step="0.01"
            className="tabular-nums"
            value={isMMR ? sk__mmr.lambda_mult : ""}
            disabled={!isMMR}
            onChange={(e) => handleLMandSTChange("lambda_mult", e.target.value)}
            min={0}
            max={1}
          />
        </div>
        <div>
          <label className={lbl(isSST)} htmlFor={`${idPrefix}-score_threshold`}>
            score_threshold
          </label>
          <Input
            id={`${idPrefix}-score_threshold`}
            type="number"
            step="0.01"
            className="tabular-nums"
            value={isSST ? sk__sst.score_threshold : ""}
            disabled={!isSST}
            onChange={(e) =>
              handleLMandSTChange("score_threshold", e.target.value)
            }
            min={0}
            max={1}
          />
        </div>
      </div>
    </div>
  );
}
