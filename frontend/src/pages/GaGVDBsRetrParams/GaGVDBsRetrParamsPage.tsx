import { useEffect, useState } from "react";
import { Button, Container, Spinner } from "react-bootstrap";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import GVDBsRetrParams from "../../components/GVDBsRetrParams/GVDBsRetrParams";
import { CheckCircleFill } from "react-bootstrap-icons";
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
    <Container style={{ marginTop: "5ch", maxWidth: "100ch" }}>
      <h3
        className="text-center bg-tc-200"
        style={{ padding: "5px", borderRadius: "10px" }}
      >
        Default Retrieval Parameters for group collections:
      </h3>
      <br />
      {isLoaded ? (
        <div>
          <GVDBsRetrParams />
          <br />
          <div className="text-center">
            <Button
              variant="success"
              className="fw-bold btn-tc-300-400"
              onClick={handleApply}
              disabled={isApplying}
              style={{ color: "black" }}
            >
              {isApplying ? (
                <Spinner size="sm" className="me-1"></Spinner>
              ) : (
                <CheckCircleFill
                  className="me-1 my-0"
                  size="20px"
                  style={{ color: "green" }}
                ></CheckCircleFill>
              )}
              Apply
            </Button>
          </div>
        </div>
      ) : (
        <div className="text-center">
          <Spinner></Spinner>
        </div>
      )}
    </Container>
  );
}
