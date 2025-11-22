from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import (
    InterviewTurnRequest,
    InterviewTurnResponse,
    FeedbackRequest,
    FeedbackResponse,
)
from agent_logic import get_next_question, generate_follow_up, generate_feedback

app = FastAPI(
    title="Job Interview Agent",
    description="Agent to conduct mock interviews and provide feedback.",
    version="0.1.0",
)

# CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ok for local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Interview Agent Backend is running"}


@app.post("/interview/turn", response_model=InterviewTurnResponse)
def interview_turn(req: InterviewTurnRequest):
    """
    One step of the mock interview:
    - Takes role and question_index
    - Returns next main question
    - Follow-up will be generated via a separate endpoint
    """
    next_q, is_last = get_next_question(req.role, req.question_index)

    return InterviewTurnResponse(
        next_question=next_q,
        is_last_question=is_last,
        follow_up_question=""   # follow-up not returned here now
    )


@app.post("/interview/followup")
def interview_followup(req: InterviewTurnRequest):
    """
    Generate a follow-up question based on:
    - which main question was asked (question_index)
    - the user's answer
    """
    follow = generate_follow_up(req.question_index, req.answer)
    return {"follow_up_question": follow}



@app.post("/interview/feedback", response_model=FeedbackResponse)
def interview_feedback(req: FeedbackRequest):
    """
    Generate post-interview feedback on:
    - communication
    - technical / role-related knowledge
    - overall performance summary
    """
    fb = generate_feedback(req.role, req.all_answers)

    return FeedbackResponse(
        communication_feedback=fb["communication_feedback"],
        technical_feedback=fb["technical_feedback"],
        overall_summary=fb["overall_summary"],
    )
