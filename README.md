# SKYNET AI - Desktop & Web Frontend

A responsive, high-performance desktop and web frontend interface for **SKYNET AI**, featuring kinetic animations, multi-conversation management, interactive skills & plugins discovery marketplace, language localizer, and tier upgrade/checkout workflows.

---

## 🚀 Quick Start for Backend Integration

### 1. Running the Frontend Locally
You can serve this frontend using any static file server or bundler:

```bash
# Python
python -m http.server 8080

# Or Node.js (npx)
npx serve .
```

Open `http://localhost:8080` in your browser.

---

## 🔌 Backend Integration Guide

This frontend is designed for straightforward plug-and-play integration with your backend API services (FastAPI, Express, Django, Flask, Go, etc.).

### 1. Chat & Inference API (`/api/chat`)
* **Client Function:** `handleSend()` in `index.html`
* **Suggested Backend Endpoint:** `POST /api/chat` or `WebSocket /ws/chat`
* **Request Payload Contract:**
  ```json
  {
    "conversation_id": "conv-1731520000000",
    "message": "Hi, how can I help you today?",
    "model": "haiku-5.5",
    "user_email": "user@example.com",
    "stream": true
  }
  ```
* **Streaming Response:** Server-Sent Events (SSE) or WebSocket packets:
  ```json
  {
    "event": "token",
    "text": "Hello! "
  }
  ```

---

### 2. Authentication API (`/api/auth`)
* **Client Functions:** `applyUserCredentials()`, `performGoogleLogin()`, `performEmailLogin()`
* **Supported Methods:**
  - Google OAuth / Gmail SSO: `POST /api/auth/google` (exchanges Google auth token for backend session JWT).
  - Email Magic Link / Host Trial: `POST /api/auth/email`
* **Session Storage:** Persisted locally via `localStorage.getItem('claude_user_session')`.

---

### 3. Subscription & Checkout (`/api/billing`)
* **Client Function:** `executePaymentFlow()`
* **Backend Webhook / Route:** `POST /api/billing/subscribe`
* **Payload:**
  ```json
  {
    "plan": "Pro",
    "currency": "INR",
    "amount": 2399,
    "payment_method": "upi" | "card" | "netbanking"
  }
  ```

---

### 4. Conversation History & Persistence (`/api/conversations`)
* **Client System:** `conversations` array and `activeChatId`
* **Routes to Implement:**
  - `GET /api/conversations`: Returns list of past chats.
  - `POST /api/conversations`: Creates a new session.
  - `GET /api/conversations/:id`: Fetches message thread.
  - `DELETE /api/conversations/:id`: Deletes or archives chat.

---

### 5. Skills & Plugins Marketplace (`/api/plugins`)
* **Client View:** `Categories` grid in Settings -> Customize.
* **Suggested Route:** `GET /api/plugins/categories` and `GET /api/plugins/search?q=...`

---

## 📁 Repository Structure
```
skynet-ui/
├── index.html        # Main standalone single-page application
├── README.md         # Architecture and backend integration guide
└── .gitignore        # Git ignore rules
```
