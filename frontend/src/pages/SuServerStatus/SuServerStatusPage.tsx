import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import SuServerStatusAll from "./SuServerStatusAll";

export default function SuServerStatusPage() {
  useTopNavBarTitle("SU Server Status");
  return <SuServerStatusAll />;
}
