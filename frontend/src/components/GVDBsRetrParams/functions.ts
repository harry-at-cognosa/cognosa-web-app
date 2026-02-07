import type { GVDBsDefRetrParams, GVDBsShortRetrParams } from "./types";

export function getRetrParamsShortNameFromFullStr(fullStr: string) {
  const d = JSON.parse(fullStr) as GVDBsDefRetrParams;
  let text = "N/A";
  let search_type = d.search_type;
  let sk_sim = d.search_kwargs__similarity;
  let sk_mmr = d.search_kwargs__mmr;
  let sk_sst = d.search_kwargs__similarity_score_threshold;
  if (!(search_type && sk_sim && sk_mmr && sk_sst)) {
    return text;
  }
  if (search_type === "similarity") {
    text = `SIM: ${sk_sim.k}`;
  } else if (search_type === "mmr") {
    text = `MMR: ${sk_mmr.k}/${sk_mmr.fetch_k}/${sk_mmr.lambda_mult}`;
  } else if (search_type === "similarity_score_threshold") {
    text = `SST: ${sk_sst.k}/${sk_sst.score_threshold}`;
  }
  return text;
}

export function getRetrParamsShortNameFromShortStr(shortStr: string) {
  const d = JSON.parse(shortStr) as GVDBsShortRetrParams;
  let text = "N/A";
  let search_type = d.search_type;
  let sk = d.search_kwargs;
  if (!(search_type && sk)) {
    return text;
  }
  if (search_type === "similarity") {
    text = `SIM: ${sk.k}`;
  } else if (search_type === "mmr") {
    text = `MMR: ${sk.k}/${sk.fetch_k}/${sk.lambda_mult}`;
  } else if (search_type === "similarity_score_threshold") {
    text = `SST: ${sk.k}/${sk.score_threshold}`;
  }
  return text;
}
