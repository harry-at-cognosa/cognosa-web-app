import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import LoginPage from "./Login/LoginPage";
import LogoutPage from "./Logout/LogoutPage";
import IndexPage from "./Index/IndexPage";
import RAGDocumentsPage from "./RAGDocuments/RAGDocumentsPage";
import ServerStatusPage from "./ServerStatus/ServerStatusPage";
import ManageUsersPage from "./ManageUsers/ManageUsersPage";
import ManageContextsPage from "./ManageContexts/ManageContextsPage";
import ChangePasswordPage from "./ChangePassword/ChangePasswordPage";
import ManageGroupsPage from "./ManageGroups/ManageGroupsPage";
import ManageLLMsPage from "./ManageLLMs/ManageLLMsPage";

export const Router = createBrowserRouter([
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
        path: "manage_groups",
        element: <ManageGroupsPage />,
      },
      {
        path: "manage_llms",
        element: <ManageLLMsPage />,
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
