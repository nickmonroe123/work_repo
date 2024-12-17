======================================================================
ERROR: test_post_no_data (account_identification.tests.tests.TestIdentifyAccountsView.test_post_no_data)
Test POST request with no data. [0.3986s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/utilities/views.py", line 72, in handle_msgspec_decode
    return msgspec.json.decode(data, type=decoder_type)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
msgspec.ValidationError: Object missing required field `name`

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/pcs3/account_identification/tests/tests.py", line 1056, in test_post_no_data
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
    search_input = self.handle_msgspec_decode(request.data, FullIdentifier)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/utilities/views.py", line 75, in handle_msgspec_decode
    raise ValidationError(f"Validation error: {str(e)}")
django.core.exceptions.ValidationError: ['Validation error: Object missing required field `name`']
