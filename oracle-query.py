======================================================================
ERROR: account_identification.tests.tests (unittest.loader._FailedTest.account_identification.tests.tests) [0.0008s]
----------------------------------------------------------------------
ImportError: Failed to import test module: account_identification.tests.tests
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/loader.py", line 396, in _find_test_path
    module = self._get_module_from_name(name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/unittest/loader.py", line 339, in _get_module_from_name
    __import__(name)
  File "/app/src/pcs3/account_identification/tests/tests.py", line 26, in <module>
    @method_decorator(csrf_exempt)
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/django/utils/decorators.py", line 71, in _dec
    raise ValueError(
ValueError: The keyword argument `name` must be the name of a method of the decorated class: <class 'account_identification.tests.tests.TestIdentifyAccountsView'>. Got '' instead.


----------------------------------------------------------------------
Ran 287 tests in 33.619s
