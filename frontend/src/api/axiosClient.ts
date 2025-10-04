import axios from "axios";
import { API_URL } from "./apiURL";

const axiosClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Define a global callback for unauthenticated access
let onUnauthenticated: (() => void) | null = null;

export const setOnUnauthenticated = (callback: () => void) => {
  onUnauthenticated = callback;
};

// Request Interceptor: Inject token + handle missing token
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (!token) {
      if (onUnauthenticated) {
        onUnauthenticated();
      }
      return Promise.reject(new Error("No token found"));
    }

    // Set Authorization header properly
    config.headers.set("Authorization", `Bearer ${token}`);
    config.headers.set("Content-Type", "application/json");
    config.headers.set("Accept", "application/json");

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Optional: Also handle 401 responses in response interceptor
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (onUnauthenticated) {
        onUnauthenticated();
      }
    }
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default axiosClient;
