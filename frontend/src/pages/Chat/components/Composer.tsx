import { useEffect, useRef, useState, type ReactNode } from "react";
import { ArrowUp, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useChatStore } from "../stores/useChatStore";

interface Props {
  onCreated: (conv_id: number) => void;
  /** the settings row under the message box */
  children?: ReactNode;
}

export default function Composer({ onCreated, children }: Props) {
  const store = useChatStore();
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  // grow with the text, up to the CSS max-height
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";
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
    <div className="composer rounded-[26px] px-3 pt-3 pb-3 sm:px-4 sm:pt-3.5">
      <div className="flex items-end gap-3">
        <textarea
          ref={inputRef}
          aria-label="Message"
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
          className="scroll-soft block max-h-48 min-h-[44px] w-full min-w-0 flex-1 resize-none bg-transparent px-1 py-2.5 text-base leading-[1.4] text-ink outline-none placeholder:text-muted-foreground"
        />
        {store.streaming ? (
          <Button
            type="button"
            variant="outline"
            size="lg"
            className="flex-none border-tint-edge max-sm:w-[42px] max-sm:px-0"
            title="Stop the answer"
            onClick={store.stop}
          >
            <Square className="size-3.5 fill-current" />
            <span className="max-sm:sr-only">Stop</span>
          </Button>
        ) : (
          <Button
            type="button"
            size="lg"
            className="flex-none max-sm:w-[42px] max-sm:px-0"
            disabled={!canSend}
            onClick={handleSend}
          >
            <ArrowUp />
            <span className="max-sm:sr-only">Send</span>
          </Button>
        )}
      </div>
      {children}
    </div>
  );
}
