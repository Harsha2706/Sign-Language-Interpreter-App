import { useEffect, useRef, useCallback } from "react";
import { useStore } from "../store/useStore";

const WS_URL = "ws://127.0.0.1:8000/ws";
const RECONNECT_DELAY_MS = 2000;
const PREDICTION_HISTORY_SIZE = 5;

export const useWebSocket = () => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);
  const setPrediction = useStore((s) => s.setPrediction);
  const historyRef = useRef<string[]>([]);

  // Simple majority-vote smoother over last N predictions
  const smoothPrediction = (label: string): string => {
    historyRef.current.push(label);
    if (historyRef.current.length > PREDICTION_HISTORY_SIZE) {
      historyRef.current.shift();
    }
    const freq: Record<string, number> = {};
    for (const l of historyRef.current) {
      freq[l] = (freq[l] ?? 0) + 1;
    }
    return Object.keys(freq).reduce((a, b) => (freq[a] > freq[b] ? a : b));
  };

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    console.log(`🔌 Connecting to ${WS_URL}…`);
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("✅ WebSocket connected to backend");
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data as string) as {
          label?: string;
          confidence?: number;
          error?: string;
          uncertain?: boolean;
        };

        if (data.error) {
          console.warn("⚠️ Backend error:", data.error);
          return;
        }

        if (data.label && data.confidence !== undefined) {
          const smoothed = smoothPrediction(data.label);
          setPrediction(smoothed, data.confidence);
        }
      } catch (err) {
        console.error("❌ WebSocket message parse error:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("❌ WebSocket error:", err);
    };

    ws.onclose = () => {
      console.warn("⚠️ WebSocket closed — reconnecting in", RECONNECT_DELAY_MS, "ms");
      wsRef.current = null;
      if (mountedRef.current) {
        reconnectTimerRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
      }
    };
  }, [setPrediction]);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null; // prevent reconnect loop on intentional unmount
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  /**
   * Send a complete sequence to the backend.
   *
   * Payload format — raw JSON array matching backend /ws expectation:
   *   [[f0_0, f0_1, …, f0_257], [f1_0, …], …]   shape: (30, 258)
   *
   * Do NOT wrap in { sequence: … } — the backend parses the raw array directly.
   */
  const send = useCallback((sequence: number[][]): void => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.warn("⚠️ WebSocket not ready — dropping sequence");
      return;
    }
    if (sequence.length === 0) return;

    ws.send(JSON.stringify(sequence));
  }, []);

  return { send };
};