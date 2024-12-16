class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        # Handle different input types
        try:
            search_input = msgspec.json.decode(request.data, type=FullIdentifier)

        except msgspec.ValidationError as e:
            # Handle msgspec validation errors (missing or invalid fields)
            return Response(
                {"error": f"Validation error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except msgspec.DecodeError as e:
            # Handle json malformed error
            return Response(
                {"error": f"Malformed Json error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            results = identify_accounts(search_input=search_input)

        except ValidationError as e:
            # Handle any validation errors from identify_accounts
            return Response(
                {"error": f"Validation error during processing: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(data=results)

        # search_input = msgspec.json.decode(request.data, type=FullIdentifier)
        # results = identify_accounts(search_input=search_input)
        # return Response(data=results)


class MsgSpecAPIView(APIView):
    parser_classes = [PlainParser]
    renderer_classes = [MsgspecJSONRenderer, BrowsableAPIRenderer]
