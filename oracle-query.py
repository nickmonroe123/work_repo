from django.core.handlers.wsgi import WSGIRequest
from rest_framework.views import APIView
from rest_framework.response import Response
import msgspec
import json

class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        try:
            # If request.data is already a dict, convert it to JSON string first
            if isinstance(request.data, dict):
                json_str = json.dumps(request.data).encode('utf-8')
                search_input = msgspec.json.decode(json_str, type=FullIdentifier)
            else:
                # Handle case where data might come as raw JSON
                search_input = msgspec.json.decode(request.data, type=FullIdentifier)
        except Exception as e:
            # Optional: Add logging here if needed
            raise ValueError(f"Invalid input format: {str(e)}")
            
        results = identify_accounts(search_input=search_input)
        return Response(data=results)
