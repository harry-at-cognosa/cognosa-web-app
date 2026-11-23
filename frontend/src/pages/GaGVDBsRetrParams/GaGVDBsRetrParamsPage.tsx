import { useEffect, useState } from "react";
import { CircleCheck, LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHead } from "@/components/Shell";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import GVDBsRetrParams from "../../components/GVDBsRetrParams/GVDBsRetrParams";
import axiosClient from "../../api/axiosClient";
import { useModalGVDBsRetrParamsStore } from "../../components/GVDBsRetrParams/useModalGVDBsRetrParamsStore";

export default function GaGVDBsRetrParamsPage() {
  const [isLoaded, setLoaded] = useState(false);
  const [isApplying, setApplying] = useState(false);
  const modalStore = useModalGVDBsRetrParamsStore();
  useTopNavBarTitle("Retrieval Parameters");
  // reload current value from backend
  useEffect(() => {
    if (isLoaded) return;
    async function fetchGVDBsRetrParams() {
      try {
        const res = await axiosClient.get<string>(
          "groupadmin/settings/gvdbs_retr_params",
        );
        const data = res.data;
        modalStore.setData(data);
        setLoaded(true);
      } catch (err: any) {
        console.log(err.response?.data?.message || err.message);
      }
    }
    fetchGVDBsRetrParams();
  }, [isLoaded]);

  function handleApply() {
    setApplying(true);
    const value = modalStore.getJSON();
    async function setGVDBsRetrParams() {
      try {
        await axiosClient.put<string>("groupadmin/settings/gvdbs_retr_params", {
          gvdbs_retr_params: value,
        });
        setApplying(false);
      } catch (err: any) {
        console.log(err.response?.data?.message || err.message);
      }
    }
    setGVDBsRetrParams();
  }
  return (
    <div className="px-5 pt-3 pb-12">
      <PageHead className="mb-3" />
      <div className="glass-card mx-auto w-full max-w-[100ch] rounded-3xl p-6">
        <h2 className="mb-5 font-heading text-xl leading-tight font-semibold tracking-[-0.015em] text-ink">
          Default Retrieval Parameters for group collections:
        </h2>
        {isLoaded ? (
          <div>
            <GVDBsRetrParams />
            <div className="mt-5 flex justify-center border-t border-line-soft pt-4">
              <Button size="lg" onClick={handleApply} disabled={isApplying}>
                {isApplying ? (
                  <LoaderCircle className="animate-spin" />
                ) : (
                  <CircleCheck />
                )}
                Apply
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex justify-center py-6">
            <LoaderCircle
              className="size-8 animate-spin text-accent-text"
              role="status"
              aria-label="Loading"
            />
          </div>
        )}
      </div>
    </div>
  );
}
