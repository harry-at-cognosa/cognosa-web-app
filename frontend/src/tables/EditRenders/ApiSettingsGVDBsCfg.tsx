import { useEffect, useState } from "react";
import GVDBsCfg from "../../components/GVDBsCfg/GVDBsCfg";
import {
  defaultGVDBsCfgState,
  useDocTasksGVDBsCfgStore,
  useTempGVDBsCfgStore,
  type SearchKwargsType,
} from "../../components/GVDBsCfg/stores";

interface Props {
  valueStr: string;
  onChange: (valueStr: string) => void;
}

export default function ApiSettingsGVDBsCfg({ valueStr, onChange }: Props) {
  const [loaded, setLoaded] = useState(false);
  const tempStore = useTempGVDBsCfgStore();
  const cfgStore = useDocTasksGVDBsCfgStore();
  const valueObj = JSON.parse(valueStr);
  useEffect(() => {
    if (loaded) return;
    tempStore.setSearchType(valueObj.search_type);
    for (const [name, value] of Object.entries(valueObj.search_kwargs)) {
      tempStore.setKwargsField(name as keyof SearchKwargsType, value as number);
    }
  }, [loaded]);
  useEffect(() => {
    setLoaded(true);
  }, []);
  useEffect(() => {
    if (!loaded) return;
    defaultGVDBsCfgState.search_type = valueObj.search_type;
    defaultGVDBsCfgState.search_kwargs = { ...tempStore.search_kwargs };
    const newValueStr = JSON.stringify({
      search_type: tempStore.search_type,
      search_kwargs: tempStore.search_kwargs,
    });
    cfgStore.setDefaultValues();
    onChange(newValueStr);
  }, [loaded, tempStore.search_type, tempStore.search_kwargs]);
  if (!loaded) return null;
  return <GVDBsCfg tempStore={tempStore} />;
}
