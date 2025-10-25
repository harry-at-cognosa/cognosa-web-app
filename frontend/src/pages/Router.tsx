import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import LoginPage from "./Login/LoginPage";
import LogoutPage from "./Logout/LogoutPage";
import IndexPage from "./Index/IndexPage";
import QueryDocumentsPage from "./QueryDocuments/QueryDocumentsPage";
import SuServerStatusPage from "./SuServerStatus/SuServerStatusPage";
import SuManageUsersPage from "./SuManageUsers/SuManageUsersPage";
import ManageContextsPage from "./ManageContexts/ManageContextsPage";
import ChangePasswordPage from "./ChangePassword/ChangePasswordPage";
import SuManageGroupsPage from "./SuManageGroups/SuManageGroupsPage";
import SuManageLLMsPage from "./SuManageLLMs/SuManageLLMsPage";
import SuManageVDBsPage from "./SuManageVDBs/SuManageVDBsPage";
import SuperuserRoute from "../components/SuperUserRoute";

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
        path: "query_documents/queries",
        element: <QueryDocumentsPage />,
      },
      {
        path: "manage_contexts",
        element: <ManageContextsPage />,
      },
      {
        path: "su",
        element: <SuperuserRoute />,
        children: [
          {
            path: "manage_groups",
            element: <SuManageGroupsPage />,
          },
          {
            path: "manage_llms",
            element: <SuManageLLMsPage />,
          },
          {
            path: "manage_vdbs",
            element: <SuManageVDBsPage />,
          },
          {
            path: "server_status",
            element: <SuServerStatusPage />,
          },
          {
            path: "manage_users",
            element: <SuManageUsersPage />,
          },
        ],
      },
    ],
  },
  {
    path: "login",
    element: <LoginPage />,
  },
]);
