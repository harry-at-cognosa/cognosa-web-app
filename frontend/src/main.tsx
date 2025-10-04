import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./pages/App";
import Login from "./pages/Login";
import Logout from "./pages/Logout";
import ChangePassword from "./pages/ChangePassword";
import Index from "./pages/Index";
import RAGDocuments from "./pages/RAGDocuments";
import ManageContexts from "./pages/ManageContexts";
import ServerStatus from "./pages/ServerStatus";
import "./main.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <Index />,
      },
      {
        path: "logout",
        element: <Logout />,
      },
      {
        path: "change_password",
        element: <ChangePassword />,
      },
      {
        path: "rag_documents",
        element: <RAGDocuments />,
      },
      {
        path: "manage_contexts",
        element: <ManageContexts />,
      },
      {
        path: "server_status",
        element: <ServerStatus />,
      },
    ],
  },
  {
    path: "login",
    element: <Login />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
