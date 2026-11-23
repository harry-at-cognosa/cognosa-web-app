import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import { PageHead } from "@/components/Shell";
import ServerStatusAll from "./ServerStatusAll";

export default function IndexPage() {
  useTopNavBarTitle("");
  return (
    <div className="px-5">
      <div className="mx-auto w-full max-w-[1040px] pt-3 pb-14">
        <PageHead title="Home" className="mb-5" />
        <Link
          to="query_documents/queries"
          className="glass-card grid grid-cols-[1fr_auto] items-center gap-x-6 rounded-3xl px-7 py-[26px] text-ink no-underline transition-shadow hover:shadow-[0_0_0_1px_var(--tint-edge),0_30px_60px_-30px_var(--glow)] max-md:px-5 max-md:py-5"
        >
          <div>
            <p className="mb-1.5 text-[13px] font-semibold text-accent-text">
              Query Documents / Queries
            </p>
            <h2 className="mb-2 font-heading text-[28px] leading-[1.15] font-semibold tracking-[-0.02em] max-md:text-[22px]">
              Ask questions across your knowledge base
            </h2>
            <p className="max-w-[64ch] text-[15.5px] leading-[1.55] text-ink-2">
              Query any document collection using natural language.
              <br />
              Select document collection, choose an AI model, and refine results
              with custom instructions.
              <br />
              Get precise answers powered by retrieval-augmented generation.
            </p>
          </div>
          <span
            className="primary-fill grid size-[52px] place-items-center rounded-full max-md:size-10"
            aria-hidden
          >
            <ArrowRight className="size-[22px]" />
          </span>
        </Link>
        <ServerStatusAll />
      </div>
    </div>
  );
}
