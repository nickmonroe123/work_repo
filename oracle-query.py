class MsgSpecAPIView(APIView):
    parser_classes = [PlainParser]
    renderer_classes = [MsgspecJSONRenderer, BrowsableAPIRenderer]
    
    def process_request(self, request_data, decoder_type):
        """Abstract method to be implemented by child classes"""
        raise NotImplementedError
    
    def handle_msgspec_decode(self, data, decoder_type):
        try:
            return msgspec.json.decode(data, type=decoder_type)
        except msgspec.ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except msgspec.DecodeError as e:
            raise ValidationError(f"Malformed Json error: {str(e)}")

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        # Decode the input
        search_input = self.handle_msgspec_decode(request.data, FullIdentifier)
        
        # Process the request
        results = identify_accounts(search_input=search_input)
        
        return Response(data=results)
