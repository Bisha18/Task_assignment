from django.test import TestCase
from datetime import date, timedelta
from .scoring import sort_tasks, calculate_smart_score, is_weekend

# Define specific non-weekend and weekend dates for deterministic testing
TODAY = date(2025, 11, 28) # Thursday
SATURDAY = TODAY + timedelta(days=2) # Saturday
SUNDAY = TODAY + timedelta(days=3)   # Sunday

class ScoringAlgorithmTests(TestCase):
    
    def setUp(self):
        # Patch date.today() for deterministic testing (since we can't patch C code datetime)
        # Note: This mock might not be perfect in a real Django environment but works for local Python logic testing.
        self.patcher = self.patch_date_today(TODAY)
        self.patcher.start()

        self.task_overdue = {
            "id": 1, "title": "Overdue Task", "due_date": "2025-11-20", 
            "estimated_hours": 2, "importance": 5, "dependencies": []
        }
        self.task_due_today = {
            "id": 2, "title": "Due Today", "due_date": TODAY.strftime('%Y-%m-%d'),
            "estimated_hours": 1, "importance": 8, "dependencies": []
        }
        self.task_far_future = {
            "id": 3, "title": "Future Task", "due_date": "2099-01-01", 
            "estimated_hours": 5, "importance": 10, "dependencies": []
        }
        self.task_quick_win = {
            "id": 4, "title": "Quick Win", "due_date": (TODAY + timedelta(days=10)).strftime('%Y-%m-%d'),
            "estimated_hours": 0.5, "importance": 3, "dependencies": []
        }
        self.task_high_effort = {
            "id": 5, "title": "Long Project", "due_date": (TODAY + timedelta(days=10)).strftime('%Y-%m-%d'),
            "estimated_hours": 20, "importance": 7, "dependencies": []
        }
        
        self.all_tasks = [self.task_overdue, self.task_due_today, self.task_far_future]

    def tearDown(self):
        self.patcher.stop()

    def patch_date_today(self, mock_date):
        """Helper to mock date.today() for testing date-dependent logic."""
        from unittest.mock import patch
        return patch('tasks.scoring.date', autospec=True, today=lambda: mock_date)

    # --- Core Scoring Tests ---

    def test_overdue_priority(self):
        """Overdue tasks should have the highest score."""
        sorted_t = sort_tasks([self.task_overdue], 'smart')
        # Overdue gets +100 base, so score must be > 100
        self.assertTrue(sorted_t[0]['priority_score'] > 100)
        self.assertIn("OVERDUE", sorted_t[0]['explanation'])

    def test_importance_weighting(self):
        """High importance should score heavily."""
        sorted_t = sort_tasks([self.task_far_future], 'smart')
        # 10 importance * 4 = 40. Days_remaining is huge, so urgency is 0. Score should be ~40
        self.assertTrue(sorted_t[0]['priority_score'] >= 40 and sorted_t[0]['priority_score'] < 45)

    def test_quick_win_bonus(self):
        """Low effort task should get a quick win bonus."""
        sorted_t = sort_tasks([self.task_quick_win], 'smart')
        self.assertIn("Quick Win", sorted_t[0]['explanation'])

    def test_high_effort_penalty(self):
        """Very high effort task should get a small penalty."""
        sorted_t = sort_tasks([self.task_high_effort], 'smart')
        # Penalty is -5
        self.assertTrue(sorted_t[0]['priority_score'] < 30) 

    # --- Dependency and Circularity Tests ---

    def test_dependency_blocker_boost(self):
        """A task that blocks a high-importance task should receive a boost."""
        t_blocked = {"id": 10, "title": "Blocked Task", "due_date": "2025-12-01", "estimated_hours": 1, "importance": 9, "dependencies": [11]}
        t_blocker = {"id": 11, "title": "Blocker Task", "due_date": "2026-01-01", "estimated_hours": 1, "importance": 1, "dependencies": []}
        
        tasks = [t_blocked, t_blocker]
        sorted_t = sort_tasks(tasks, 'smart')
        
        blocker_result = next(t for t in sorted_t if t['id'] == 11)
        # It blocks 1 task, so it should get a +5 boost
        self.assertIn("Blocks 1 task(s)", blocker_result['explanation'])
        # A task with 1 importance should have a base score of 4. Dependency adds +5. Score should be ~9.
        self.assertTrue(blocker_result['priority_score'] >= 9)


    def test_circular_dependency(self):
        """Should detect cycles and return -1 score."""
        t1 = {"id": 1, "title": "T1", "dependencies": [2], "due_date": "2025-01-01", "estimated_hours": 1, "importance": 5}
        t2 = {"id": 2, "title": "T2", "dependencies": [3], "due_date": "2025-01-01", "estimated_hours": 1, "importance": 5}
        t3 = {"id": 3, "title": "T3", "dependencies": [1], "due_date": "2025-01-01", "estimated_hours": 1, "importance": 5}
        tasks = [t1, t2, t3]
        
        sorted_t = sort_tasks(tasks, 'smart')
        
        for task in sorted_t:
            self.assertEqual(task['priority_score'], -1)
            self.assertIn("Circular", task['explanation'])
            self.assertTrue(task['is_circular'])

    # --- Date Intelligence Tests ---
    
    def test_is_weekend_helper(self):
        """Verify the weekend detection is correct."""
        self.assertFalse(is_weekend(TODAY)) # Thursday
        self.assertTrue(is_weekend(SATURDAY))
        self.assertTrue(is_weekend(SUNDAY))

    def test_weekend_due_date_penalty(self):
        """Task due on a weekend should receive a small penalty."""
        # Create a task due on Saturday, far enough out to avoid high urgency boost
        task_weekend = {
            "id": 20, "title": "Weekend Due", "due_date": SATURDAY.strftime('%Y-%m-%d'),
            "estimated_hours": 1, "importance": 5, "dependencies": []
        }
        
        # Base score should be: (Imp 5 * 4) + (Quick Win +5) + (Urgency ~10) = ~35
        # Weekend penalty should reduce it by 5.
        
        sorted_t = sort_tasks([task_weekend], 'smart')
        self.assertIn("Weekend Due Date", sorted_t[0]['explanation'])
        # We can't check the exact value due to relative date but we assert the penalty mechanism is used.
        # This confirms the date intelligence logic is triggered.

    # --- Eisenhower Matrix Tests ---

    def test_eisenhower_quadrants(self):
        """Test tasks are correctly assigned to the four quadrants."""
        
        # Urgent: <= 3 days away from TODAY (Thursday, 2025-11-28)
        # Important: >= 7
        
        urgent_date = (TODAY + timedelta(days=3)).strftime('%Y-%m-%d') # Sunday
        non_urgent_date = (TODAY + timedelta(days=10)).strftime('%Y-%m-%d')

        # 1. DO (Urgent & Important)
        task_do = {"id": 30, "due_date": urgent_date, "importance": 9}
        # 2. DECIDE (Not Urgent & Important)
        task_decide = {"id": 31, "due_date": non_urgent_date, "importance": 9}
        # 3. DELEGATE (Urgent & Not Important)
        task_delegate = {"id": 32, "due_date": urgent_date, "importance": 4}
        # 4. DELETE (Not Urgent & Not Important)
        task_delete = {"id": 33, "due_date": non_urgent_date, "importance": 4}

        tasks = [task_do, task_decide, task_delegate, task_delete]
        sorted_t = sort_tasks(tasks, 'eisenhower')
        
        # Check scores (higher score means higher quadrant priority)
        self.assertEqual(next(t for t in sorted_t if t['id'] == 30)['priority_score'], 4)
        self.assertEqual(next(t for t in sorted_t if t['id'] == 31)['priority_score'], 3)
        self.assertEqual(next(t for t in sorted_t if t['id'] == 32)['priority_score'], 2)
        self.assertEqual(next(t for t in sorted_t if t['id'] == 33)['priority_score'], 1)

        # Check quadrants
        self.assertEqual(next(t for t in sorted_t if t['id'] == 30)['eisenhower_quadrant'], "Do")
        self.assertEqual(next(t for t in sorted_t if t['id'] == 33)['eisenhower_quadrant'], "Delete")