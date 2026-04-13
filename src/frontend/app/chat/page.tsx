'use client';

import { ChatPanel } from '@/components/chat/ChatPanel';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';

export default function ChatPage() {
  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex flex-1 flex-col overflow-hidden">
          <ChatPanel sessionId={crypto.randomUUID()} />
        </main>
      </div>
    </div>
  );
}
