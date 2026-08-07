import difflib
import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .models import Guest

MAX_RESULTS = 8


def _guest_payload(guest):
    return {
        "id": guest.id,
        "first_name": guest.first_name,
        "last_name": guest.last_name,
        "attendance": guest.attendance,
        "notes": guest.notes,
    }


@require_GET
def search_guests(request):
    query = request.GET.get("q", "").strip().lower()
    if len(query) < 2:
        return JsonResponse({"guests": []})

    tokens = query.split()
    guests = list(Guest.objects.all())

    matches = [g for g in guests if any(t in g.full_name().lower() for t in tokens)]

    if not matches:
        by_name = {}
        for guest in guests:
            by_name.setdefault(guest.full_name().lower(), guest)
        close_names = difflib.get_close_matches(query, by_name.keys(), n=MAX_RESULTS, cutoff=0.6)
        matches = [by_name[name] for name in close_names]

    return JsonResponse({"guests": [_guest_payload(g) for g in matches[:MAX_RESULTS]]})


@csrf_exempt
def submit_rsvp(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid JSON"}, status=400)

    guest = get_object_or_404(Guest, pk=data.get("guest_id"))

    attendance = str(data.get("attendance", "")).strip()
    selectable = {c for c, _ in Guest.Attendance.choices if c != Guest.Attendance.PENDING}
    if attendance not in selectable:
        return JsonResponse({"error": "invalid attendance selection"}, status=400)

    guest.attendance = attendance
    guest.notes = str(data.get("notes", ""))[:500]
    guest.responded_at = timezone.now()
    guest.save()

    return JsonResponse({"status": "ok"})
