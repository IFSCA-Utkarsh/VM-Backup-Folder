const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getAuthHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function login(id, password) {
  try {
    const res = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: id,
        password: password,
      }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`Login failed: ${res.status} - ${errorText}`);
      throw new Error(errorText || "Invalid credentials");
    }

    const data = await res.json();
    console.log("Login successful, token:", data.access_token);
    return data;
  } catch (err) {
    console.error("Login error:", err);
    throw err;
  }
}

async function sendChatMessage(message) {
  try {
    console.log('Sending chat message:', message);
    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ question: message }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`Chat request failed: ${res.status} - ${errorText}`);
      throw new Error(errorText || "Chat request failed");
    }

    const data = await res.json();
    console.log('Chat response:', data);
    return data; // { question, answer, sources }
  } catch (err) {
    console.error("Chat error:", err);
    throw err;
  }
}

export default { login, sendChatMessage };