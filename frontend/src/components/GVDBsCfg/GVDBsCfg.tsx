import { Form, InputGroup } from "react-bootstrap";
import clsx from "clsx";
import { type TempGVDBsCfgStore, type SearchType } from "./stores";

interface Props {
  tempStore: TempGVDBsCfgStore;
}

export default function GVDBsCfg({ tempStore }: Props) {
  const handleKandFetchKChange = (name: "k" | "fetch_k", value: string) => {
    let value_int = parseInt(value, 10);
    if (isNaN(value_int)) return;
    if (value_int <= 0) value_int = 1;
    tempStore.setKwargsField(name, value_int);
  };

  const handleLMandSTChange = (
    name: "lambda_mult" | "score_threshold",
    value: string
  ) => {
    let value_float = Number(value);
    if (isNaN(value_float)) return;
    if (value_float < 0) value_float = 0;
    if (value_float > 1) value_float = 1;
    tempStore.setKwargsField(name, value_float);
  };

  const disabledFetchK = tempStore.search_type !== "mmr";
  const disabledLambdaMult = tempStore.search_type !== "mmr";
  const disabledScoreThreshold =
    tempStore.search_type !== "similarity_score_threshold";

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
          value={tempStore.search_type}
          onChange={(e) =>
            tempStore.setSearchType(e.target.value as SearchType)
          }
          autoComplete="off"
        >
          {tempStore.search_type_name.map(([value, label]) => (
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
          value={tempStore.search_kwargs.k}
          onChange={(e) => handleKandFetchKChange("k", e.target.value)}
          min={1}
        />
      </InputGroup>
      <InputGroup className="mb-2">
        <InputGroup.Text
          className={clsx(
            "fw-bold justify-content-end",
            disabledFetchK ? "bg-tc-100" : "bg-tc-300"
          )}
          style={{ width: "16ch" }}
        >
          fetch_k:
        </InputGroup.Text>
        <Form.Control
          type="number"
          className="fw-bold"
          value={tempStore.search_kwargs.fetch_k}
          disabled={disabledFetchK}
          onChange={(e) => handleKandFetchKChange("fetch_k", e.target.value)}
          min={1}
        />
      </InputGroup>
      <InputGroup className="mb-2">
        <InputGroup.Text
          className={clsx(
            "fw-bold justify-content-end",
            disabledLambdaMult ? "bg-tc-100" : "bg-tc-300"
          )}
          style={{ width: "16ch" }}
        >
          lambda_mult:
        </InputGroup.Text>
        <Form.Control
          type="number"
          step="0.01"
          className="fw-bold"
          disabled={disabledLambdaMult}
          value={tempStore.search_kwargs.lambda_mult}
          onChange={(e) => handleLMandSTChange("lambda_mult", e.target.value)}
          min={0}
          max={1}
        />
      </InputGroup>
      <InputGroup className="mb-2">
        <InputGroup.Text
          className={clsx(
            "fw-bold justify-content-end",
            disabledScoreThreshold ? "bg-tc-100" : "bg-tc-300"
          )}
          style={{ width: "16ch" }}
        >
          score_threshold:
        </InputGroup.Text>
        <Form.Control
          type="number"
          step="0.01"
          className="fw-bold"
          disabled={disabledScoreThreshold}
          value={tempStore.search_kwargs.score_threshold}
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
