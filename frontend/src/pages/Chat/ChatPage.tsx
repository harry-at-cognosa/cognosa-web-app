import { useEffect, useRef } from "react";
import { Alert } from "react-bootstrap";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import clsx from "clsx";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";
import CenteredSpinner from "../../components/CenteredSpinner";
import PanelSplitter from "../QueryDocuments/components/PanelSplitter";
import { useLeftPanelPct } from "../QueryDocuments/hooks/useLeftPanelPct";
import ConversationsBar from "./components/ConversationsBar";
import ChatHeader from "./components/ChatHeader";
import MessageThread from "./components/MessageThread";
import Composer from "./components/Composer";
import { useChatStore } from "./stores/useChatStore";
import styles from "./ChatPage.module.css";

const CHAT_PATH = "/app/chat";

export default function ChatPage() {
  useTopNavBarTitle("Chat");
  const user = useLoggedUserStore();
  const store = useChatStore();
  const navigate = useNavigate();
  const params = useParams();
  const splitRef = useRef<HTMLDivElement | null>(null);
  const [leftPct, setLeftPct] = useLeftPanelPct();
  const routeConvId = params.convId ? Number(params.convId) : null;

  useEffect(() => {
    if (!user.isLogged || !user.chat_enabled) return;
    store.loadOptions();
    store.loadConversations();
    // leaving the page closes the stream, which stops an answer in progress
    return () => useChatStore.getState().stop();
  }, [user.isLogged, user.chat_enabled]);

  // The URL names the open conversation, so a reload comes back to it.
  useEffect(() => {
    if (!user.isLogged || !user.chat_enabled) return;
    const state = useChatStore.getState();
    if (routeConvId === null) {
      if (state.conv !== null && !state.streaming) state.newChat();
      return;
    }
    if (state.conv?.conv_id === routeConvId) return;
    state.openConversation(routeConvId).then((found) => {
      if (!found) navigate(CHAT_PATH, { replace: true });
    });
  }, [routeConvId, user.isLogged, user.chat_enabled]);

  if (!user.isLogged) return <CenteredSpinner />;
  // Chat is switched on per group; without it the page does not exist.
  if (!user.chat_enabled) return <Navigate to="/app" replace />;

  return (
    <div className={styles.wrapper}>
      <div
        className={styles.splitContainer}
        ref={splitRef}
        style={{ "--left-pct": `${leftPct}%` } as React.CSSProperties}
      >
        <div className={clsx("ps-2", "pe-2", styles.leftPanel)}>
          <ConversationsBar
            onOpen={(conv_id) => navigate(`${CHAT_PATH}/${conv_id}`)}
            onNew={() => {
              useChatStore.getState().newChat();
              navigate(CHAT_PATH);
            }}
          />
        </div>
        <PanelSplitter containerRef={splitRef} onChange={setLeftPct} />
        <div className={styles.rightPanel}>
          {store.optionsError ? (
            <Alert variant="danger" className="m-3">
              Chat is not available right now: {store.optionsError}
            </Alert>
          ) : !store.options ? (
            <CenteredSpinner />
          ) : (
            <>
              <ChatHeader />
              <MessageThread />
              <Composer
                onCreated={(conv_id) =>
                  navigate(`${CHAT_PATH}/${conv_id}`, { replace: true })
                }
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
