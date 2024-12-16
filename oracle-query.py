class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        search_input = msgspec.json.decode(request.data, type=FullIdentifier)
        # search_input = msgspec.json.decode(json.dumps(request.data).encode('utf-8'), type=FullIdentifier)
        results = identify_accounts(search_input=search_input)
        return Response(data=results)


class TestIdentifyAccountsView(APITestCase):
    """API Tests."""

    # @patch('core.models.Request.handle_new_request', Mock())
    # def setUp(self):
    def setUp(self):
        super().setUp()
        user = get_user_model()._default_manager.create_user(username='test_user')
        self.client.force_authenticate(user=user)

        self.url = '/account_identification/api/'  # Full path based on URL configuration
        self.valid_payload = {
            "name": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "",
                "suffix": "",
                "prefix": ""
            },
            "phone_number": {
                "country_code": "",
                "area_code": "555",
                "exchange": "123",
                "line_number": "4567",
                "extension": "",
                "type_code": ""
            },
            "address": {
                "city": "Springfield",
                "state": "IL",
                "line1": "123 Main St",
                "postal_code": "62701",
                "line2": "",
                "country_code": ""
            },
            "email": "john.doe@example.com"
        }

    @patch('account_identification.tasks.identify_accounts')
    def test_post_success(self, mock_identify):
        # Mock the identify_accounts function to return a successful response
        mock_identify.return_value = [{"match_score": 100.0}]

        response = self.client.post(
            self.url,
            json=self.valid_payload
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"match_score": 100.0}])
        mock_identify.assert_called_once()

======================================================================
ERROR: test_post_success (account_identification.tests.tests.TestIdentifyAccountsView.test_post_success) [0.3425s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 73, in test_post_success
    response = self.client.post(
               ^^^^^^^^^^^^^^^^^
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
  File "/usr/local/lib/python3.12/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/django/views/decorators/csrf.py", line 65, in _view_wrapper
    return view_func(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/django/views/generic/base.py", line 104, in view
    return self.dispatch(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/views.py", line 509, in dispatch
    response = self.handle_exception(exc)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/rest_framework/views.py", line 469, in handle_exception
    self.raise_uncaught_exception(exc)
  File "/usr/local/lib/python3.12/site-packages/rest_framework/views.py", line 480, in raise_uncaught_exception
    raise exc
  File "/usr/local/lib/python3.12/site-packages/rest_framework/views.py", line 506, in dispatch
    response = handler(request, *args, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/views.py", line 11, in post
    search_input = msgspec.json.decode(request.data, type=FullIdentifier)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: a bytes-like object is required, not 'dict'

