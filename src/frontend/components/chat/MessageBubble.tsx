export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-brand-500 px-4 py-2.5 text-sm text-white">
          <p className="whitespace-pre-wrap">{message.content}</p>
          {message.timestamp && (
            <p className="mt-1 text-right text-xs text-white/70">
              {new Date(message.timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div
        className="max-w-[80%] rounded-2xl rounded-bl-sm bg-gray-100 px-4 py-2.5 text-sm text-gray-900"
        role="status"
        aria-live="polite"
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.timestamp && (
          <p className="mt-1 text-right text-xs text-gray-400">
            {new Date(message.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}
