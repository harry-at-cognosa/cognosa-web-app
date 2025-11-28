import { useRef, useState } from "react";
import type { createTableStore } from "../../TableStoreFactory";
import { Dropdown, Form, InputGroup } from "react-bootstrap";

interface Props {
  useStore: ReturnType<typeof createTableStore>;
}

export default function PaginationLimit({ useStore }: Props) {
  const { nextRequest, data, setLimit, setOffset } = useStore();
  const [inputLimit, setInputLimit] = useState(nextRequest.limit); // local input state
  const debounceRef = useRef<number | null>(null);

  if (!data) return null;
  const { total, table_options } = data;
  const { offset } = nextRequest;

  const handleLimitSelectChange = (value: number) => {
    setInputLimit(value);
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    let newLimit = value;
    if (newLimit < 1) newLimit = 1;
    setLimit(newLimit);
    // Adjust offset if needed
    const newMaxOffset = Math.max(0, total - newLimit);
    if (offset > newMaxOffset) {
      setOffset(newMaxOffset);
    }
  };

  // Handle limit change
  const handleLimitInputChange = (value: number) => {
    // Update local input state immediately for UX
    setInputLimit(value);

    // Clear any existing debounce timer
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new debounce timer
    debounceRef.current = setTimeout(() => {
      let newLimit = value;
      if (newLimit < 1) newLimit = 1;

      setLimit(newLimit);

      // Adjust offset if needed
      const newMaxOffset = Math.max(0, total - newLimit);
      if (offset > newMaxOffset) {
        setOffset(newMaxOffset);
      }
    }, 2000); // 2 seconds
  };

  const idLimitInput = "limit_input__" + data.name;

  return (
    <InputGroup size="sm" className="mb-0">
      <InputGroup.Text className="fw-bold bg-tc-300 bc-tc-300">
        Limit:
      </InputGroup.Text>

      <Form.Control
        list={table_options.select_limit.length ? idLimitInput : ""}
        type="number"
        size="sm"
        value={inputLimit}
        className="fw-bold bg-tc-100 bc-tc-300"
        onChange={(e) => {
          const rawValue = e.target.value;
          const value = parseInt(rawValue, 10);
          if (!isNaN(value)) {
            handleLimitInputChange(value);
          }
        }}
        aria-label="Rows per page"
        style={{ width: "8ch" }}
      />
      {table_options.select_limit.length ? (
        <Dropdown>
          <Dropdown.Toggle
            size="sm"
            className="bc-tc-300 bg-tc-300"
            style={{ color: "black" }}
          />
          <Dropdown.Menu
            align={"end"}
            style={{ minWidth: "auto", width: "10ch" }}
          >
            {table_options.select_limit.map((size) => (
              <Dropdown.Item
                key={size}
                onClick={() => handleLimitSelectChange(size)}
              >
                {size}
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
      ) : null}
    </InputGroup>
  );
}
