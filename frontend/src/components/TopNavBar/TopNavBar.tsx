import { PersonCircle, FileEarmarkText } from "react-bootstrap-icons";
import { Container, Dropdown, Nav, Navbar } from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { useNavbarStore } from "./useTopNavBarStore";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";
import { useWebAppOptionsStore } from "../../stores/useWebAppOptionsStore";

const TopNavBar = () => {
  const user = useLoggedUserStore();
  const title = useNavbarStore((state) => state.title);
  const { color } = useWebAppOptionsStore();

  return (
    <Navbar
      sticky="top"
      expand="lg"
      variant="light"
      className={`justify-content-between p-0`}
      style={{ backgroundColor: color.c300 }}
    >
      <title>{title}</title>
      <style>
        {`
          .nav-hover-glow {
            transition: background-color 0.3s ease;
          }
          .nav-hover-glow:hover {
            background-color: ${color.c400}!important;            
          }
        `}
      </style>
      <Container fluid>
        {/* Left side - App name */}
        <LinkContainer to="/app">
          <Navbar.Brand className="d-flex align-items-center">
            <FileEarmarkText className="me-2"></FileEarmarkText>
            {title}
            &nbsp;&nbsp;&nbsp;{"(" + user.group_name + ")"}
          </Navbar.Brand>
        </LinkContainer>

        {/* Hamburger toggle button (visible on small screens) */}
        <Navbar.Toggle aria-controls="navbar-nav" />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="ms-auto d-flex align-items-center">
            {user.isLogged && (
              <Dropdown className="nav-hover-glow">
                <Dropdown.Toggle variant="" id="nav-dropdown-query_documents">
                  <Navbar.Text className="me-2 fw-bold">
                    Query Documents
                  </Navbar.Text>
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <LinkContainer to="/app/manage_contexts">
                    <Dropdown.Item>Manage Contexts</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/query_documents/queries">
                    <Dropdown.Item>Queries</Dropdown.Item>
                  </LinkContainer>
                </Dropdown.Menu>
              </Dropdown>
            )}
            {user.is_groupadmin && (
              <Dropdown className="nav-hover-glow">
                <Dropdown.Toggle variant="" id="nav-dropdown-groupadmin">
                  <Navbar.Text className="me-2 fw-bold">GroupAdmin</Navbar.Text>
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <LinkContainer to="/app/groupadmin/manage_users">
                    <Dropdown.Item>Users</Dropdown.Item>
                  </LinkContainer>
                </Dropdown.Menu>
              </Dropdown>
            )}
            {user.is_superuser && (
              <Dropdown className="nav-hover-glow">
                <Dropdown.Toggle variant="" id="nav-dropdown-superuser">
                  <Navbar.Text className="me-2 fw-bold">SuperUser</Navbar.Text>
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <LinkContainer to="/app/su/manage_groups">
                    <Dropdown.Item>Groups</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/su/manage_users">
                    <Dropdown.Item>Users</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/su/manage_llms">
                    <Dropdown.Item>LLMs</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/su/manage_vdbs">
                    <Dropdown.Item>VDBs</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/su/manage_doc_tasks">
                    <Dropdown.Item>Doc Tasks</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/su/server_status">
                    <Dropdown.Item>Server Status</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/su/manage_api_settings">
                    <Dropdown.Item>Api Settings</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/su/manage_log_crud">
                    <Dropdown.Item>Log CRUD</Dropdown.Item>
                  </LinkContainer>
                </Dropdown.Menu>
              </Dropdown>
            )}

            {/* Right side - User menu */}
            {user.isLogged && (
              <Dropdown className="nav-hover-glow ms-3">
                <Dropdown.Toggle
                  variant=""
                  id="nav-dropdown-logout"
                  className="d-flex align-items-center py-0"
                >
                  <Navbar.Text className="fw-bold me-2">
                    {user.full_name || user.user_name || user.email}
                  </Navbar.Text>
                  <PersonCircle size={24} />
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <LinkContainer to="/app/change_password">
                    <Dropdown.Item>Change password</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/app/logout">
                    <Dropdown.Item>Logout</Dropdown.Item>
                  </LinkContainer>
                </Dropdown.Menu>
              </Dropdown>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default TopNavBar;
