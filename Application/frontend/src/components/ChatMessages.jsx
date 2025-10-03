import { useRef, useEffect } from 'react';

function ChatMessages({ messages, isLoading }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col gap-4">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`p-4 rounded-lg ${
            msg.role === 'user'
              ? 'bg-blue-100 ml-10'
              : 'bg-gray-100 mr-10'
          }`}
        >
          <p className="text-sm">{msg.content}</p>
          {msg.sources && msg.sources.length > 0 ? (
            <div className="mt-2">
              <p className="text-xs font-semibold">Sources:</p>
              <ul className="text-xs list-disc pl-4">
                {msg.sources.map((source, i) => (
                  source.source ? (
                    <li key={i}>
                      <a
                        href={source.source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {source.source}
                      </a>
                    </li>
                  ) : (
                    <li key={i}>No source URL available</li>
                  )
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-xs mt-2 text-gray-500">No sources provided</p>
          )}
          {msg.error && <p className="text-red-600 text-xs mt-2">Error: {msg.content}</p>}
        </div>
      ))}
      {isLoading && (
        <div className="p-4 rounded-lg bg-gray-100 mr-10">
          <p className="text-sm">Loading...</p>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatMessages;