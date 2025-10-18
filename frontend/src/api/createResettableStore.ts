import type { StateCreator } from "zustand";
import { create } from "zustand";

const storeResetFns = new Set<() => void>();

export const resetAllStores = () => {
  storeResetFns.forEach((resetFn) => {
    resetFn();
  });
};

export const createResettableStore = (<T extends unknown>(
  f: StateCreator<T> | undefined
) => {
  if (f === undefined) return create;
  const store = create(f);
  const initialState = store.getState();
  storeResetFns.add(() => {
    store.setState(initialState, true);
  });
  return store;
}) as typeof create;
