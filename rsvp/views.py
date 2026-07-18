import difflib
import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .models import Guest, Meal, Party

MAX_RESULTS = 8


def _guest_payload(guest):
    return {
        "id": guest.id,
        "first_name": guest.first_name,
        "last_name": guest.last_name,
        "attendance": guest.attendance,
        "meal_choice": guest.meal_choice.name if guest.meal_choice_id else "",
        "notes": guest.notes,
    }


def _party_payload(party, guests):
    return {
        "party_id": party.id,
        "label": party.label,
        "guests": [_guest_payload(g) for g in guests],
    }


@require_GET
def search_guests(request):
    query = request.GET.get("q", "").strip().lower()
    if len(query) < 2:
        return JsonResponse({"parties": []})

    tokens = query.split()
    guests = list(Guest.objects.select_related("party", "meal_choice").all())

    matches = [g for g in guests if any(t in g.full_name().lower() for t in tokens)]

    if not matches:
        by_name = {g.full_name().lower(): g for g in guests}
        close_names = difflib.get_close_matches(query, by_name.keys(), n=MAX_RESULTS, cutoff=0.6)
        matches = [by_name[name] for name in close_names]

    parties = {}
    for guest in matches:
        parties.setdefault(guest.party_id, {"party": guest.party, "guests": []})
        parties[guest.party_id]["guests"].append(guest)

    payload = [_party_payload(p["party"], p["guests"]) for p in list(parties.values())[:MAX_RESULTS]]
    return JsonResponse({"parties": payload})


@require_GET
def list_meals(request):
    meals = Meal.objects.filter(is_active=True)
    return JsonResponse({"meals": [m.name for m in meals]})


@csrf_exempt
def submit_rsvp(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid JSON"}, status=400)

    party = get_object_or_404(Party, pk=data.get("party_id"))
    guest_updates = {g["id"]: g for g in data.get("guests", []) if "id" in g}

    guests = party.guests.filter(id__in=guest_updates.keys())
    if not guests:
        return JsonResponse({"error": "no matching guests for this party"}, status=400)

    now = timezone.now()
    for guest in guests:
        info = guest_updates[guest.id]
        if info.get("attending"):
            guest.attendance = Guest.Attendance.ATTENDING
            meal_name = str(info.get("meal_choice", "")).strip()
            guest.meal_choice = Meal.objects.filter(name__iexact=meal_name).first() if meal_name else None
        else:
            guest.attendance = Guest.Attendance.DECLINED
            guest.meal_choice = None
        guest.notes = str(info.get("notes", ""))[:500]
        guest.responded_at = now
        guest.save()

    return JsonResponse({"status": "ok"})
