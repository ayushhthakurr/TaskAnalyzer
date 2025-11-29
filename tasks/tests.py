from django.test import TestCase
from tasks.scoring import analyze_tasks

class ScoringTests(TestCase):
    def test_overdue_higher_than_future(self):
        tasks = [
            {"id": "A", "title": "A", "due_date": "2000-01-01", "estimated_hours": 1, "importance": 5, "dependencies": []},
            {"id": "B", "title": "B", "due_date": "2999-01-01", "estimated_hours": 1, "importance": 5, "dependencies": []}
        ]
        result = analyze_tasks(tasks)["tasks"]
        scores = {t["id"]: t["score"] for t in result}
        self.assertGreater(scores["A"], scores["B"])  # overdue beats future

    def test_quick_higher_than_long(self):
        tasks = [
            {"id": "Q", "title": "Quick", "estimated_hours": 1, "importance": 5, "dependencies": []},
            {"id": "L", "title": "Long", "estimated_hours": 16, "importance": 5, "dependencies": []}
        ]
        result = analyze_tasks(tasks)["tasks"]
        scores = {t["id"]: t["score"] for t in result}
        self.assertGreater(scores["Q"], scores["L"])  # shorter effort preferred

    def test_detects_circular_dependency(self):
        tasks = [
            {"id": "A", "title": "A", "dependencies": ["B"]},
            {"id": "B", "title": "B", "dependencies": ["A"]}
        ]
        res = analyze_tasks(tasks)
        self.assertTrue(len(res["cycles"]) >= 1)
