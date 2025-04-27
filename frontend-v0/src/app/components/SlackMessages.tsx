'use client';

import { useState, useEffect } from 'react';
import { fetchSlackEntities } from '../utils/api';

interface SlackMessage {
  id: string;
  slackId: string;
  channelId: string;
  text: string;
  threadTs: string | null;
  createdAt: string;
}

export default function SlackMessages() {
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<SlackMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getMessages = async () => {
      try {
        setLoading(true);
        const response = await fetchSlackEntities();
        if (response.status === 'success' && response.data && response.data.messages) {
          setMessages(response.data.messages);
        } else {
          setError('Invalid response format');
        }
      } catch (err) {
        setError('Failed to fetch messages');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getMessages();
  }, []);

  if (loading) return <div className="text-center p-4">Loading messages...</div>;
  if (error) return <div className="text-red-500 p-4">{error}</div>;
  if (messages.length === 0) return <div className="text-center p-4">No messages found</div>;

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4 text-gray-500">Slack Messages</h2>
      <div className="space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="border-b pb-2 text-gray-500">
            <div className="flex justify-between">
              <span className="font-semibold text-gray-500">{message.slackId}</span>
              <span className="text-sm text-gray-500">
                {new Date(message.createdAt).toLocaleString()}
              </span>
            </div>
            <p className="mt-1">{message.text}</p>
            {message.threadTs && (
              <div className="mt-1 text-sm text-blue-500">
                Thread: {message.threadTs}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
} 