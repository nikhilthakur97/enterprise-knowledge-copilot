// Scaffolded application shell.
//
// This commit only proves the typed API client can reach the backend.
// The real chat UI lands in the next commit; for now we render the
// app title and a backend health indicator so the dev server boot
// proves end-to-end wiring (frontend -> API client -> FastAPI).

import { useEffect, useState } from 'react';
import { ApiError, getHealth } from './api/client';
import './App.css';

type HealthState =
  | { kind: 'loading' }
  | { kind: 'ok' }
  | { kind: 'error'; message: string };

function App() {
  const [health, setHealth] = useState<HealthState>({ kind: 'loading' });

  useEffect(() => {
    let cancelled = false;
    getHealth()
      .then(() => {
        if (!cancelled) setHealth({ kind: 'ok' });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message =
          err instanceof ApiError
            ? `${err.status === 0 ? 'Network error' : `HTTP ${err.status}`}: ${err.message}`
            : 'Unknown error';
        setHealth({ kind: 'error', message });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="app">
      <header className="app-header">
        <h1>Enterprise Knowledge Copilot</h1>
        <p className="app-subtitle">
          Internal HR knowledge assistant grounded in synthetic policy docs.
        </p>
      </header>
      <section className="app-status" aria-live="polite">
        {health.kind === 'loading' && <p>Checking backend connection…</p>}
        {health.kind === 'ok' && (
          <p className="status-ok">Backend reachable. Chat UI coming next.</p>
        )}
        {health.kind === 'error' && (
          <p className="status-error">
            Backend not reachable: {health.message}. Start it with{' '}
            <code>uvicorn app.main:app --reload</code> in the{' '}
            <code>backend/</code> folder.
          </p>
        )}
      </section>
    </main>
  );
}

export default App;
