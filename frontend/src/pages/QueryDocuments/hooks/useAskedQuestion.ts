import { create } from "zustand";
import { useDocTasksCurrentStore } from "../stores/useDocTasksCurrent";

// View level only (v1.1.0): the asked question is repeated as a heading above
// the answer and must keep showing what was actually asked even if the Query
// box is edited afterwards. A task stores one query text, which a follow-up
// replaces, so the first question of a task is known only to the session that
// asked it. This module remembers, per task and answer number, the text that
// was submitted. Nothing in the behaviour stores reads it back.
type AskedMap = Record<number, { 1?: string; 2?: string }>;

interface AskedState {
  byId: AskedMap;
  // submitted, task id not known yet (the POST has not returned)
  pending: string | null;
  setPending: (text: string | null) => void;
  record: (doc_task_id: number, slot: 1 | 2, text: string) => void;
}

export const useAsked = create<AskedState>((set) => ({
  byId: {},
  pending: null,
  setPending: (pending) => set({ pending }),
  record: (doc_task_id, slot, text) =>
    set((s) => ({
      pending: null,
      byId: {
        ...s.byId,
        [doc_task_id]: { ...(s.byId[doc_task_id] || {}), [slot]: text },
      },
    })),
}));

/**
 * The question to show above the answer, or null when nothing has been asked.
 * `shownAnswer` is the answer on show (1 or 2) for a task with a follow-up.
 */
export function useAskedQuestion(shownAnswer: 1 | 2): string | null {
  const asked = useAsked();
  const doc_task_id = useDocTasksCurrentStore((s) => s.doc_task_id);
  const question_number = useDocTasksCurrentStore((s) => s.question_number);
  const previousQuery = useDocTasksCurrentStore((s) => s.previousQuery);
  if (doc_task_id === null) return asked.pending;
  const known = asked.byId[doc_task_id];
  const n = question_number >= 2 ? shownAnswer : 1;
  // previousQuery holds the last submitted query, or the stored one of a task
  // loaded from the history; it does not follow edits in the Query box
  return known?.[n] ?? previousQuery?.input_text ?? null;
}
