// Veil over a cell while the table reloads; it also keeps the cell's buttons
// from being clicked until the new rows arrive.
export function BusyCell({ isBusy }: { isBusy: boolean }) {
  if (!isBusy) return null;
  return (
    <div className="absolute inset-0 z-10 bg-(--solid) opacity-50"></div>
  );
}
