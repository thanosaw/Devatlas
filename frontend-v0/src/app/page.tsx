import SlackMessages from './components/SlackMessages';

export default function Home() {
  return (
    <div className="grid min-h-screen p-8 gap-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Slack Monitoring Dashboard</h1>
        <p className="text-gray-600">View and monitor Slack messages from your channels</p>
      </header>
      
      <main>
        <SlackMessages />
      </main>
      
      <footer className="mt-16 text-center text-gray-500 text-sm">
        <p>Slack Monitoring Tool © {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}
