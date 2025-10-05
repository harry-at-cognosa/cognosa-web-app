import { PersonCircle, FileEarmarkText } from "react-bootstrap-icons";
import { Container, Dropdown, Nav, Navbar } from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { useNavbarStore } from "../../stores/useTopNavBarStore";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";

const TopNavBar = () => {
  const user = useLoggedUserStore();
  const title = useNavbarStore((state) => state.title);
  return (
    <Navbar
      sticky="top"
      expand="lg"
      variant="light"
      className="justify-content-between p-0"
      style={{ backgroundColor: "var(--bs-gray-300)" }}
    >
      <title>{title}</title>
      <style>
        {`
          .nav-hover-glow {
            transition: background-color 0.3s ease;
          }
          .nav-hover-glow:hover {
            background-color: var(--bs-gray-400)!important;            
          }
        `}
      </style>
      <Container fluid>
        {/* Left side - App name */}
        <LinkContainer to="/">
          <Navbar.Brand className="d-flex align-items-center">
            <FileEarmarkText className="me-2"></FileEarmarkText>
            {title}
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
                  <LinkContainer to="/manage_contexts">
                    <Dropdown.Item>Manage Contexts</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/rag_documents">
                    <Dropdown.Item>RAG Documents</Dropdown.Item>
                  </LinkContainer>
                </Dropdown.Menu>
              </Dropdown>
            )}
            {user.is_superuser && (
              <LinkContainer to="/server_status">
                <Nav.Link className="fw-bold nav-hover-glow">
                  Server Status
                </Nav.Link>
              </LinkContainer>
            )}
            {/* Right side - User menu */}
            {user.isLogged && (
              <Dropdown className="nav-hover-glow">
                <Dropdown.Toggle variant="" id="nav-dropdown-logout">
                  <Navbar.Text className="me-2 fw-bold">
                    {user.fullName || user.userName || user.email}
                  </Navbar.Text>
                  <PersonCircle size={"28"} />
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <LinkContainer to="/change_password">
                    <Dropdown.Item>Change password</Dropdown.Item>
                  </LinkContainer>
                  <LinkContainer to="/logout">
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
