import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Container, Form } from "react-bootstrap";
import { API_URL } from "../../api/apiURL";

export default function ChangePasswordPage() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");

    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    const res = await fetch(`${API_URL}/change_password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
    if (res.ok) {
      setMessage("Password changed successfully.");
      navigate("/app");
    } else {
      const err = await res.json().catch(() => ({}));
      setMessage(err?.detail[0]?.msg || "Password change failed.");
    }
  }

  return (
    <Container className="d-flex justify-content-center align-items-center min-vh-100">
      <Card className="shadow-lg p-4" style={{ maxWidth: 400, width: "100%" }}>
        <h2 className="text-center mb-4">Change Password</h2>
        <Form onSubmit={handleSubmit}>
          <Form.Group>
            <Form.Label>Current password</Form.Label>
            <Form.Control
              type="password"
              placeholder=""
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              style={{ width: "100%", padding: "0.5rem" }}
              required
            ></Form.Control>
          </Form.Group>
          <br />
          <Form.Group>
            <Form.Label>New password</Form.Label>
            <Form.Control
              type="password"
              placeholder=""
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              style={{ width: "100%", padding: "0.5rem" }}
              required
            ></Form.Control>
          </Form.Group>
          <br />
          <Button type="submit" variant="primary" className="mt-2 mx-auto">
            Change
          </Button>
          {message && <div>{message}</div>}
        </Form>
      </Card>
    </Container>
  );
}
