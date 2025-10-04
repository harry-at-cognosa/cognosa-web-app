import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { setOnUnauthenticated } from "../api/axiosClient";

const NavigationInjector = () => {
  const navigate = useNavigate();

  useEffect(() => {
    setOnUnauthenticated(() => {
      // Show toast or alert
      alert("Session expired. Redirecting to logout...");

      // Delay navigation by 1 second
      setTimeout(() => {
        navigate("/logout", { replace: true });
      }, 1000);
    });

    // Optional cleanup
    return () => {
      setOnUnauthenticated(() => {});
    };
  }, [navigate]);

  return null;
};

export default NavigationInjector;
