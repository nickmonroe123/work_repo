class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        search_input = self.handle_msgspec_decode(request.data, FullIdentifier)
        results = identify_accounts(search_input=search_input)
        return Response(data=results, status=status.HTTP_200_OK)

class MsgSpecAPIView(APIView):
    parser_classes = [PlainParser]
    renderer_classes = [MsgspecJSONRenderer, BrowsableAPIRenderer, JSONRenderer]  # Removed MsgspecJSONRenderer as it's not standard

    def handle_msgspec_decode(self, data, decoder_type):
        try:
            if isinstance(data, (bytes, str)):
                return msgspec.json.decode(data, type=decoder_type)
            return msgspec.convert(data, type=decoder_type)
        except msgspec.ValidationError as e:
            return Response (
                {"error": f"Validation error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except msgspec.DecodeError as e:
            return Response (
                {"error": f"Malformed Json error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

I have the IdentifyAccountsView which is an api that will be called from externally. Can you help me setup the code to be very concise and small so that whenever the handle_msgspec_decode returns a bad response it fully
returns the response as a 400 bad request. Currently it returns that 400 and then conitnues running the code?
