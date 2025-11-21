export default function HomePage() {
  if (import.meta.env.DEV) {
    return (
      <iframe
        src="http://localhost:8000/"
        style={{ width: "100%", height: "100vh", border: "none" }}
      />
    );
  }
  // Production: render actual content or redirect
  return null;
}
