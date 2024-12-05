________________________________________________________________________________________ test_oracle_des_record_struct _________________________________________________________________________________________

    def test_oracle_des_record_struct():
        # Full Oracle DES record
>       record1 = OracleDESRecord(
            ACCT_NUM="98765",
            PRIMARY_NUMBER="5551234567",
            ACCT_NAME="Doe,John",
            PSTL_CD_TXT_BLR="12345",
            CITY_NM_BLR="Anytown",
            STATE_NM_BLR="NY",
            BLR_ADDR1_LINE="100 Main St",
            BLR_ADDR2_LINE="Apt 4B"
        )
E       TypeError: Unexpected keyword argument 'ACCT_NUM'

tests.py:201: TypeError
_________________________________________________________________________________________ test_data_source_conversions _________________________________________________________________________________________

    def test_data_source_conversions():
        # Convert between different record types
>       oracle_record = OracleDESRecord(
            ACCT_NUM="12345",
            ACCT_NAME="Doe,John",
            PRIMARY_NUMBER="5551234567"
        )
E       TypeError: Unexpected keyword argument 'ACCT_NUM'

tests.py:295: TypeError
_________________________
