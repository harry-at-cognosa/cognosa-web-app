import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import App from "./pages/App";
import LoginPage from "./pages/Login/LoginPage";
import LogoutPage from "./pages/Logout/LogoutPage";
import IndexPage from "./pages/Index/IndexPage";
import RAGDocumentsPage from "./pages/RAGDocuments/RAGDocumentsPage";
import ServerStatusPage from "./pages/ServerStatus/ServerStatusPage";
import "./main.css";
import ManageUsersPage from "./pages/ManageUsers/ManageUsersPage";
import ManageContextsPage from "./pages/ManageContexts/ManageContextsPage";
import ChangePasswordPage from "./pages/ChangePassword/ChangePasswordPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <IndexPage />,
      },
      {
        path: "logout",
        element: <LogoutPage />,
      },
      {
        path: "change_password",
        element: <ChangePasswordPage />,
      },
      {
        path: "rag_documents",
        element: <RAGDocumentsPage />,
      },
      {
        path: "manage_contexts",
        element: <ManageContextsPage />,
      },
      {
        path: "server_status",
        element: <ServerStatusPage />,
      },
      {
        path: "manage_users",
        element: <ManageUsersPage />,
      },
    ],
  },
  {
    path: "login",
    element: <LoginPage />,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
