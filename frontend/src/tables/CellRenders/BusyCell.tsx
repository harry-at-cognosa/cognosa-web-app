export function BusyCell({ isBusy }: { isBusy: boolean }) {
  if (!isBusy) return null;
  return (
    <div
      className="position-absolute w-100 h-100 top-0 start-0"
      style={{ zIndex: 1050, opacity: 0.5, backgroundColor: "lightgray" }}
    ></div>
  );
}
