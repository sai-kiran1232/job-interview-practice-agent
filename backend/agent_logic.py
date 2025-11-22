# backend/agent_logic.py

from typing import Tuple, List, Dict

# Predefined questions for each role (as required by assignment)
ROLE_QUESTIONS: Dict[str, List[str]] = {
    "software_engineer": [
        "Tell me about a challenging technical problem you solved recently.",
        "Which programming languages and technologies are you most comfortable with?",
        "Describe a time you worked in a team to deliver a project.",
        "How do you keep yourself updated with new technologies?"
    ],
    "sales_associate": [
        "Tell me about a time you successfully closed a difficult sale.",
        "How do you handle customer objections during a pitch?",
        "Describe a situation where you turned an unhappy customer into a satisfied one.",
        "How do you build long-term relationships with clients?"
    ],
    "retail_associate": [
        "Tell me about a time you handled a difficult customer in a store.",
        "How do you prioritize tasks when the store is busy?",
        "What does good customer service mean to you?",
        "How do you handle mistakes at the cash register or in billing?"
    ],
}

DEFAULT_ROLE = "software_engineer"


def normalize_role(role: str) -> str:
    """Convert user input into one of our known role keys."""
    if not role:
        return DEFAULT_ROLE
    r = role.strip().lower()
    if "engineer" in r or "developer" in r:
        return "software_engineer"
    if "sale" in r:
        return "sales_associate"
    if "retail" in r or "store" in r:
        return "retail_associate"
    return DEFAULT_ROLE


def get_next_question(role: str, q_index: int) -> Tuple[str, bool]:
    """
    Given a role and question index, return:
    - next question
    - is_last_question: bool
    """
    norm_role = normalize_role(role)
    questions = ROLE_QUESTIONS.get(norm_role, ROLE_QUESTIONS[DEFAULT_ROLE])

    if q_index < 0:
        q_index = 0

    if q_index >= len(questions):
        # No more questions
        return ("We have completed the mock interview questions for this role.", True)

    is_last = (q_index == len(questions) - 1)
    return questions[q_index], is_last


def generate_follow_up(answer: str) -> str:
    """
    Very simple follow-up generator based on length of answer.
    This makes the agent feel more like a real interviewer.
    """
    if not answer or len(answer.split()) < 5:
        return "Could you please elaborate a bit more and give a specific example?"
    if len(answer.split()) < 20:
        return "That sounds interesting. Can you walk me through the situation step by step?"
    else:
        return "Thanks for the detailed answer. What would you do differently if you faced this situation again?"

def generate_feedback(role: str, all_answers: List[str]) -> Dict[str, str]:
    """
    Generate simple rule-based feedback on:
    - communication
    - technical knowledge (or role-specific knowledge)
    - overall summary
    """
    full_text = " ".join(all_answers).strip()
    total_words = len(full_text.split()) if full_text else 0

    # Communication feedback
    if total_words == 0:
        communication = (
            "You did not provide any answers, so I cannot judge your communication. "
            "Try to speak out your thoughts clearly and give complete answers."
        )
    elif total_words < 60:
        communication = (
            "Your answers were quite short. Try to give more detailed responses using a clear structure: "
            "Situation, Task, Action, Result."
        )
    else:
        communication = (
            "Your communication was reasonably clear and detailed. You can improve further by making your "
            "answers more structured and highlighting the key result at the end."
        )

    # Role-specific / technical feedback
    r = role.lower()
    text_lower = full_text.lower()

    if "engineer" in r or "developer" in r:
        # Check for some common technical words
        tech_keywords = ["python", "java", "api", "database", "system", "algorithm", "performance"]
        mentioned = [k for k in tech_keywords if k in text_lower]
        if not mentioned:
            technical = (
                "You talked about your work, but did not mention many specific technologies or technical details. "
                "Mention programming languages, tools, system design aspects, or performance metrics."
            )
        else:
            technical = (
                "You showed some technical knowledge by mentioning items like "
                + ", ".join(mentioned)
                + ". You can improve by explaining why you chose those technologies and what trade-offs you considered."
            )
    elif "sale" in r:
        sales_words = ["customer", "client", "target", "revenue", "deal", "pitch", "objection"]
        mentioned = [k for k in sales_words if k in text_lower]
        if not mentioned:
            technical = (
                "For a sales role, try to mention how you handle customers, objections, targets, and how you closed deals. "
                "Use numbers if possible, like percentage growth or target achievement."
            )
        else:
            technical = (
                "You showed understanding of sales by mentioning items like "
                + ", ".join(mentioned)
                + ". You can improve by adding concrete numbers, such as conversion rates or target achievements."
            )
    elif "retail" in r or "store" in r:
        retail_words = ["customer", "store", "inventory", "cash", "billing", "queue", "floor"]
        mentioned = [k for k in retail_words if k in text_lower]
        if not mentioned:
            technical = (
                "For a retail role, try to mention dealing with customers in the store, handling billing or cash, "
                "and keeping the store organized during busy times."
            )
        else:
            technical = (
                "You showed some understanding of retail work by mentioning items like "
                + ", ".join(mentioned)
                + ". You can improve by giving exact situations where you handled rush hours or difficult customers."
            )
    else:
        technical = (
            "You gave some role-related answers. To improve, mention specific tools, processes, or metrics used in that role."
        )

    # Overall summary
    if total_words == 0:
        overall = (
            "Since you did not answer the questions, please try another mock interview and practice speaking out your answers. "
            "Focus on clear structure and giving concrete examples."
        )
    elif total_words < 60:
        overall = (
            "Overall, your interview felt a bit short. With more details and concrete examples, "
            "you can create a stronger impression."
        )
    else:
        overall = (
            "Overall, this was a decent mock interview. With a bit more structure and more concrete metrics or tools, "
            "your answers can become significantly stronger."
        )

    return {
        "communication_feedback": communication,
        "technical_feedback": technical,
        "overall_summary": overall,
    }
