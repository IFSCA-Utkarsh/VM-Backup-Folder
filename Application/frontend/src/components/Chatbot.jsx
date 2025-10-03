import { useState } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');
  const [error, setError] = useState('');

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) {
      console.log('Submit blocked: Empty message or loading');
      return;
    }

    setMessages(draft => [
      ...draft,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', sources: [], loading: true }
    ]);
    setNewMessage('');
    setError('');

    try {
      console.log('Sending chat request:', trimmedMessage);
      const data = await api.sendChatMessage(trimmedMessage);
      console.log('Chat response:', data);
      setMessages(draft => {
        draft[draft.length - 1].content = data.answer;
        draft[draft.length - 1].sources = data.sources;
        draft[draft.length - 1].loading = false;
      });
    } catch (err) {
      console.error('Chat error:', err);
      setError(`Failed to get response: ${err.message}`);
      setMessages(draft => {
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].error = true;
        draft[draft.length - 1].content = `Error: ${err.message}`;
      });
    }
  }

  return (
    <div className='relative grow flex flex-col gap-6 pt-6'>
      {error && <p className="text-red-600 text-sm text-center">{error}</p>}
      {messages.length === 0 && (
        <div className='mt-3 font-urbanist text-primary-blue text-xl font-light space-y-4 max-w-xl leading-relaxed'>
          <p>
            <strong className='font-semibold text-primary-dark'>
              Hello! I’m <span className='text-primary-blue'>IFSCA IntelliChat</span> 🤖
            </strong>
          </p>
          <p>
            Your dedicated AI assistant, here to provide you with <em>quick access</em> to internal resources, up-to-date regulatory information, and <em>step-by-step guidance</em>. 📚
          </p>
          <p>
            I’m designed to make your work easier by offering <strong>accurate answers</strong> and helping you navigate complex processes <em>smoothly and efficiently</em>. ⚙️
          </p>
          <p>
            Together, we can enhance collaboration and empower you in driving <strong>excellence</strong> across the organization. 🤝🚀
          </p>
          <p className='italic text-primary-dark'>
            I’m here to assist you every step of the way — just ask!
          </p>
        </div>
      )}
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
      />
      <ChatInput
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
      />
    </div>
  );
}

export default Chatbot;