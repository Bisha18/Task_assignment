# Smart Task Analyzer

## Setup
1. `pip install -r requirements.txt`
2. `python manage.py migrate`
3. `python manage.py runserver`
4. Open `frontend/index.html` in your browser.

## [cite_start]Algorithm Explanation [cite: 78]
The priority score is calculated using a weighted sum formula:
`Score = (Urgency * 1.5) + (Importance * 1.2) + (DependencyCount * 2.0) - (Effort * 0.5)`

* **Urgency:** Inverse calculation of days remaining. Overdue tasks get a massive boost.
* **Importance:** Direct scaling of the user's 1-10 input.
* **Effort:** Inverted. We penalize high effort to encourage "Quick Wins" (low effort tasks).
* **Dependencies:** We calculate how many tasks rely on the current task (downstream impact).

## [cite_start]Design Decisions [cite: 79]
* **Stateless Analysis:** The `POST /analyze` endpoint is stateless. It accepts a JSON list and returns it sorted. This allows the "Bulk Input" feature to work immediately without database clutter.
* **Circular Dependencies:** The scoring algorithm includes a depth-first check to detect cycles. If a cycle is found, the score is penalized to prevent system crashes.