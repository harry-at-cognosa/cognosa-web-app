import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Container,
  Card,
  Form,
  InputGroup,
  FloatingLabel,
} from "react-bootstrap";
import { EyeFill, EyeSlashFill } from "react-bootstrap-icons";
import { API_URL } from "../api/apiURL";

export default function Login() {
  const [emailInput, setEmailInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  async function login(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    const body = new URLSearchParams();
    body.set("username", emailInput);
    body.set("password", passwordInput);

    // choose to login by email or username
    const api_login_path = emailInput.includes("@")
      ? "/auth/jwt/login"
      : "/auth/jwt/login_by_username";

    const res = await fetch(`${API_URL}${api_login_path}`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      navigate("/");
    } else {
      setError("Invalid login");
    }
  }

  return (
    <Container className="d-flex justify-content-center align-items-center min-vh-100">
      <Card className="shadow-lg p-4" style={{ maxWidth: 400, width: "100%" }}>
        <h2 className="text-center mb-4">Login</h2>
        <Form onSubmit={login}>
          {/* Email with floating label */}
          <FloatingLabel controlId="floatingEmail" label="Username or Email">
            <Form.Control
              type="text"
              className="mb-3"
              placeholder="name@example.com"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              required
            />
          </FloatingLabel>

          <InputGroup className="mb-3">
            {/* Password with show/hide toggle */}
            <FloatingLabel controlId="floatingPassword" label="Password">
              <Form.Control
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                required
              ></Form.Control>
            </FloatingLabel>
            <Button
              variant="outline-secondary"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeSlashFill size={18} />
              ) : (
                <EyeFill size={18} />
              )}
            </Button>
          </InputGroup>

          {error && <div className="text-danger mb-3">{error}</div>}

          <Button
            type="submit"
            variant="primary"
            className="w-100 py-2 fw-bold"
          >
            LOGIN
          </Button>
        </Form>
      </Card>
    </Container>
  );
}
