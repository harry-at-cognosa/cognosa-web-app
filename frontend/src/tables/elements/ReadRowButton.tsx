import { Button } from "@/components/ui/button";
import type { createTableStore, TableRow } from "../TableStoreFactory";

interface Props {
  row: TableRow;
  useStore: ReturnType<typeof createTableStore>;
}

export default function ReadRowButton({ row, useStore }: Props) {
  const { setReadRow } = useStore();

  return (
    <Button
      type="button"
      variant="secondary"
      size="xs"
      onClick={() => setReadRow({ ...row })}
    >
      View
    </Button>
  );
}
