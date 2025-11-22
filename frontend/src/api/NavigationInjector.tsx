import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { setOnUnauthenticated } from "../api/axiosClient";

const NavigationInjector = () => {
  const navigate = useNavigate();

  useEffect(() => {
    setOnUnauthenticated(() => {
      // Show toast or alert
      console.log("Session expired. Redirecting to index...");

      // Delay navigation by 1 second
      setTimeout(() => {
        window.location.replace("/");
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
