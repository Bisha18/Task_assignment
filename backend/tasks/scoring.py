from datetime import date, datetime, timedelta

def is_weekend(day):
    """Check if the given date is a Saturday (5) or Sunday (6)."""
    return day.weekday() >= 5

def calculate_smart_score(task, all_tasks_map):
    """
    Core Algorithm: "Smart Balance"
    Calculates a priority score based on Urgency, Importance, Effort, and Dependencies.
    """
    score = 0
    explanation = []
    
   
    try:
        today = date.today()
        due = datetime.strptime(task.get('due_date'), '%Y-%m-%d').date()
        days_remaining = (due - today).days
        
        # Date Intelligence: Deprioritize tasks due on weekends
        if is_weekend(due) and days_remaining > 0:
            score -= 5 # Slight penalty for weekend due dates if not already urgent
            explanation.append("Weekend Due Date (Slight Penalty)")

        if days_remaining < 0:
            score += 100  
            explanation.append("OVERDUE")
        elif days_remaining == 0:
            score += 50
            explanation.append("Due today")
        elif days_remaining <= 3:
            score += (30 - (days_remaining * 5)) 
            explanation.append("Due soon")
        else:
            score += max(0, 10 - days_remaining)
            
    except (ValueError, TypeError):
        explanation.append("Invalid date")

    importance = task.get('importance', 5)
    score += importance * 4 
    if importance >= 8:
        explanation.append("High Importance")

    hours = task.get('estimated_hours', 1)
    if hours <= 2:
        score += 5 
        explanation.append("Quick Win")
    elif hours > 10:
        score -= 5 
    
    my_id = task.get('id')
    blocks_count = 0
    
    if my_id:
        for other_task in all_tasks_map.values():
            if my_id in other_task.get('dependencies', []):
                blocks_count += 1
                # Inherit a small priority boost from the blocked task
                score += 5 
                
    if blocks_count > 0:
        explanation.append(f"Blocks {blocks_count} task(s)")

    return round(score, 2), ", ".join(explanation)

def detect_circular_dependencies(tasks):
    """
    DFS approach to detect cycles in the dependency graph.
    Returns a set of task IDs involved in a cycle.
    """
    adj = {t['id']: t.get('dependencies', []) for t in tasks}
    visited = set()
    recursion_stack = set()
    cycle_nodes = set()

    def dfs(node):
        visited.add(node)
        recursion_stack.add(node)
        
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in recursion_stack:
                cycle_nodes.add(node)
                return True
        
        recursion_stack.remove(node)
        return False

    for task in tasks:
        if task['id'] not in visited:
            dfs(task['id'])
            
    return cycle_nodes

def sort_tasks(tasks, strategy="smart"):
    """
    Orchestrator for sorting strategies, including the Eisenhower Matrix view logic.
    """
 
    tasks_map = {t.get('id'): t for t in tasks}
    
    # Check cycles first
    cycles = detect_circular_dependencies(tasks)
    
    processed_tasks = []
    
    for task in tasks:
        t = task.copy()
        
        if t.get('id') in cycles:
            t['priority_score'] = -1
            t['explanation'] = "Circular Dependency Detected!"
            t['is_circular'] = True
            processed_tasks.append(t)
            continue
        
        t['is_circular'] = False

        if strategy == "fastest":
            val = t.get('estimated_hours', 0)
            t['priority_score'] = -val 
            t['explanation'] = f"{val} hours"
            
        elif strategy == "impact":
            val = t.get('importance', 0)
            t['priority_score'] = val
            t['explanation'] = f"Importance: {val}"
            
        elif strategy == "deadline":
            try:
                due = datetime.strptime(t.get('due_date'), '%Y-%m-%d').timestamp()
                t['priority_score'] = -due 
                t['explanation'] = t.get('due_date')
            except:
                t['priority_score'] = 0
        
        elif strategy == "eisenhower":
            # --- Eisenhower Matrix Logic (Urgent vs Important) ---
            importance = t.get('importance', 5)
            
            try:
                today = date.today()
                due = datetime.strptime(t.get('due_date'), '%Y-%m-%d').date()
                days_remaining = (due - today).days
                is_urgent = days_remaining <= 3 
            except:
                is_urgent = False   

            if is_urgent and importance >= 7:
                t['eisenhower_quadrant'] = "Do"
                t['priority_score'] = 4
            elif importance >= 7:
                t['eisenhower_quadrant'] = "Decide"
                t['priority_score'] = 3
            elif is_urgent:
                t['eisenhower_quadrant'] = "Delegate"
                t['priority_score'] = 2
            else:
                t['eisenhower_quadrant'] = "Delete"
                t['priority_score'] = 1
                
            t['explanation'] = f"Quadrant: {t['eisenhower_quadrant']}"
            
        else: 
            score, expl = calculate_smart_score(t, tasks_map)
            t['priority_score'] = score
            t['explanation'] = expl
            
        processed_tasks.append(t)

    return sorted(processed_tasks, key=lambda x: x['priority_score'], reverse=True)