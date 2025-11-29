from datetime import date
from dateutil import parser
from typing import Dict, Any, List

DEFAULT_WEIGHTS = {
    "urgency": 0.4,
    "importance": 0.35,
    "effort": 0.15,
    "dependencies": 0.1
}

def parse_date_safe(d):
    if not d:
        return None
    try:
        return parser.parse(d).date()
    except:
        return None

def normalize_task(raw):
    task = {}
    task["id"] = str(raw.get("id") or raw.get("title"))
    task["title"] = raw.get("title", "Untitled")
    task["due_date"] = parse_date_safe(raw.get("due_date"))
    task["estimated_hours"] = float(raw.get("estimated_hours", 1))
    task["importance"] = int(raw.get("importance", 5))
    deps = raw.get("dependencies", [])
    task["dependencies"] = [str(x) for x in deps]
    return task

def detect_cycles(tasks):
    visited = set()
    stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        stack.add(node)
        path.append(node)

        for dep in tasks[node]["dependencies"]:
            if dep not in tasks:
                continue
            if dep not in visited:
                dfs(dep, path)
            elif dep in stack:
                idx = path.index(dep)
                cycles.append(path[idx:].copy())

        path.pop()
        stack.remove(node)

    for t in tasks:
        if t not in visited:
            dfs(t, [])

    return cycles

def urgency_score(due):
    if due is None:
        return 0.1

    diff = (due - date.today()).days

    if diff < 0:
        return 1.0
    if diff <= 3:
        return 0.9
    if diff <= 7:
        return 0.7
    if diff <= 30:
        return 0.4
    return 0.1

def effort_score(hours):
    if hours <= 1:
        return 1.0
    return max(0.2, 1 / (hours ** 0.5))

def dependency_score(task_id, tasks):
    count = 0
    for t in tasks.values():
        if task_id in t["dependencies"]:
            count += 1
    return min(1.0, count / 3)

def analyze_tasks(raw_tasks, weights=None):
    if weights is None:
        weights = DEFAULT_WEIGHTS

    tasks = {}
    for raw in raw_tasks:
        t = normalize_task(raw)
        tasks[t["id"]] = t

    cycles = detect_cycles(tasks)

    result = []
    for tid, t in tasks.items():
        u = urgency_score(t["due_date"])
        i = t["importance"] / 10
        e = effort_score(t["estimated_hours"])
        d = dependency_score(tid, tasks)

        score = (
            u * weights["urgency"] +
            i * weights["importance"] +
            e * weights["effort"] +
            d * weights["dependencies"]
        ) * 100

        result.append({
            "id": tid,
            "title": t["title"],
            "due_date": t["due_date"].isoformat() if t["due_date"] else None,
            "estimated_hours": t["estimated_hours"],
            "importance": t["importance"],
            "dependencies": t["dependencies"],
            "score": round(score, 2),
            "explanation": f"Urgency {u}, Importance {i}, Effort {e}, Blocks {d}"
        })

    result.sort(key=lambda x: x["score"], reverse=True)

    return {"tasks": result, "cycles": cycles}
