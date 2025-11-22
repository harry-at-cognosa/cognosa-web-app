import { createBrowserRouter } from "react-router-dom";
import App from "./App";
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
import SuManageApiSettingsPage from "./SuManageApiSettings/SuManageApiSettingsPage";
import GaManageUsersPage from "./GaManageUsers/GaManageUsersPage";
import GroupAdminRoute from "../components/GroupAdminRoute";
import SuManageDocTasksPage from "./SuManageDocTasks/SuManageDocTasksPage";
import SuManageLogCRUDPage from "./SuManageLogCRUD/SuManageLogCRUDPage";
import HomePage from "./HomePage/HomePage";

export const Router = createBrowserRouter([
  {
    path: "app",
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
        path: "groupadmin",
        element: <GroupAdminRoute />,
        children: [
          {
            path: "manage_users",
            element: <GaManageUsersPage />,
          },
        ],
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
          {
            path: "manage_api_settings",
            element: <SuManageApiSettingsPage />,
          },
          {
            path: "manage_doc_tasks",
            element: <SuManageDocTasksPage />,
          },
          {
            path: "manage_log_crud",
            element: <SuManageLogCRUDPage />,
          },
        ],
      },
    ],
  },
  {
    path: "home",
    element: <HomePage />,
  },
]);
