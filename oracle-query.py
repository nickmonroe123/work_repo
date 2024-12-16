
def query_with_params(sql_query: str, params: Dict = None) -> List[OracleDESRecord]:
    """Executes a parameterized query and returns results as OracleDESRecords.

    Args:
        connection (cx_Oracle.Connection): Database connection
        sql_query (str): SQL query with bind variables
        params (Dict): Dictionary of parameter names and values

    Returns:
        List[OracleDESRecord]: List of OracleDESRecords containing query results
    """
    try:
        # Connect
        connection = connect_to_oracle(**constants.DB_CONFIG)
        # Create cursor
        cursor = connection.cursor()

        # Execute query with parameters
        cursor.execute(sql_query, params or {})

        # Get column names
        columns = [col[0] for col in cursor.description]

        # Fetch results and convert to list of dictionaries
        results = []
        for row in cursor:
            results.append(dict(zip(columns, row)))

        no_null = replace_null_with_empty_string(results)
        return [msgspec.convert(item, OracleDESRecord) for item in no_null]

    except oracledb.Error as error:
        logger.info(f"Database error: {error}")
        raise

    finally:
        if cursor:
            cursor.close()


def replace_null_with_empty_string(d):
    """Replaces all None values in a dictionary with empty strings."""
    try:
        if len(d) > 0:
            for record in d:
                for k, v in record.items():
                    if v is None:
                        record[k] = ""
        return d
    except Exception as e:
        logger.info(
            f"Error in replace_null_with_empty_string when removing null values!: {e}"
        )
        return


def search_with_phone(external_record: GeneralRequest) -> list[OracleDESRecord]:
    query = """
            SELECT
            ACCT_NUM, ACCT_NAME, ACCT_TYPE_CD,
            BLR_ADDR1_LINE,
            BLR_ADDR2_LINE, CITY_NM_BLR, STATE_NM_BLR,
            PSTL_CD_TXT_BLR,
            EMAIL_ADDR, SPC_DIV_ID, SRC_SYS_CD,
            'No uCan' as UCAN,
            CASE
            WHEN REPLACE(upper(ACCT_HOME_PHONE), ' ', '' ) = REPLACE(UPPER(:acct_home_phone), ' ', '' )
            THEN ACCT_HOME_PHONE
            WHEN REPLACE(upper(ACCT_WORK_PHONE), ' ', '' ) = REPLACE(UPPER(:acct_work_phone), ' ', '' )
            THEN ACCT_WORK_PHONE
            WHEN REPLACE(upper(PRTY_HOME_PHONE), ' ', '' ) = REPLACE(UPPER(:prty_home_phone), ' ', '' )
            THEN PRTY_HOME_PHONE
            WHEN REPLACE(upper(PRTY_WORK_PHONE), ' ', '' ) = REPLACE(UPPER(:prty_work_phone), ' ', '' )
            THEN PRTY_WORK_PHONE
            WHEN REPLACE(upper(OTHER_PHONE), ' ', '' ) = REPLACE(UPPER(:other_phone), ' ', '' )
            THEN OTHER_PHONE
            ELSE
            ''
            END AS PRIMARY_NUMBER,
            CASE
            WHEN TO_CHAR(trunc(acct_clse_dt)) IS NULL
            AND TO_CHAR(trunc(acct_open_dt), 'yyyy-mm-dd') = '1900-01-01' THEN
            'Never'
            WHEN ( TO_CHAR(trunc(acct_open_dt), 'yyyy-mm-dd') > '1900-01-01'
            AND TO_CHAR(trunc(acct_clse_dt)) IS NULL )
            OR ( TO_CHAR(trunc(acct_open_dt), 'yyyy-mm-dd') > '1900-01-01'
            AND TO_CHAR(trunc(acct_clse_dt), 'yyyy-mm-dd') = '9999-12-31' ) THEN
            'Active'
            ELSE
            'Former'
            END AS accountStatus
            FROM DSP_UAT_PRST.VW_DSP_PRVCY_BILLER_ACCT
            WHERE REPLACE(upper(ACCT_HOME_PHONE), ' ', '' ) = REPLACE(UPPER(:acct_home_phone), ' ', '' )
            OR REPLACE(upper(ACCT_WORK_PHONE), ' ', '' ) = REPLACE(UPPER(:acct_work_phone), ' ', '' )
            OR REPLACE(upper(PRTY_HOME_PHONE), ' ', '' ) = REPLACE(UPPER(:prty_home_phone), ' ', '' )
            OR REPLACE(upper(PRTY_WORK_PHONE), ' ', '' ) = REPLACE(UPPER(:prty_work_phone), ' ', '' )
            OR REPLACE(upper(OTHER_PHONE), ' ', '' ) = REPLACE(UPPER(:other_phone), ' ', '' )
            """
    # Parameter values
    params = {
        "acct_home_phone": external_record.phone_number,
        "acct_work_phone": external_record.phone_number,
        "prty_home_phone": external_record.phone_number,
        "prty_work_phone": external_record.phone_number,
        "other_phone": external_record.phone_number,
    }

    return query_with_params(query, params)
