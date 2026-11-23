import type { ReactNode } from "react";
import {
  useSuServerStatusStore,
  type SuServerStatusResponse,
} from "./useSuServerStatusStore";
import { useEffect } from "react";
import axiosClient from "../../api/axiosClient";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

async function fetchBackendData() {
  try {
    const { data } = await axiosClient.get<SuServerStatusResponse>(
      "/su/server_status"
    );
    useSuServerStatusStore.getState().setData(data);
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

function State({ status, text }: { status: Status; text: string }) {
  return <span className={`status ${KIND[status] ?? "off"}`}>{text}</span>;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="glass-card overflow-hidden rounded-3xl">
      <h2 className="px-5 pt-4 pb-3 font-mono text-[15px] font-semibold text-ink">
        {title}
      </h2>
      {children}
    </section>
  );
}

const head = "bg-sunk [&_tr]:border-0";
const cell = "py-2 wrap-anywhere";
const num = "py-2 tabular-nums";
const nowrap = "py-2 whitespace-nowrap";

export default function SuServerStatusAll() {
  const { api_settings, run_tasks, group_vdbs_rows, group_llms_rows } =
    useSuServerStatusStore();
  useEffect(() => {
    fetchBackendData();
    const interval = setInterval(() => {
      fetchBackendData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const textAppDBVersions = `APP: ${api_settings.app_version} DB: ${api_settings.db_version}`;

  return (
    <>
      {/* App/DB versions*/}
      <p className="mx-1.5 max-w-[86ch] text-[15px] leading-[1.55] text-ink-2">
        {textAppDBVersions}
      </p>

      {/* Run Tasks Tables */}
      {run_tasks.length > 0 && (
        <div className="grid grid-cols-2 items-start gap-5">
          {run_tasks.map((task) => (
            <Section key={task.name} title={task.name}>
              <Table>
                <TableHeader className={head}>
                  <TableRow>
                    <TableHead className="pl-5">Name</TableHead>
                    <TableHead className="w-56">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {task.subprocesses.map((sp) => (
                    <TableRow key={sp.name}>
                      <TableCell className="py-2 pl-5 font-mono text-[13.5px] wrap-anywhere">
                        {sp.name}
                      </TableCell>
                      <TableCell className="py-2">
                        <State status={sp.is_good} text={sp.status_text} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Section>
          ))}
        </div>
      )}

      {/* GroupVBDs Table */}
      <Section title="GroupVDBs">
        <Table>
          <TableHeader className={head}>
            <TableRow>
              <TableHead className="pl-5">Group ID</TableHead>
              <TableHead>Seqn #</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>URL</TableHead>
              <TableHead>Collection</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {group_vdbs_rows.map((vdb, idx) => (
              <TableRow key={idx}>
                <TableCell className={`${num} pl-5`}>{vdb.group_id}</TableCell>
                <TableCell className={num}>{vdb.gvdbs_seqn}</TableCell>
                <TableCell className={nowrap}>{vdb.gvdbs_type}</TableCell>
                <TableCell className={`${cell} font-semibold`}>
                  {vdb.gvdbs_name}
                </TableCell>
                <TableCell className={cell}>{vdb.gvdbs_url}</TableCell>
                <TableCell className={cell}>{vdb.gvdbs_collection}</TableCell>
                <TableCell className="py-2 pr-5">
                  <State
                    status={vdb.gvdbs_status}
                    text={vdb.gvdbs_status_text}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Section>

      {/* GroupLLMs Table */}
      <Section title="GroupLLMs">
        <Table>
          <TableHeader className={head}>
            <TableRow>
              <TableHead className="pl-5">Group ID</TableHead>
              <TableHead>Seqn #</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>API BASE</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {group_llms_rows.map((llm, idx) => (
              <TableRow key={idx}>
                <TableCell className={`${num} pl-5`}>{llm.group_id}</TableCell>
                <TableCell className={num}>{llm.gllms_seqn}</TableCell>
                <TableCell className={nowrap}>{llm.gllms_type}</TableCell>
                <TableCell className={`${cell} font-semibold`}>
                  {llm.gllms_name}
                </TableCell>
                <TableCell className={cell}>{llm.gllms_api_base}</TableCell>
                <TableCell className={cell}>{llm.gllms_model}</TableCell>
                <TableCell className="py-2 pr-5">
                  <State
                    status={llm.gllms_status}
                    text={llm.gllms_status_text}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Section>
    </>
  );
}
