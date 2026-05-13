import { useAuthStore } from "./store/useAuthStore";
import LoginPage from "./components/LoginPage";
import Dashboard from "./components/Dashboard";
import "./App.css";

function App() {
  const { isAuthenticated, username, logout } = useAuthStore();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div>
      {/* ── Top Navigation Bar ── */}
      <header className="app-topbar">
        <span className="app-brand">
          <svg
            width="22"
            height="22"
            viewBox="0 0 48 48"
            fill="none"
            style={{ verticalAlign: "middle" }}
          >
            <circle cx="24" cy="24" r="24" fill="url(#tg)" />
            <defs>
              <radialGradient id="tg" cx="30%" cy="30%" r="70%">
                <stop offset="0%" stopColor="#c084fc" />
                <stop offset="100%" stopColor="#7c3aed" />
              </radialGradient>
            </defs>
            <path
              d="M16 30 Q16 22 20 20 L20 15 Q20 13 22 13 Q24 13 24 15 L24 20
                 L24 14 Q24 12 26 12 Q28 12 28 14 L28 20
                 L28 15 Q28 13 30 13 Q32 13 32 15 L32 22
                 Q34 21 34 23 L34 28 Q34 34 28 35 L22 35 Q16 34 16 30Z"
              fill="white"
              fillOpacity="0.92"
            />
          </svg>
          SignLang AI
        </span>
        <div className="app-user">
          <span className="app-username">👤 {username}</span>
          <button id="logout-btn" className="logout-btn" onClick={logout}>
            Sign Out
          </button>
        </div>
      </header>

      {/* ── Dashboard ── */}
      <Dashboard />
    </div>
  );
}

export default App;