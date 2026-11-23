import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "./main.css";
import "./lib/scheme";
import { RouterProvider } from "react-router-dom";
import { Router } from "./pages/Router";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={Router} />
  </React.StrictMode>
);
