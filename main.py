import json
from openai import OpenAI
from models import TripItinerary
from config import OPENAI_API_KEY


SYSTEM_PROMPT = """
You are a travel planning agent.

You MUST output ONLY valid JSON.
You MUST follow this schema EXACTLY.
DO NOT invent new fields.
DO NOT rename fields.

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
- Split activities into morning / afternoon / evening
- Max 3 activities per slot
- No extra keys
- Output ONLY the JSON object
"""


def generate_itinerary(message_history: list) -> TripItinerary:
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=message_history,
        response_format={"type": "json_object"}
    )

    raw_output = response.choices[0].message.content
    print("\nRAW OUTPUT:\n", raw_output)

    # save assistant output to memory
    message_history.append({"role": "assistant", "content": raw_output})

    data = json.loads(raw_output)
    return TripItinerary.model_validate(data)


def main():
    print("✈️ Travel Itinerary Agent (type 'exit' to quit)\n")

    # Conversation memory (context)
    message_history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        user_input = input("👉 ")

        if user_input.lower() in ("exit", "quit"):
            print("👋 Bye")
            break

        # store user message
        message_history.append({"role": "user", "content": user_input})

        try:
            itinerary = generate_itinerary(message_history)
        except Exception as e:
            print("❌ Error:", e)
            continue

        print("\n📍 Destination:", itinerary.destination)
        print("🗓️ Days:", itinerary.total_days)
        print("💰 Budget:", itinerary.budget_level)
        print("🎯 Interests:", ", ".join(itinerary.interests))
        print("\n---------------- DAY-WISE PLAN ----------------\n")

        for day in itinerary.days:
            print(f"Day {day.day} – {day.city}")
            print("  Morning:", ", ".join(day.morning))
            print("  Afternoon:", ", ".join(day.afternoon))
            print("  Evening:", ", ".join(day.evening))
            print("  Stay:", day.stay)
            print("  Notes:", day.notes)
            print()


if __name__ == "__main__":
    main()
