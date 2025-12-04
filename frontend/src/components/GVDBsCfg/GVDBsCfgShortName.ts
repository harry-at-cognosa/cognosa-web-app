import type { DocTasksGVDBsCfgStore } from "./stores";

interface Props {
  cfgStore: DocTasksGVDBsCfgStore;
}

export default function getGVDBsCfgShortName({ cfgStore }: Props): string {
  let text = "Search Options: ";
  const { k, fetch_k, lambda_mult, score_threshold } = cfgStore.search_kwargs;
  if (cfgStore.search_type === "similarity") {
    text += "SIM: " + k;
  } else if (cfgStore.search_type === "mmr") {
    text += "MMR: " + k + "/" + fetch_k + "/" + lambda_mult;
  } else if (cfgStore.search_type === "similarity_score_threshold") {
    text += "SST: " + k + "/" + score_threshold;
  }
  return text;
}
