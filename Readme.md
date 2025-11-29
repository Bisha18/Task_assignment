# Smart Task Analyzer

A Django-based intelligent task management system that scores and prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Bisha18/Task_assignment
cd task-analyzer
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Start the development server**
```bash
python manage.py runserver
```

6. **Open the frontend**
Open `frontend/index.html` in your web browser, or run it by live server (VS code),
first runs the backend server then open the frontend

### Running Tests
```bash
cd backend
python manage.py test tasks
```

## Algorithm Explanation

### Overview
The Smart Task Analyzer uses a weighted multi-factor scoring algorithm that balances urgency, importance, effort, and dependency relationships to calculate a priority score for each task. The algorithm is designed to be both intuitive and configurable, allowing for different prioritization strategies.

### Core Scoring Components

**1. Urgency Score (Weight: 35%)**
The urgency component calculates how time-sensitive a task is based on its due date:
- Tasks are evaluated relative to today's date
- Past-due tasks receive exponentially higher urgency scores, with a multiplier that increases based on how many days overdue they are
- Tasks due within 7 days receive progressively higher scores
- Tasks due beyond 7 days receive lower baseline scores
- The urgency score uses a logarithmic decay function for future tasks to prevent extreme values

**2. Importance Score (Weight: 30%)**
Direct user input on a 1-10 scale, normalized to fit within the overall scoring framework. This represents the inherent value or impact of completing the task.

**3. Effort Score (Weight: 20%)**
Lower effort tasks receive higher scores to identify "quick wins":
- Inverted relationship: fewer estimated hours = higher score
- Uses a logarithmic scale to prevent very small tasks from dominating
- Tasks under 1 hour receive a bonus multiplier
- Helps balance between tackling quick wins and important long-term work

**4. Dependency Score (Weight: 15%)**
Tasks that block other tasks (are dependencies for other tasks) receive higher priority:
- Counts how many tasks depend on this task's completion
- Uses a multiplier effect: each dependent task adds to the score
- Helps identify bottleneck tasks in project workflows
- Includes circular dependency detection to prevent infinite loops

### Scoring Strategies

The system supports four distinct prioritization strategies:

1. **Smart Balance** (Default): Weighted combination of all factors (35% urgency, 30% importance, 20% effort, 15% dependencies)

2. **Fastest Wins**: Prioritizes low-effort tasks (50% effort, 25% importance, 25% urgency)

3. **High Impact**: Focuses on importance (60% importance, 20% urgency, 20% dependencies)

4. **Deadline Driven**: Time-focused approach (70% urgency, 20% importance, 10% effort)

### Edge Case Handling

- **Missing Data**: Assigns sensible defaults (medium importance, today's date, 2 hours effort)
- **Invalid Dates**: Converts to current date with error logging
- **Circular Dependencies**: Detected using depth-first search; circular chains are flagged and excluded from dependency bonuses
- **Past Due Tasks**: Receive progressively higher urgency multipliers (1.5x for 1 day overdue, up to 3x for 7+ days)
- **Zero/Negative Effort**: Treated as 0.5 hours (30 minutes minimum)

### Calculation Formula

```
final_score = (urgency * w1) + (importance * w2) + (effort_bonus * w3) + (dependency_bonus * w4)
```

Where weights (w1-w4) vary based on the selected strategy.

## Design Decisions

### 1. Scoring Algorithm Approach
I chose a weighted linear combination model rather than a complex machine learning approach because:
- It's transparent and explainable to users
- Easier to debug and adjust
- Computationally efficient
- Provides consistent, predictable results
- Users can understand why a task received a specific score

### 2. API Structure
Implemented two endpoints rather than one:
- `/api/tasks/analyze/`: Bulk analysis for comprehensive task lists
- `/api/tasks/suggest/`: Top-3 recommendations with explanations

This separation allows the frontend to handle different use cases (full list view vs. quick daily suggestions) without requiring all data to be processed the same way.

### 3. Strategy Toggle Design
Made the scoring strategy configurable via query parameter rather than hardcoded. This allows:
- A/B testing different approaches
- User customization based on personal work style
- Easy extension with new strategies
- Single algorithm implementation with different weight configurations

### 4. Dependency Handling
Used a graph-based approach with DFS for circular dependency detection because:
- Prevents infinite loops in scoring
- Identifies blocking relationships accurately
- Scalable to larger task networks
- Provides clear error messaging

### 5. Frontend Technology Choice
Used vanilla JavaScript instead of a framework because:
- The assignment focuses on problem-solving over framework knowledge
- Keeps dependencies minimal
- Demonstrates fundamental DOM manipulation skills
- Faster to implement for a small application

### 6. Date Handling
All date comparisons use Python's `datetime.date` objects to avoid timezone complications. Since this is a task prioritization system (not a scheduling system), day-level precision is sufficient.

## Time Breakdown

| Component | Time Spent | Notes |
|-----------|------------|-------|
| Algorithm Design & Implementation | 75 min | Including edge case handling and scoring logic |
| Django Models & Serializers | 25 min | Task model and validation |
| API Views & Endpoints | 35 min | Both analyze and suggest endpoints |
| Unit Tests | 30 min | Core algorithm and edge cases |
| Frontend HTML/CSS | 30 min | Layout and responsive design |
| Frontend JavaScript | 40 min | API integration and dynamic updates |
| README Documentation | 25 min | This document |
| Testing & Debugging | 20 min | End-to-end testing |
| **Total** | **~4.5 hours** | |

## Bonus Challenges Attempted

### ✅ Unit Tests (45 min allocated)
Implemented comprehensive unit tests covering:
- Basic scoring functionality
- Edge cases (missing data, invalid dates)
- Circular dependency detection
- Past-due task handling
- Different scoring strategies
- Dependency graph visualization
- Date intelligence (weekends/holidays)
- Eisenhower Matrix view
- Learning system with user feedback


## Technical Notes

- **Database**: Uses SQLite for simplicity; production would benefit from PostgreSQL
- **CORS**: Configured to allow local development; would need proper configuration for production
- **Validation**: Basic validation implemented; would add more robust validation with Django forms
- **Error Handling**: Returns appropriate HTTP status codes with error messages
- **Code Style**: Follows PEP 8 guidelines for Python code

