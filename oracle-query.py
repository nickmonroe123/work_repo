======================================================================
ERROR: test_internal_record_address_parsing_0_standard_address (account_identification.tests.tests.TestInternalRecord.test_internal_record_address_parsing_0_standard_address) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 33, in test_internal_record_address_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'addressLine1'

======================================================================
ERROR: test_internal_record_address_parsing_1_address_with_apt (account_identification.tests.tests.TestInternalRecord.test_internal_record_address_parsing_1_address_with_apt) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 33, in test_internal_record_address_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'addressLine1'

======================================================================
ERROR: test_internal_record_address_parsing_2_empty_address (account_identification.tests.tests.TestInternalRecord.test_internal_record_address_parsing_2_empty_address) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 33, in test_internal_record_address_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'addressLine1'

======================================================================
ERROR: test_internal_record_address_parsing_3_complex_address (account_identification.tests.tests.TestInternalRecord.test_internal_record_address_parsing_3_complex_address) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 33, in test_internal_record_address_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'addressLine1'

======================================================================
ERROR: test_to_identified_account_phone_parsing_0_full_phone (account_identification.tests.tests.TestInternalRecord.test_to_identified_account_phone_parsing_0_full_phone) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 61, in test_to_identified_account_phone_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'primaryPhone'

======================================================================
ERROR: test_to_identified_account_phone_parsing_1_partial_phone (account_identification.tests.tests.TestInternalRecord.test_to_identified_account_phone_parsing_1_partial_phone) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 61, in test_to_identified_account_phone_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'primaryPhone'

======================================================================
ERROR: test_to_identified_account_phone_parsing_2_short_phone (account_identification.tests.tests.TestInternalRecord.test_to_identified_account_phone_parsing_2_short_phone) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 61, in test_to_identified_account_phone_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'primaryPhone'

======================================================================
ERROR: test_to_identified_account_phone_parsing_3_empty_phone (account_identification.tests.tests.TestInternalRecord.test_to_identified_account_phone_parsing_3_empty_phone) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 61, in test_to_identified_account_phone_parsing
    record = InternalRecord(
             ^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'primaryPhone'

======================================================================
ERROR: test_oracle_name_parsing_0_standard_name (account_identification.tests.tests.TestOracleDESRecord.test_oracle_name_parsing_0_standard_name) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 90, in test_oracle_name_parsing
    record = OracleDESRecord(ACCT_NAME=input_name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'ACCT_NAME'

======================================================================
ERROR: test_oracle_name_parsing_1_comma_in_name (account_identification.tests.tests.TestOracleDESRecord.test_oracle_name_parsing_1_comma_in_name) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 90, in test_oracle_name_parsing
    record = OracleDESRecord(ACCT_NAME=input_name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'ACCT_NAME'

======================================================================
ERROR: test_oracle_name_parsing_2_multiple_commas (account_identification.tests.tests.TestOracleDESRecord.test_oracle_name_parsing_2_multiple_commas) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 90, in test_oracle_name_parsing
    record = OracleDESRecord(ACCT_NAME=input_name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'ACCT_NAME'

======================================================================
ERROR: test_oracle_name_parsing_3_empty_name (account_identification.tests.tests.TestOracleDESRecord.test_oracle_name_parsing_3_empty_name) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 90, in test_oracle_name_parsing
    record = OracleDESRecord(ACCT_NAME=input_name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'ACCT_NAME'

======================================================================
ERROR: test_oracle_name_parsing_4_no_comma (account_identification.tests.tests.TestOracleDESRecord.test_oracle_name_parsing_4_no_comma) [0.0042s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/parameterized/parameterized.py", line 620, in standalone_func
    return func(*(a + p.args), **p.kwargs, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/account_identification/tests/tests.py", line 90, in test_oracle_name_parsing
    record = OracleDESRecord(ACCT_NAME=input_name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Unexpected keyword argument 'ACCT_NAME'
