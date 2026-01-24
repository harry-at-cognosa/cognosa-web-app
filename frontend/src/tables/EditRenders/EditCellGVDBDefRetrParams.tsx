import { useEffect, useState } from "react";
import GVDBsRetrParams from "../../components/GVDBsRetrParams/GVDBsRetrParams";
import { useModalGVDBsRetrParamsStore } from "../../components/GVDBsRetrParams/useModalGVDBsRetrParamsStore";

interface Props {
  valueStr: string;
  onChange: (valueStr: string) => void;
}

export default function EditCellGVDBDefRetrParams({
  valueStr,
  onChange,
}: Props) {
  const [loaded, setLoaded] = useState(false);
  const modalStore = useModalGVDBsRetrParamsStore();

  useEffect(() => {
    if (loaded) return;
    modalStore.setData(valueStr);
  }, [loaded]);
  useEffect(() => {
    setLoaded(true);
  }, []);
  if (!loaded) return null;
  return <GVDBsRetrParams onChange={onChange} />;
}
