import json
from openai import OpenAI
from pydantic import ValidationError

from models import TripItinerary
from memory import add_memory, search_memory
from config import OPENAI_API_KEY

# ================= CONFIG =================

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4.1"

MAX_RETRIES = 3
MAX_TURNS = 6

# ================= PROMPTS =================

SYSTEM_BASE = """
You are a travel planning agent.

You MUST output ONLY valid JSON.
NO markdown.
NO explanations.
NO extra keys.
"""

SCHEMA_PROMPT = """
Schema:
{
  "destination": string,
  "total_days": number,
  "start_date": string,
  "end_date": string,
  "budget_level": string,
  "interests": [string],
  "days": [
    {
      "day": number,
      "city": string,
      "morning": [string],
      "afternoon": [string],
      "evening": [string],
      "stay": string,
      "notes": string
    }
  ]
}

Rules:
- Max 3 activities per time slot
"""

# ================= PREFERENCE EXTRACTION =================

def extract_preferences(user_input: str) -> list[str]:
    """
    Extract stable, long-term travel preferences from user input.
    """

    prompt = f"""
You are extracting long-term travel preferences.

User input:
\"\"\"{user_input}\"\"\"

Return ONLY valid JSON in this exact format:
{{
  "preferences": [string]
}}

Rules:
- Extract ONLY stable preferences (pace, interests, style).
- Do NOT include destinations, number of days, or itineraries.
- Use short, general statements like:
  "User prefers relaxed trips"
  "User likes beaches and local food"
  "User avoids packed schedules"
- If no preferences are found, return an empty list.
"""

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": prompt}
        ]
    )

    data = json.loads(resp.output_text)
    return data.get("preferences", [])

# ================= ITINERARY GENERATION =================

def generate_itinerary(message_history: list) -> TripItinerary:
    for _ in range(MAX_RETRIES):
        resp = client.responses.create(
            model=MODEL,
            input=message_history
        )
        raw = resp.output_text

        try:
            data = json.loads(raw)
            return TripItinerary.model_validate(data)

        except (json.JSONDecodeError, ValidationError) as e:
            message_history.append({
                "role": "system",
                "content": f"Fix the JSON. Error: {str(e)}"
            })

    raise RuntimeError("Failed to generate valid itinerary")

# ================= MAIN LOOP =================

def main():
    print("✈️ Travel Itinerary Agent (type 'exit' to quit)\n")

    # Initial system context
    message_history = [
        {"role": "system", "content": SYSTEM_BASE + SCHEMA_PROMPT}
    ]

    itinerary: TripItinerary | None = None

    while True:
        user_input = input("👉 ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("👋 Bye")
            break

        # ---- Extract & store long-term preferences ----
        preferences = extract_preferences(user_input)
        for pref in preferences:
            add_memory(pref)

        # ---- Recall memory (soft guidance only) ----
        memories = search_memory(user_input, k=3)
        if memories:
            message_history.append({
                "role": "system",
                "content": "Relevant user preferences:\n" + "\n".join(memories)
            })

        # ---- First input: create itinerary ----
        if itinerary is None:
            message_history.append({
                "role": "user",
                "content": user_input
            })
            itinerary = generate_itinerary(message_history)

        # ---- Subsequent inputs: refine itinerary ----
        else:
            message_history.append({
                "role": "system",
                "content": (
                    f"The destination is fixed as {itinerary.destination}. "
                    f"The trip duration is fixed at {itinerary.total_days} days. "
                    "You may refine activities, pacing, and preferences only."
                )
            })
            message_history.append({
                "role": "user",
                "content": user_input
            })
            itinerary = generate_itinerary(message_history)

        # ---- Keep context small ----
        message_history = (
            message_history[:1] + message_history[-MAX_TURNS:]
        )

        # ---- Output ----
        print("\n📍", itinerary.destination)
        print("🗓️ Days:", itinerary.total_days)
        print("💰 Budget:", itinerary.budget_level)
        print("🎯 Interests:", ", ".join(itinerary.interests))

        for d in itinerary.days:
            print(f"\nDay {d.day} – {d.city}")
            print("  Morning:", d.morning)
            print("  Afternoon:", d.afternoon)
            print("  Evening:", d.evening)
            print("  Stay:", d.stay)
            print("  Notes:", d.notes)

# ================= ENTRY =================

if __name__ == "__main__":
    main()
