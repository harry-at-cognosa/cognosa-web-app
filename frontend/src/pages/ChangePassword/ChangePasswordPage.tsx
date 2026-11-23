import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHead } from "@/components/Shell";
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
      navigate("/");
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
    <div className="grid min-h-full grid-rows-[auto_1fr] px-5 pt-3 pb-8">
      <PageHead title="Change Password" />
      <div className="glass-card w-full max-w-[400px] place-self-center rounded-3xl p-6">
        <form onSubmit={handleSubmit} className="grid gap-4">
          <div>
            <label htmlFor="current-password" className="lbl">
              Current password
            </label>
            <Input
              id="current-password"
              type="password"
              placeholder=""
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="new-password" className="lbl">
              New password
            </label>
            <Input
              id="new-password"
              type="password"
              placeholder=""
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>
          <div className="mt-1">
            <Button type="submit">Change</Button>
          </div>
          {message && (
            <div role="status" className="text-sm text-ink-2">
              {message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
