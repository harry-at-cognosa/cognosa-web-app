import { useEffect, useState } from "react";
import { CircleAlert, LoaderCircle } from "lucide-react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { useTopNavBarTitle } from "../../hooks/useTopNavBarTitle";
import { useLoggedUserStore } from "../../stores/useLoggedUserStore";
import CenteredSpinner from "../../components/CenteredSpinner";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Notice } from "@/components/Notice";
import { PageHead } from "@/components/Shell";
import { SplitLayout } from "@/components/SplitLayout";
import ConversationsBar from "./components/ConversationsBar";
import ChatSettings from "./components/ChatHeader";
import DownloadConversationButton from "./components/DownloadConversationButton";
import MessageThread from "./components/MessageThread";
import Composer from "./components/Composer";
import { useChatStore } from "./stores/useChatStore";

const CHAT_PATH = "/app/chat";

export default function ChatPage() {
  useTopNavBarTitle("Chat");
  const user = useLoggedUserStore();
  const store = useChatStore();
  const navigate = useNavigate();
  const params = useParams();
  // a failed rename or delete (v1.0.1 used alert() for these)
  const [notice, setNotice] = useState<string | null>(null);
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

  const handleNew = () => {
    // v1.0.1 disables New Chat while an answer is being written
    if (useChatStore.getState().streaming) return;
    useChatStore.getState().newChat();
    navigate(CHAT_PATH);
  };

  const ready = !store.optionsError && Boolean(store.options);

  return (
    <SplitLayout
      listLabel="Conversations"
      newLabel="New Chat"
      onNew={handleNew}
      newDisabled={store.streaming}
      list={(afterPick) => (
        <ConversationsBar
          onOpen={(conv_id) => {
            navigate(`${CHAT_PATH}/${conv_id}`);
            afterPick();
          }}
          onNew={handleNew}
          onNotice={setNotice}
        />
      )}
    >
      {(headTools) => (
        <div className="mx-auto flex h-full w-full flex-col px-0 sm:px-1">
          <PageHead className="pb-2">
            {headTools}
            {ready ? <DownloadConversationButton /> : null}
          </PageHead>
          {store.optionsError ? (
            <>
              <Notice text={notice} onDismiss={() => setNotice(null)} />
              <Alert
                role="alert"
                className="mt-2 rounded-2xl border-transparent bg-err-bg px-3.5 py-2.5 text-err"
              >
                <CircleAlert />
                <AlertDescription className="text-sm font-medium text-err">
                  Chat is not available right now: {store.optionsError}
                </AlertDescription>
              </Alert>
            </>
          ) : !store.options ? (
            <div className="flex min-h-0 flex-1 items-center justify-center">
              <LoaderCircle
                className="size-8 animate-spin text-accent-text"
                role="status"
                aria-label="Loading"
              />
            </div>
          ) : (
            <>
              <MessageThread />
              <div className="flex flex-none flex-col gap-2 pt-2">
                <Notice text={notice} onDismiss={() => setNotice(null)} />
                <Notice
                  text={store.sendError || null}
                  onDismiss={store.clearSendError}
                />
                <Composer
                  onCreated={(conv_id) =>
                    navigate(`${CHAT_PATH}/${conv_id}`, { replace: true })
                  }
                >
                  <ChatSettings />
                </Composer>
              </div>
            </>
          )}
        </div>
      )}
    </SplitLayout>
  );
}
