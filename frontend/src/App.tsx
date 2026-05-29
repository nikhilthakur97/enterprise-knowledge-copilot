import { ChatInput } from './components/ChatInput';
import { ChatWindow } from './components/ChatWindow';
import { useChat } from './hooks/useChat';
import './App.css';

function App() {
  const { turns, loading, error, send } = useChat();

  return (
    <main className="app">
      <header className="app-header">
        <div className="app-mark" aria-hidden="true">
          EK
        </div>
        <div className="app-titles">
          <h1>Enterprise Knowledge Copilot</h1>
          <p className="app-subtitle">
            Grounded answers from Lumina&apos;s HR knowledge base.
          </p>
        </div>
        <span className="app-tag">
          <span className="app-tag-dot" aria-hidden="true" />
          Lumina HR
        </span>
      </header>
      <ChatWindow
        turns={turns}
        loading={loading}
        error={error}
        onPickExample={send}
      />
      <ChatInput onSend={send} disabled={loading} />
    </main>
  );
}

export default App;
