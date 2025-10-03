function ChatInput({ newMessage, isLoading, setNewMessage, submitNewMessage }) {
  function handleSubmit(e) {
    e.preventDefault();
    submitNewMessage();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="sticky bottom-0 bg-white py-4 flex gap-2"
    >
      <input
        type="text"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        placeholder="Type your question..."
        disabled={isLoading}
        className="border p-2 rounded-md grow disabled:bg-gray-100"
      />
      <button
        type="submit"
        disabled={isLoading}
        className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:bg-gray-400"
      >
        Send
      </button>
    </form>
  );
}

export default ChatInput;