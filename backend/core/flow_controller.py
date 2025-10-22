from typing import Dict


def _missing_slots(context: Dict) -> list[str]:
    required = ["intent", "from", "to", "date"]
    return [s for s in required if not context.get(s)]


def decide_next_action(context: Dict) -> str:
    missing = _missing_slots(context)
    
    # If we have intent, from, and to, we can search flights
    # BUT ONLY if we have a specific date - NO DEFAULT DATE FALLBACK
    if context.get("intent") and context.get("from") and context.get("to") and context.get("date"):
        return "search_flights"
    
    # If we're missing critical information, prompt for it
    if missing:
        return "prompt_missing"

    stage = context.get("booking_stage")
    if stage in {"collect_slots", None}:
        return "prompt_missing"
    if stage == "search":
        return "search_flights"
    if stage == "review":
        if context.get("intent") == "confirm":
            return "request_payment"
        return "search_flights"
    if stage == "payment":
        if context.get("payment_confirmed"):
            return "confirm"
        return "request_payment"

    return "prompt_missing"


