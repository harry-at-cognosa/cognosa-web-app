import { useEffect } from "react";
import { CircleCheck, LoaderCircle } from "lucide-react";
import { useSuChangeOneselfStore } from "./useSuChangeOneselfStore";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Sel } from "@/components/Sel";

const YES_NO = [
  { value: "1", label: "Yes" },
  { value: "0", label: "No" },
];

/**
 * SuperUser > Change Group: the dialog. The menu item that opens it lives in the
 * shell (components/Shell.tsx), which mounts this component whenever the SuperUser
 * group is shown and controls `show`.
 */
export default function SuChangeOneself({
  show,
  onShowChange,
}: {
  show: boolean;
  onShowChange: (show: boolean) => void;
}) {
  const store = useSuChangeOneselfStore();
  useEffect(() => {
    if (!store.needReload) return;
    async function fetchChangeOneselfData() {
      await store.fetchData();
    }
    fetchChangeOneselfData();
  }, [store.needReload]);
  useEffect(() => store.setNeedReload(true), []);
  // reload each time the dialog is shown
  useEffect(() => {
    if (show) store.setNeedReload(true);
  }, [show]);

  const handleApply = () => {
    store.setNeedReload(true);
    async function setOneself() {
      const result = await store.applyData();
      if (result?.is_success) {
        onShowChange(false);
        location.reload();
      }
    }
    setOneself();
  };
  return (
    <Dialog open={show} onOpenChange={onShowChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Superuser: Group and Options</DialogTitle>
          <DialogDescription className="sr-only">
            Choose the group and the roles to act with
          </DialogDescription>
        </DialogHeader>
        {store.error_msg ? (
          <h3 className="text-lg font-semibold text-err">{store.error_msg}</h3>
        ) : null}
        {store.firstLoad ? (
          <LoaderCircle
            className="size-7 animate-spin text-accent-text"
            role="status"
            aria-label="Loading"
          />
        ) : (
          <div className="grid grid-cols-[auto_1fr] items-center gap-x-3 gap-y-2.5">
            <label htmlFor="su-change-group" className="lbl m-0 text-right">
              Group:
            </label>
            <Sel
              id="su-change-group"
              label="Group"
              value={String(store.group_id)}
              disabled={store.needReload}
              onChange={(v) => store.setGroupId(Number(v))}
              options={store.group_list.map((group) => ({
                value: String(group.group_id),
                label: `${group.group_id}: ${group.group_name}`,
              }))}
            />
            <label htmlFor="su-change-cm" className="lbl m-0 text-right">
              ContentManager:
            </label>
            <Sel
              id="su-change-cm"
              label="ContentManager"
              value={store.is_contentmanager ? "1" : "0"}
              disabled={store.needReload}
              onChange={(v) => store.setIsContentManager(Boolean(Number(v)))}
              options={YES_NO}
            />
            <label htmlFor="su-change-ga" className="lbl m-0 text-right">
              GroupAdmin:
            </label>
            <Sel
              id="su-change-ga"
              label="GroupAdmin"
              value={store.is_groupadmin ? "1" : "0"}
              disabled={store.needReload}
              onChange={(v) => store.setIsGroupAdmin(Boolean(Number(v)))}
              options={YES_NO}
            />
          </div>
        )}
        <DialogFooter className="sm:justify-center">
          <Button onClick={handleApply}>
            <CircleCheck />
            Apply
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
