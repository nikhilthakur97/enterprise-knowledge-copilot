import { ChatInput } from './components/ChatInput';
import { ChatWindow } from './components/ChatWindow';
import { useChat } from './hooks/useChat';
import './App.css';

function App() {
  const { turns, loading, error, send } = useChat();

  return (
    <main className="app">
      <header className="app-header">
        <h1>Enterprise Knowledge Copilot</h1>
        <p className="app-subtitle">
          Internal HR knowledge assistant grounded in Lumina policy documents.
        </p>
      </header>
      <ChatWindow turns={turns} loading={loading} error={error} />
      <ChatInput onSend={send} disabled={loading} />
    </main>
  );
}

export default App;
