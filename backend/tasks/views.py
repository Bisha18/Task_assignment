from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from .scoring import sort_tasks

class AnalyzeTaskView(APIView):
    """
    POST /api/tasks/analyze/
    Accepts a list of tasks and a strategy query param.
    Returns prioritized list.
    """
    def post(self, request):
        tasks = request.data
        if not isinstance(tasks, list):
            return Response(
                {"error": "Expected a list of tasks"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Updated to include 'eisenhower' strategy
        strategy = request.query_params.get('strategy', 'smart')
        
        # Validate minimal fields
        for t in tasks:
            if 'title' not in t or 'due_date' not in t:
                 return Response(
                    {"error": "All tasks must have title and due_date"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        sorted_data = sort_tasks(tasks, strategy)
        return Response(sorted_data)

class SuggestTaskView(APIView):
    """
    GET /api/tasks/suggest/ (Simulated via POST for payload)
    Accepts tasks and returns top 3 for today.
    """
    def post(self, request):
        tasks = request.data
        if not isinstance(tasks, list):
            return Response({"error": "List required"}, status=400)
            
        # Use smart strategy for suggestions
        sorted_tasks = sort_tasks(tasks, 'smart')
        
        # Filter top 3 valid tasks
        suggestions = [t for t in sorted_tasks if t['priority_score'] > 0][:3]
        
        return Response({
            "suggestions": suggestions,
            "message": "Here are your top priorities for today."
        })