import requests


def get_weather(city: str) -> str:
    """
    Get simple weather info using wttr.in (free, no API key).
    """
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url, timeout=5)
        return response.text.strip()
    except Exception:
        return "Weather data unavailable"


def search_places(city: str, interest: str) -> list[str]:
    """
    Very simple place lookup using Wikipedia search.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{interest} in {city}",
        "format": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=5).json()
        results = res.get("query", {}).get("search", [])
        return [item["title"] for item in results[:3]]
    except Exception:
        return []


def local_transport(city: str) -> str:
    """
    Static hints (can be improved later).
    """
    return f"In {city}, taxis and local public transport are recommended."


def get_travel_time(place_a: str, place_b: str) -> str:
    """
    Placeholder for now.
    Real APIs come later.
    """
    return f"Approx 30–60 minutes travel from {place_a} to {place_b}"
