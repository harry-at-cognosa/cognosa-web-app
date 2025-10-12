import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import ServerStatusAll from "./ServerStatusAll";

function ServerStatusPage() {
  useTopNavBarTitle("Server Status");
  return <ServerStatusAll />;
}

export default ServerStatusPage;
