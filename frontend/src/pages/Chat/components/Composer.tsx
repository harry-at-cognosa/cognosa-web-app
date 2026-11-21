import { useEffect, useRef, useState } from "react";
import { Alert, Button, Form } from "react-bootstrap";
import { SendFill, StopFill } from "react-bootstrap-icons";
import { useChatStore } from "../stores/useChatStore";
import styles from "../ChatPage.module.css";

interface Props {
  onCreated: (conv_id: number) => void;
}

export default function Composer({ onCreated }: Props) {
  const store = useChatStore();
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  // grow with the text, up to the CSS max-height
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = el.scrollHeight + 2 + "px";
  }, [text]);

  // ready to type when a conversation is opened or a new chat started
  useEffect(() => {
    inputRef.current?.focus();
  }, [store.conv?.conv_id]);

  const canSend =
    !store.streaming && !store.loadingConv && Boolean(text.trim());

  const handleSend = async () => {
    if (!canSend) return;
    const content = text;
    setText("");
    const accepted = await store.send(content, onCreated);
    // a refused message goes back into the box so it is not lost
    if (!accepted) setText((current) => current || content);
    inputRef.current?.focus();
  };

  return (
    <div className={styles.composer}>
      {store.sendError ? (
        <Alert
          variant="danger"
          dismissible
          className="py-2 mb-2"
          onClose={store.clearSendError}
        >
          {store.sendError}
        </Alert>
      ) : null}
      <div className={styles.composerInner}>
        <Form.Control
          as="textarea"
          ref={inputRef}
          rows={1}
          placeholder="Ask a question...  (Enter to send, Shift+Enter for a new line)"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        {store.streaming ? (
          <Button
            type="button"
            variant="outline-secondary"
            title="Stop the answer"
            onClick={store.stop}
          >
            <StopFill /> Stop
          </Button>
        ) : (
          <Button
            type="button"
            variant="light"
            className="btn-tc-300-400 fw-bold"
            disabled={!canSend}
            onClick={handleSend}
          >
            <SendFill /> Send
          </Button>
        )}
      </div>
    </div>
  );
}
