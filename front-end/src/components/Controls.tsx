import { useStore } from "../store/useStore";
import { useSpeech } from "../hooks/useSpeech";

const Controls = () => {
  const { label } = useStore();
  const { speak } = useSpeech();

  return (
    <button
      onClick={() => speak(label)}
      style={{ padding: "10px 18px", borderRadius: 10, marginTop: 12, cursor: "pointer" }}
    >
      🔊 Speak
    </button>
  );
};

export default Controls;