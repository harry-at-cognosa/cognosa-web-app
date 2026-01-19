import { Form, InputGroup } from "react-bootstrap";
import type { SearchType } from "./types";
import { useModalGVDBsRetrParamsStore } from "./useModalGVDBsRetrParamsStore";
import clsx from "clsx";

const SearchTypeName = [
  ["similarity", "Similarity"],
  ["mmr", "MMR"],
  ["similarity_score_threshold", "Similarity Score Threshold"],
];

interface Props {
  onChange?: (valueStr: string) => void;
}

export default function GVDBsRetrParams({ onChange }: Props) {
  const modalStore = useModalGVDBsRetrParamsStore();

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

  return (
    <>
      <InputGroup className="mb-2">
        <InputGroup.Text
          className="fw-bold justify-content-end bg-tc-300"
          style={{ width: "16ch" }}
        >
          Search Type:
        </InputGroup.Text>
        <Form.Select
          className="fw-bold"
          value={search_type}
          onChange={(e) => handleSearchTypeChange(e.target.value as SearchType)}
          autoComplete="off"
        >
          {SearchTypeName.map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </Form.Select>
      </InputGroup>
      <hr />
      <InputGroup className="mb-2">
        <InputGroup.Text
          className="fw-bold justify-content-end bg-tc-300"
          style={{ width: "16ch" }}
        >
          k:
        </InputGroup.Text>
        <Form.Control
          type="number"
          className="fw-bold"
          value={isSIM ? sk__sim.k : isMMR ? sk__mmr.k : sk__sst.k}
          onChange={(e) => handleKandFetchKChange("k", e.target.value)}
          min={1}
        />
      </InputGroup>

      <InputGroup className="mb-2">
        <InputGroup.Text
          className={clsx(
            "fw-bold justify-content-end",
            isMMR ? "bg-tc-300" : "bg-tc-100",
          )}
          style={{ width: "16ch" }}
        >
          fetch_k:
        </InputGroup.Text>
        <Form.Control
          type="number"
          className="fw-bold"
          value={isMMR ? sk__mmr.fetch_k : ""}
          disabled={!isMMR}
          onChange={(e) => handleKandFetchKChange("fetch_k", e.target.value)}
          min={1}
        />
      </InputGroup>
      <InputGroup className="mb-2">
        <InputGroup.Text
          className={clsx(
            "fw-bold justify-content-end",
            isMMR ? "bg-tc-300" : "bg-tc-100",
          )}
          style={{ width: "16ch" }}
        >
          lambda_mult:
        </InputGroup.Text>
        <Form.Control
          type="number"
          step="0.01"
          className="fw-bold"
          value={isMMR ? sk__mmr.lambda_mult : ""}
          disabled={!isMMR}
          onChange={(e) => handleLMandSTChange("lambda_mult", e.target.value)}
          min={0}
          max={1}
        />
      </InputGroup>

      <InputGroup className="mb-2">
        <InputGroup.Text
          className={clsx(
            "fw-bold justify-content-end",
            isSST ? "bg-tc-300" : "bg-tc-100",
          )}
          style={{ width: "16ch" }}
        >
          score_threshold:
        </InputGroup.Text>
        <Form.Control
          type="number"
          step="0.01"
          className="fw-bold"
          value={isSST ? sk__sst.score_threshold : ""}
          disabled={!isSST}
          onChange={(e) =>
            handleLMandSTChange("score_threshold", e.target.value)
          }
          min={0}
          max={1}
        />
      </InputGroup>
    </>
  );
}
