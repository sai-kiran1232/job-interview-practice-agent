# backend/models.py

from pydantic import BaseModel
from typing import List, Optional


class InterviewTurnRequest(BaseModel):
    role: str                   # e.g. "software engineer", "sales", etc.
    question_index: int         # which question number we are on (0,1,2,...)
    answer: str                 # user's answer to the previous question (can be empty for first question)


class InterviewTurnResponse(BaseModel):
    next_question: str          # the next main interview question
    is_last_question: bool      # true if this is the last question
    follow_up_question: str     # follow-up based on the user's answer


class FeedbackRequest(BaseModel):
    role: str
    all_answers: List[str]      # all answers user gave during interview


class FeedbackResponse(BaseModel):
    communication_feedback: str
    technical_feedback: str
    overall_summary: str
