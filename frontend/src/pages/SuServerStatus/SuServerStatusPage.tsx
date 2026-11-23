import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import { PageHead } from "@/components/Shell";
import SuServerStatusAll from "./SuServerStatusAll";

export default function SuServerStatusPage() {
  useTopNavBarTitle("SU Server Status");
  return (
    <div className="px-5">
      <div className="mx-auto flex w-full max-w-[1200px] flex-col gap-5 pt-3 pb-14">
        <PageHead />
        <SuServerStatusAll />
      </div>
    </div>
  );
}
