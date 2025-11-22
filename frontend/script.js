// frontend/script.js

const API_BASE = "http://localhost:8000";

const roleSelect = document.getElementById("roleSelect");
const chatBox = document.getElementById("chatBox");
const feedbackBox = document.getElementById("feedbackBox");
const answerInput = document.getElementById("answerInput");

const startBtn = document.getElementById("startBtn");
const nextBtn = document.getElementById("nextBtn");
const feedbackBtn = document.getElementById("feedbackBtn");

const voiceInputBtn = document.getElementById("voiceInputBtn");
const voiceStatus = document.getElementById("voiceStatus");

let currentQuestionIndex = 0;
let allAnswers = [];
let currentRole = "software engineer";
let waitingForFollowUp = false;      // false = expecting answer to main question
let isLastCurrentQuestion = false;   // is the current main question the last one?

// Utility: add message to chat box
function addMessage(text, type) {
  const div = document.createElement("div");
  div.classList.add("message");
  if (type) {
    div.classList.add(type);
  }
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Speak text using browser text-to-speech
function speakText(text) {
  if (!("speechSynthesis" in window)) {
    return; // not supported
  }
  const utterance = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(utterance);
}

// Start interview: get first main question only
startBtn.addEventListener("click", async () => {
  currentRole = roleSelect.value;
  currentQuestionIndex = 0;
  allAnswers = [];
  waitingForFollowUp = false;
  isLastCurrentQuestion = false;

  chatBox.innerHTML = "";
  feedbackBox.innerHTML = "";
  answerInput.value = "";

  addMessage(`Starting mock interview for role: ${currentRole}`, "system");

  try {
    const body = {
      role: currentRole,
      question_index: currentQuestionIndex,
      answer: ""
    };

    const res = await fetch(`${API_BASE}/interview/turn`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    // Only main question here, no follow-up yet
    addMessage(`Interviewer: ${data.next_question}`, "interviewer");
    speakText(data.next_question);

    isLastCurrentQuestion = data.is_last_question;
    nextBtn.disabled = false;
    feedbackBtn.disabled = true;
  } catch (err) {
    console.error(err);
    addMessage("Error starting interview. Check if backend is running.", "system");
  }
});

// Send answer and either:
// 1) show follow-up for current question, or
// 2) move to next main question
nextBtn.addEventListener("click", async () => {
  const userAnswer = answerInput.value.trim();
  if (!userAnswer) {
    alert("Please type your answer before proceeding.");
    return;
  }

  // Show user answer in chat
  addMessage(`You: ${userAnswer}`, "user");
  answerInput.value = "";

  try {
    if (!waitingForFollowUp) {
      // This is answer to the main question
      allAnswers.push(userAnswer);

      const body = {
        role: currentRole,
        question_index: currentQuestionIndex,
        answer: userAnswer
      };

      const res = await fetch(`${API_BASE}/interview/followup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      });

      const data = await res.json();

      // Now show follow-up question
      addMessage(`Follow-up: ${data.follow_up_question}`, "interviewer");
      speakText(data.follow_up_question);

      // Next click will be answer to follow-up
      waitingForFollowUp = true;
    } else {
      // This is answer to the follow-up question
      // We do not need to store it for scoring, but we accept it.

      waitingForFollowUp = false;

      // If current main question was the last one, end interview here
      if (isLastCurrentQuestion) {
        addMessage("This was the last question for this mock interview.", "system");
        nextBtn.disabled = true;
        feedbackBtn.disabled = false;  // enable feedback
        return;
      }

      // Move to next main question
      currentQuestionIndex += 1;

      const body = {
        role: currentRole,
        question_index: currentQuestionIndex,
        answer: userAnswer
      };

      const res = await fetch(`${API_BASE}/interview/turn`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      });

      const data = await res.json();

      addMessage(`Interviewer: ${data.next_question}`, "interviewer");
      speakText(data.next_question);

      isLastCurrentQuestion = data.is_last_question;
      // waitingForFollowUp is already false, so next click again gives follow-up
    }
  } catch (err) {
    console.error(err);
    addMessage("Error during interview. Check if backend is running.", "system");
  }
});

// Get feedback after interview
feedbackBtn.addEventListener("click", async () => {
  feedbackBox.innerHTML = "";

  addMessage("Generating feedback based on your answers...", "system");

  try {
    const body = {
      role: currentRole,
      all_answers: allAnswers
    };

    const res = await fetch(`${API_BASE}/interview/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    const parts = [
      `Communication Feedback: ${data.communication_feedback}`,
      `Technical Feedback: ${data.technical_feedback}`,
      `Overall Summary: ${data.overall_summary}`
    ];

    parts.forEach((txt) => {
      const div = document.createElement("div");
      div.classList.add("message");
      div.textContent = txt;
      feedbackBox.appendChild(div);
    });

    feedbackBox.scrollTop = feedbackBox.scrollHeight;
  } catch (err) {
    console.error(err);
    const div = document.createElement("div");
    div.classList.add("message");
    div.textContent = "Error generating feedback. Check if backend is running.";
    feedbackBox.appendChild(div);
  }
});

// Voice input using Web Speech API
let recognition = null;
let recognizing = false;

if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = "en-IN"; // English India
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    recognizing = true;
    voiceStatus.textContent = "Listening... please speak.";
  };

  recognition.onend = () => {
    recognizing = false;
    voiceStatus.textContent = "";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    answerInput.value = transcript;
  };

  recognition.onerror = (event) => {
    recognizing = false;
    voiceStatus.textContent = "Error capturing voice. Try again.";
    console.error(event);
  };
} else {
  voiceStatus.textContent = "Voice input not supported in this browser.";
}

// When user clicks Speak Answer
voiceInputBtn.addEventListener("click", () => {
  if (!recognition) {
    alert("Voice input is not supported in this browser.");
    return;
  }
  if (recognizing) {
    recognition.stop();
  } else {
    recognition.start();
  }
});
