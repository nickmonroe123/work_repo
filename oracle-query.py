class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        search_input = self.handle_msgspec_decode(request.data, FullIdentifier)
        results = identify_accounts(search_input=search_input)
        return Response(data=results)

class MsgSpecAPIView(APIView):
    parser_classes = [PlainParser]
    renderer_classes = [MsgspecJSONRenderer, BrowsableAPIRenderer, JSONRenderer]

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

======================================================================
FAIL: test_post_no_data (account_identification.tests.tests.TestIdentifyAccountsView.test_post_no_data)
Test POST request with no data. [0.0056s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/account_identification/tests/tests.py", line 1055, in test_post_no_data
    response = self.client.post(self.url, data={}, format='json')
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/test.py", line 295, in post
    response = super().post(
               ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/test.py", line 209, in post
    return self.generic('POST', path, data, content_type, **extra)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/test.py", line 233, in generic
    return super().generic(
           ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/django/test/client.py", line 676, in generic
    return self.request(**r)
           ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/test.py", line 285, in request
    return super().request(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/test.py", line 237, in request
    request = super().request(**kwargs)
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/django/test/client.py", line 1092, in request
    self.check_exception(response)
  File "/usr/local/lib/python3.12/site-packages/django/test/client.py", line 805, in check_exception
    raise exc_value
  File "/usr/local/lib/python3.12/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/django/core/handlers/base.py", line 220, in _get_response
    response = response.render()
               ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/django/template/response.py", line 114, in render
    self.content = self.rendered_content
                   ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/response.py", line 59, in rendered_content
    assert renderer, ".accepted_renderer not set on Response"
           ^^^^^^^^
AssertionError: .accepted_renderer not set on Response
