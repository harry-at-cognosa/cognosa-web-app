import { useTopNavBarTitle } from "../hooks/useTopNavBarTitle";
import ServerStatusAll from "./elements/ServerStatus/ServerStatusAll";

function ServerStatus() {
  useTopNavBarTitle("Server Status");
  return <ServerStatusAll />;
}

export default ServerStatus;
