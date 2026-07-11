# A factory that returns the model we want, so the rest of the code
# never has to care which backend we are using.
def get_llm(backend: str = "local"):
    if backend == "local":
        from langchain_ollama import ChatOllama
        # temperature=0 keeps classification stable and repeatable
        return ChatOllama(model="llama3", temperature=0)
    elif backend == "api":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    else:
        raise ValueError("backend must be 'local' or 'api'")

# Choose your backend here: "local" or "api"
BACKEND = "local"
llm = get_llm(BACKEND)

import json

def parse_json(text: str) -> dict:
    # Local models sometimes wrap their JSON in extra text,
    # so we grab everything between the first { and the last }.
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])

def classify_ticket(state: dict) -> dict:
    prompt = f"""You are a support triage assistant.
Classify the following support ticket.
Respond with ONLY a JSON object with two keys:
"category": one of ["billing", "technical", "account", "general"]
"priority": one of ["low", "medium", "high"]

Ticket:
{state['ticket']}"""

    response = llm.invoke(prompt)
    result = parse_json(response.content)

    # We return only the keys we want to update in the shared state
    return {"category": result["category"], "priority": result["priority"]}

def draft_reply(state: dict) -> dict:
    prompt = f"""You are a friendly and concise support agent.
Write a short, helpful reply to this {state['category']} ticket.
Do not make promises you cannot keep.

Ticket:
{state['ticket']}"""

    response = llm.invoke(prompt)

    return {"draft_reply": response.content, "status": "auto-drafted"}

def escalate_to_human(state: dict) -> dict:
    # No auto-reply for urgent tickets. We flag them for a person.
    return {
        "draft_reply": "",
        "status": "escalated to human review",
    }

from typing import TypedDict

class TicketState(TypedDict):
    ticket: str        # the original ticket text
    category: str      # filled in by the classifier
    priority: str      # filled in by the classifier
    draft_reply: str   # filled in by the responder (or cleared on escalation)
    status: str        # where the ticket ended up

def route_by_priority(state: TicketState) -> str:
    # Urgent tickets skip the automatic reply and go to a human.
    if state["priority"] == "high":
        return "human_review"
    return "responder"

from langgraph.graph import StateGraph, START, END

# Create the graph and tell it the shape of our state
graph = StateGraph(TicketState)

# Register each agent as a node
graph.add_node("classifier", classify_ticket)
graph.add_node("responder", draft_reply)
graph.add_node("human_review", escalate_to_human)

# Every ticket starts at the classifier
graph.add_edge(START, "classifier")

# After classifying, the router decides where to go next
graph.add_conditional_edges(
    "classifier",
    route_by_priority,
    {
        "responder": "responder",       # normal tickets get an auto-draft
        "human_review": "human_review",  # urgent tickets get escalated
    },
)

# Both paths finish the run
graph.add_edge("responder", END)
graph.add_edge("human_review", END)

# Compile turns our definition into something runnable
app = graph.compile()

# A clearly urgent billing issue
urgent_ticket = (
    "I was charged twice for my subscription this month "
    "and I need a refund today. This is unacceptable."
)

result = app.invoke({"ticket": urgent_ticket})

print("Category:", result["category"])
print("Priority:", result["priority"])
print("Status:  ", result["status"])
print("Reply:   ", result["draft_reply"])

# A routine, low-stakes question
routine_ticket = "How do I change the email address on my account?"

result = app.invoke({"ticket": routine_ticket})

print("Category:", result["category"])
print("Priority:", result["priority"])
print("Status:  ", result["status"])
print("Reply:   ", result["draft_reply"])