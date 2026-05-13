import { create } from "zustand";

type State = {
  label: string;
  confidence: number;
  setPrediction: (label: string, confidence: number) => void;
};

export const useStore = create<State>((set) => ({
  label: "",
  confidence: 0,
  setPrediction: (label, confidence) =>
    set({ label, confidence }),
}));