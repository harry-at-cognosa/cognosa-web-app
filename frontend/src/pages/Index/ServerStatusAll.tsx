import {
  useServerStatusStore,
  type ServerStatusResponse,
} from "./useServerStatusStore";
import { useEffect } from "react";
import axiosClient from "../../api/axiosClient";

async function fetchBackendData() {
  try {
    const { data } = await axiosClient.get<ServerStatusResponse>(
      "/server_status"
    );
    useServerStatusStore.getState().setData(data);
    return data;
  } catch (err) {
    console.error("Failed to fetch backend data:", err);
    throw err;
  }
}

type Status = "success" | "warning" | "danger";

// the server's status (Bootstrap contextual names) as a 9b status pill
const KIND: Record<Status, string> = {
  success: "ok",
  warning: "warn",
  danger: "err",
};

function StatusList({
  title,
  items,
}: {
  title: string;
  items: { name: string; status: Status; text: string }[];
}) {
  return (
    <section className="glass-card rounded-3xl px-5 pt-[18px] pb-2.5">
      <h2 className="mb-2 font-heading text-base font-semibold tracking-[-0.01em]">
        {title}
      </h2>
      <ul>
        {items.map((i, idx) => (
          <li
            key={idx}
            className="flex items-center justify-between gap-3 border-t border-line-soft py-[9px] text-[14.5px]"
          >
            <span className="min-w-0 wrap-anywhere">{i.name}</span>
            <span className={`status ${KIND[i.status] ?? "off"}`}>{i.text}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function ServerStatusAll() {
  const { api_settings, group_vdbs_rows, group_llms_rows } =
    useServerStatusStore();
  useEffect(() => {
    fetchBackendData();
    const interval = setInterval(() => {
      fetchBackendData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const textAppVersion = `App version: ${api_settings.app_version}`;
  const textDBVersion = `Database version: ${api_settings.db_version}`;

  return (
    <>
      {/* App/DB versions*/}
      <p className="mx-1.5 mt-4 mb-[22px] flex flex-wrap gap-x-7 gap-y-1 text-sm text-ink-2 tabular-nums">
        <span>{textAppVersion}</span>
        <span>{textDBVersion}</span>
      </p>
      <div className="grid grid-cols-1 items-start gap-5 md:grid-cols-2">
        <StatusList
          title="Vector Databases and Collections"
          items={group_vdbs_rows.map((vdb) => ({
            name: vdb.gvdbs_name,
            status: vdb.gvdbs_status,
            text: vdb.gvdbs_status_text,
          }))}
        />
        <StatusList
          title="Available LLM"
          items={group_llms_rows.map((llm) => ({
            name: llm.gllms_name,
            status: llm.gllms_status,
            text: llm.gllms_status_text,
          }))}
        />
      </div>
    </>
  );
}
