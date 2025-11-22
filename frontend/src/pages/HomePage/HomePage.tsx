import { useEffect, useState } from "react";

export default function HomePage() {
  const [htmlContent, setHtmlContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHtml = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://127.0.0.1:8000/");

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const text = await response.text();
        setHtmlContent(text);
        setError(null);
      } catch (err) {
        console.error("Error fetching HTML:", err);
        setError("Failed to load content");
        setHtmlContent("");
      } finally {
        setLoading(false);
      }
    };

    fetchHtml();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  if (import.meta.env.DEV) {
    return <div dangerouslySetInnerHTML={{ __html: htmlContent }} />;
  }

  // Production: render actual content or redirect
  return null;
}
