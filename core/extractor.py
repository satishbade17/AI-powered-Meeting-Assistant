# Actionable items, decisions, questions

import os

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
)


# ============================================================
# GROQ LLM
# ============================================================

def get_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set in environment / .env"
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=groq_api_key,
        temperature=0.2,
    )


# ============================================================
# COMMON CHAIN
# ============================================================

def build_chain(system_prompt: str):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}"),
    ])

    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | prompt
        | llm
        | StrOutputParser()
    )


# ============================================================
# ACTION ITEMS
# ============================================================

def extract_action_items(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "
        "Analyze the meeting transcript carefully and extract "
        "all actionable items.\n\n"

        "For each action item provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, otherwise write "
        "'Not specified')\n\n"

        "Format the answer as a numbered list.\n"
        "Do not invent information that is not present "
        "in the transcript.\n\n"

        "If there are no action items, say:\n"
        "'No action items found.'"
    )

    return chain.invoke(transcript)


# ============================================================
# KEY DECISIONS
# ============================================================

def extract_key_decisions(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "
        "Analyze the meeting transcript and extract all "
        "important decisions that were actually made.\n\n"

        "Format the answer as a numbered list.\n"
        "Do not treat suggestions or discussions as final "
        "decisions unless the transcript indicates that "
        "a decision was made.\n"
        "Do not invent information.\n\n"

        "If there are no key decisions, say:\n"
        "'No key decisions found.'"
    )

    return chain.invoke(transcript)


# ============================================================
# OPEN QUESTIONS
# ============================================================

def extract_questions(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. "
        "Analyze the meeting transcript and extract all "
        "unresolved questions, pending issues, or topics "
        "that require follow-up.\n\n"

        "Format the answer as a numbered list.\n"
        "Do not invent questions that are not supported "
        "by the transcript.\n\n"

        "If there are no unresolved questions, say:\n"
        "'No open questions found.'"
    )

    return chain.invoke(transcript)