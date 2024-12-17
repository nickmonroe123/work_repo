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
            raise ValidationError(f"Validation error: {str(e)}")
        except msgspec.DecodeError as e:
            raise ValidationError(f"Malformed Json error: {str(e)}")

def test_post_no_data(self):
    """Test POST request with no data."""
    response = self.client.post(self.url, data={}, format='json')
    
    self.assertEqual(response.status_code, 400)
    # self.assertIn('error', response.json())
    self.assertIn('Validation error', response.json())
