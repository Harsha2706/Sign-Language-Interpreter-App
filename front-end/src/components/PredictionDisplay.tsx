import { useStore } from "../store/useStore";

const PredictionDisplay = () => {
  const { label, confidence } = useStore();

  return (
    <div>
      <h2>Prediction: {label}</h2>
      <p>Confidence: {confidence?.toFixed(2)}</p>
    </div>
  );
};

export default PredictionDisplay;