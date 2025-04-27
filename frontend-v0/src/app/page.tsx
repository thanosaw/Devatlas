import Link from 'next/link';

export default function Home() {
  return (
    <div className="grid min-h-screen p-8 gap-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">DevAtlas Dashboard</h1>
        <p className="text-gray-600">Project management and monitoring tools</p>
      </header>
      
      <main className="flex flex-col gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-600">Available Tools</h2>
          <div className="space-y-4">
            <div className="border-b pb-4">
              <h3 className="font-semibold mb-2 text-gray-600">Slack Monitoring</h3>
              <p className="mb-3 text-gray-600">View and monitor messages from your Slack channels</p>
              <Link 
                href="/slacks" 
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors"
              >
                View Slack Messages
              </Link>
            </div>
          </div>
        </div>
      </main>
      
      <footer className="mt-16 text-center text-gray-500 text-sm">
        <p>DevAtlas © {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}
