from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import analyze_tasks, DEFAULT_WEIGHTS
import json

@api_view(["POST"])
def analyze(request):
    data = request.data.get("tasks") or request.data
    if not isinstance(data, list):
        return Response({"error": "Provide tasks as a list."}, status=400)

    strategy = request.data.get("strategy")
    weights = DEFAULT_WEIGHTS.copy()

    if strategy == "fastest_wins":
        weights = {"urgency": 0.2, "importance": 0.2, "effort": 0.5, "dependencies": 0.1}
    elif strategy == "high_impact":
        weights = {"urgency": 0.1, "importance": 0.7, "effort": 0.1, "dependencies": 0.1}
    elif strategy == "deadline_driven":
        weights = {"urgency": 0.7, "importance": 0.2, "effort": 0.05, "dependencies": 0.05}

    result = analyze_tasks(data, weights)
    return Response(result)

@api_view(["GET"])
def suggest(request):
    raw = request.query_params.get("tasks")
    if not raw:
        return Response({"error": "Provide ?tasks=[...] JSON array"}, 400)

    try:
        tasks = json.loads(raw)
    except:
        return Response({"error": "Invalid JSON"}, 400)

    result = analyze_tasks(tasks)
    return Response({
        "suggestions": result["tasks"][:3],
        "cycles": result["cycles"]
    })
