from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import msgspec
import json
from django.core.exceptions import ValidationError
from typing import Any

class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        try:
            # Check if we have any data at all
            if not request.data:
                return Response(
                    {"error": "No data provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Handle different input types
            try:
                if isinstance(request.data, dict):
                    json_str = json.dumps(request.data).encode('utf-8')
                else:
                    json_str = request.data
                
                search_input = msgspec.json.decode(json_str, type=FullIdentifier)
            
            except msgspec.ValidationError as e:
                # Handle msgspec validation errors (missing or invalid fields)
                return Response(
                    {"error": f"Validation error: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except json.JSONDecodeError as e:
                # Handle invalid JSON
                return Response(
                    {"error": f"Invalid JSON format: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except UnicodeDecodeError as e:
                # Handle encoding issues
                return Response(
                    {"error": f"Invalid character encoding: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Attempt to process the request
                results = identify_accounts(search_input=search_input)
                
                # Verify results is not None
                if results is None:
                    return Response(
                        {"error": "No results returned from processing"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                return Response(data=results)
                
            except ValidationError as e:
                # Handle any validation errors from identify_accounts
                return Response(
                    {"error": f"Validation error during processing: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                # Handle any other unexpected errors from identify_accounts
                return Response(
                    {"error": f"Error processing request: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            # Catch any other unexpected errors
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
