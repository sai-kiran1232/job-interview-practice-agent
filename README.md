# Job Interview Practice Agent

This project is an AI-powered agent that helps users prepare for job interviews.

It was built as part of the **Agentic AI Internship Program** assignment and is focused on:
- Conducting **mock interviews for specific roles** (software engineer, sales associate, retail associate)
- Asking **follow-up questions** like a real interviewer
- Providing **post-interview feedback** on communication and role-related knowledge
- Supporting **chat-based** interaction, with **voice input and spoken questions** (voice preferred, chat acceptable as per task)

---

## 1. Features

### 1.1 Mock interviews for specific roles
- User selects a role from the UI:
  - Software Engineer
  - Sales Associate
  - Retail Associate
- For each role, the backend has a separate list of interview questions.
- The agent walks through the questions one by one.

### 1.2 Follow-up questions like a real interviewer
- For every main question:
  - The user answers.
  - A **follow-up question** is generated based on the answer (e.g. “Could you elaborate?”, “Walk me through step by step?”).
- This makes the interaction feel more like a real conversation.

### 1.3 Post-interview feedback
- After the mock interview, the user clicks **Get Feedback**.
- The backend analyses all answers and returns:
  - **Communication feedback**  
    (e.g., were answers too short, detailed, structured)
  - **Technical / role-specific feedback**  
    (e.g., did they mention technologies, tools, customer handling, etc.)
  - **Overall summary**
- The feedback is rule-based (no heavy ML), but tailored by role.

### 1.4 Interaction mode: Voice (preferred) + Chat (acceptable)
- **Chat**:
  - User can type answers in the text box and click *Send Answer & Next Question*.
- **Voice**:
  - **Speak Answer** button uses the browser’s Web Speech API to convert speech to text and fill the answer box.
  - The agent uses browser text-to-speech to read out interviewer questions and follow-ups.
- If voice is not supported in the browser, the chat mode still fully works.

---

## 2. Architecture Overview

**Frontend** (in `/frontend`):
- `index.html` — Simple page with:
  - Role dropdown
  - Conversation area
  - Answer input
  - Buttons: Start Interview, Send Answer & Next Question, Get Feedback, Speak Answer
- `script.js` — Handles:
  - Talking to the backend via Fetch API
  - Managing interview flow:
    - Main question → answer → follow-up → answer → next question
  - Collecting all answers for feedback
  - Voice input and text-to-speech
- `style.css` — Basic layout and styling

**Backend** (in `/backend`):
- `main.py`:
  - FastAPI app with endpoints:
    - `POST /interview/turn` — Get the next **main** interview question for a given role and question index.
    - `POST /interview/followup` — Generate a **follow-up question** based on the user’s answer.
    - `POST /interview/feedback` — Generate **post-interview feedback** based on all answers.
    - `GET /` — Health check message.
- `agent_logic.py`:
  - Contains:
    - Role-based question sets
    - Logic to normalize role names
    - Follow-up generation (simple heuristics based on answer length)
    - Feedback generation (communication, technical/role, overall)
- `models.py`:
  - Pydantic models for request and response bodies.

There is no external database; everything is in memory for simplicity, as the assignment focuses on agent behaviour, not persistence.

---

---

## Conversational & Agentic Behaviour

The interview agent is designed to behave like a realistic human interviewer rather than a static chatbot. It adapts its flow based on user responses and maintains control of the interview process.

### Adaptability Scenarios Tested

1. Confused User
   Example: User answers "I don’t know" or "I am not sure"
   Agent behaviour: Provides guiding follow-up questions such as
   "Can you share any situation where you faced difficulty?" or requests clarity rather than breaking the flow.

2. Efficient User
   Example: Gives strong and structured answer immediately
   Agent behaviour: Moves quickly to next meaningful question without unnecessary probing.

3. Chatty / Off-topic User
   Example: Irrelevant answers such as personal stories or jokes
   Agent behaviour: Responds with structured follow-up like
   "Can we focus on the technical part and return to the question?"

4. Edge-Case User
   Example: Provides invalid inputs, profanity, or nonsense text
   Agent behaviour: Redirects politely:
   "I didn’t fully understand that. Could you please rephrase your answer?"

This ensures the agent demonstrates intelligence beyond simple scripted question flow.

## Design Reasoning & Technical Decisions

- The system uses FastAPI to keep the backend lightweight, fast and easy to document for testing.
- Follow-up logic is rule-based instead of ML to maintain transparency and deterministic behaviour required in interview training apps.
- Stateless backend was selected to minimize complexity and avoid unnecessary database overhead for short conversation sessions.
- Web Speech API is used for voice to enable zero-cost real-time voice interaction without needing external speech services.
- Separating endpoints for main questions and follow-ups improves the realism of the interview flow and avoids robotic behavior.

These decisions reflect a balance between simplicity, practicality and agent realism.

---