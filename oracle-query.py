import json
import logging
import re
from operator import itemgetter
from typing import Dict, List, Tuple

import msgspec
import oracledb
import requests
from account_identification import constants
from account_identification.structs import (
    FullIdentifier,
    GeneralRequest,
    IdentifiedAccount,
    InternalRecord,
    InternalRequestLike,
    OracleDESRecord,
)
from django.conf import settings
from thefuzz import fuzz

logger = logging.getLogger(__name__)


def lower_no_spaces(input: str) -> str:
    return input.lower().replace(' ', '')


def normalize_address(address: str) -> str:
    """Normalize an address by replacing street abbreviations, removing spaces,
    and lowercasing."""
    cleaned = []
    for word in address.split():
        word = word.upper()
        for abbr, full in constants.STREET_ACRO.items():
            pattern = r'\b{}\b'.format(re.escape(abbr))
            if re.search(pattern, word):
                cleaned.append(full.lower())
        cleaned.append(word.lower())
    return ''.join(cleaned)


class AccountProcess:
    """Valuable Links to Overall Process
    Account Identification Process: https://chalk.charter.com/display/ITDMIG/Account+Identification+and+Hydration
    getSPCAccountv1x1 shown in process above: https://chalk.charter.com/display/EWS/getSpcAccountDivision+V+1.1#
    findAccountx1x0 shown in process above: https://chalk.charter.com/display/EWS/findAccount+V+1.0
    """

    system_id = settings.SPECTRUM_CORE_SYSTEM_ID
    url_accounts = settings.SPECTRUM_CORE_ACCOUNT
    url_billing = settings.SPECTRUM_CORE_BILLING

    # This list encompasses the first 5 api calls to getSpcAccountDivisionV1x1 (4) and findAccountV1x0 (1)
    core_services_list: list[InternalRequestLike] = []

    # This list holds the output of Identified accounts
    output_list: list[IdentifiedAccount] = []

    # This list encompasses the queries against the oracle des database
    oracle_des_list: list[OracleDESRecord] = []

    # External Record (The starting point of requested information)
    ext_request = GeneralRequest()

    # Keep Track of the Fuzzy Amount
    fuzzy_amount = 0

    # Bad phone number list
    bad_numbers = constants.BAD_NUMBERS

    ###################################################################################################
    # Here is the process of the 4 api calls that call spectrum core services

    def _parse_spectrum_core_api(
        self,
        payload: dict,
        function_url: str,
        function_name: str,
        post_processing_function=None,
        response_key='getSpcAccountDivisionResponse',
        response_list_key='spcAccountDivisionList',
    ) -> list[InternalRecord]:
        """Helper function for parsing information from spectrum core services
        account API."""
        try:
            # Make the post request call out to spectrum core services
            # TODO: Need to add the certificate authentication here
            response = requests.request("POST", function_url, json=payload)
            # Will return an HTTPError object if an error has occurred during the process
            response.raise_for_status()
            # For now if it fails return empty list. Its possible there are just no records here
            response_key_contents = response.json().get(response_key)
            if response_key_contents is None:
                logger.error(
                    f"The format of the JSON has been changed during {function_name}! New format: {response.json()}"
                )
                raise ValueError('Format of Spectrum Core Account API has changed')
            core_services_list_to_add = response_key_contents.get(response_list_key, [])
            if post_processing_function is not None:
                core_services_list_to_add = post_processing_function(
                    core_services_list_to_add
                )
            core_services_list_to_add = [
                msgspec.convert(x, type=InternalRecord)
                for x in core_services_list_to_add
            ]
            return core_services_list_to_add
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in spectrum core api search: {function_name}")
            raise e

    def phone_search(self):
        """/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1
        Type of Possible Requests: Post
        Determines the divisionID, unique account ID and other account information
        """
        # Core services requires phone number to be 10 digits to search.
        if (
            len(self.ext_request.phone_number) != 10
            or self.ext_request.phone_number in constants.BAD_NUMBERS
        ):
            logger.warning(
                f"Phone number is either not 10 digits, or a non-allowed number."
            )
            return
        # Set up the api call itself, only using phone number here
        payload = {
            "getSpcAccountDivisionRequest": {
                "systemID": self.system_id,
                "telephoneNumber": self.ext_request.phone_number,
            }
        }
        self.core_services_list += self._parse_spectrum_core_api(
            payload,
            function_url=self.url_accounts, function_name='phone_search'
        )

    # This second function will be the retrieval of accounts that have a name and zip match
    def name_zip_search(self):
        # zipcode must be 5 digits, anything less will fail in core services, we handle anything extra in parsing
        if (
            len(self.ext_request.zipcode5) != 5
            or self.ext_request.first_name == ""
            or self.ext_request.last_name == ""
        ):
            logger.warning(f"Zip is either not 5 digits, or a name is an empty value.")
            return
        # Set up the api call itself, only using phone number here
        payload = {
            "getSpcAccountDivisionRequest": {
                "systemID": self.system_id,
                "firstName": self.ext_request.first_name,
                "lastName": self.ext_request.last_name,
                "zipCode5": self.ext_request.zipcode5,
            }
        }
        self.core_services_list += self._parse_spectrum_core_api(
            payload,
            function_url=self.url_accounts, function_name='name_zip_search'
        )

    # This third function will be the retrieval of accounts that have an email match
    def email_search(self):
        # If bad data just leave
        if self.ext_request.email_address == "":
            logger.warning(f"Lacking sufficient data to search on email address.")
            return
        # Set up the api call itself, only using phone number here
        payload = {
            "getSpcAccountDivisionRequest": {
                "systemID": self.system_id,
                "emailAddress": self.ext_request.email_address,
            }
        }
        self.core_services_list += self._parse_spectrum_core_api(
            payload,
            function_url=self.url_accounts, function_name='email_search'
        )

    def clean_address_search(self, json_list: list[dict]) -> list[dict]:
        """Clean the address information by ensuring that if an apartment is
        provided in the request, it either matches the addressLine2 field or
        the full address."""
        json_list_cleaned = []
        for record in json_list:
            try:
                if re.sub("[^0-9]", "", record['addressLine2']) == re.sub(
                    "[^0-9]", "", self.ext_request.apartment
                ):
                    json_list_cleaned.append(record)
            except:
                """Issue: sometimes addressLine1 contains apt. example: '7330 ETON AVE APT DD86770'. No addressLine2.
                Cant do this through query due to wildcard automatically being set.
                We will handle by checking for 1
                """
                full_address = f"{self.ext_request.street_number}{self.ext_request.street_name}{self.ext_request.apartment}"
                if full_address.replace(' ', '') == record['addressLine1'].replace(
                    ' ', ''
                ):
                    json_list_cleaned.append(record)
        return json_list_cleaned

    # This fourth function will be the retrieval of accounts that have address match
    def address_search(self):
        # If bad data just leave
        if self.ext_request.street_number == "" or self.ext_request.street_name == "" or \
                (len(self.ext_request.state) != 2 and len(self.ext_request.state) != 0) or \
                (len(self.ext_request.zipcode5) != 5 and len(self.ext_request.zipcode5) != 0) or \
                (len(self.ext_request.state) != 2 and len(self.ext_request.zipcode5) != 5):
            logger.warning(f"Lacking sufficient data to search on address.")
            return
        # Set up the api call itself, only using address here
        payload = {
            "getSpcAccountDivisionRequest": {
                "systemID": self.system_id,
                "streetNumber": self.ext_request.street_number,
                "streetName": self.ext_request.street_name,
                "city": self.ext_request.city,
                "state": self.ext_request.state,
                "zipCode5": self.ext_request.zipcode5,
            }
        }
        self.core_services_list += self._parse_spectrum_core_api(
            payload,
            function_url=self.url_accounts,
            function_name='address_search',
            post_processing_function=lambda x: self.clean_address_search(x),
        )

    #################################################################################################
    # Here is the 1 api that we call core spectrum for to get info based on billing records
    # Get the UCAN and email address for any billing records that are found
    def billing_info_specific(self, dataset: list[dict]) -> list[dict]:
        changing_dataset = dataset
        for record in changing_dataset:
            # If bad data just leave
            if record['accountNumber'] == "":
                logger.warning(f"Account number is missing, cannot continue!")
                continue

            # Set up the api call itself, only using account number here
            payload = {
                "getSpcAccountDivisionRequest": {
                    "systemID": self.system_id,
                    "accountNumber": record['accountNumber'],
                }
            }
            account_division_list = self._parse_spectrum_core_api(
                payload,
                function_url=self.url_accounts,
                function_name='billing_info_specific',
            )
            if not account_division_list:
                logger.warning(
                    f"We have found no matching records for this  account number: {record['accountNumber']}"
                )
                continue
            # populate the specific values
            account_division_response = account_division_list[0]
            record['uCAN'] = account_division_response.ucan
            record['emailAddress'] = account_division_response.email_address
        return changing_dataset

    # This fifth function will be the retrieval of accounts that have an billing address match
    def billing_search(self):
        # If bad data just leave
        if self.ext_request.last_name == "" or self.ext_request.first_name == "" or \
                (len(self.ext_request.state) != 2 and len(self.ext_request.state) != 0) or \
                (len(self.ext_request.zipcode5) != 5 and len(self.ext_request.zipcode5) != 0) or \
                (len(self.ext_request.state) != 2 and len(self.ext_request.zipcode5) != 5):
            logger.warning(
                f"Lacking sufficient data to search on billing address search."
            )
            return
        # Set up the api call itself, only using phone number here
        payload = {
            "findAccountRequest": {
                "systemID": self.system_id,
                "lastName": self.ext_request.last_name,
                "firstName": self.ext_request.first_name,
                "zipCode5": self.ext_request.zipcode5,
                "streetNumber": self.ext_request.street_number,
                "state": self.ext_request.state,
                "city": self.ext_request.city,
            }
        }

        self.core_services_list.extend(
            self._parse_spectrum_core_api(
                payload,
                function_url=self.url_billing,
                function_name='billing_search',
                response_key='findAccountResponse',
                response_list_key='accountList',
                post_processing_function=lambda x: self.billing_info_specific(x),
            )
        )

    #################################################################################################
    # Here is the process that we use to get oracle information (references models.py)
    def oracle_des_process(self):
        """One thing we want to setup is to only call the specific queries IF
        the value is populated in the json!"""
        # Only do this first query if the phone number is valid!
        if (
            len(self.ext_request.phone_number) == 10
            and self.ext_request.phone_number not in constants.BAD_NUMBERS
        ):
            self.oracle_des_list.extend(search_with_phone(self.ext_request))

        if self.ext_request.street_name and self.ext_request.street_number:
            self.oracle_des_list.extend(search_with_address(self.ext_request))

        if self.ext_request.email_address:
            self.oracle_des_list.extend(search_with_email(self.ext_request))

        if self.ext_request.first_name or self.ext_request.zipcode5:
            self.oracle_des_list.extend(search_with_zip_name(self.ext_request))

    ###################################################################################
    # Start of Fuzzy searching

    def check_match(
        self,
        record: InternalRequestLike,
    ) -> IdentifiedAccount:
        self.fuzzy_amount = 0

        # Only run the process if external AND 1 of the 2 internal phone numbers are valid
        if self.ext_request.phone_number not in constants.BAD_NUMBERS and (
            record.phone_number not in constants.BAD_NUMBERS
            or record.secondary_number not in constants.BAD_NUMBERS
        ):
            phone_accuracy_primary_number = fuzz.WRatio(
                self.ext_request.phone_number, record.phone_number
            )
            phone_accuracy_secondary_number = fuzz.WRatio(
                self.ext_request.phone_number, record.secondary_number
            )
            self.fuzzy_amount += max(
                phone_accuracy_primary_number, phone_accuracy_secondary_number
            )

        # Now we want to calculate the fuzzy score for email address
        self.fuzzy_amount += fuzz.WRatio(
            lower_no_spaces(self.ext_request.email_address),
            lower_no_spaces(record.email_address),
        )

        # Now we want to check on the name
        ext_first = lower_no_spaces(self.ext_request.first_name)
        ext_last = lower_no_spaces(self.ext_request.last_name)
        int_first = lower_no_spaces(record.first_name)
        int_last = lower_no_spaces(record.last_name)
        # Get the fuzzy score for a couple scenarios
        # Scenario 1: name is given correctly
        correct_accuracy = fuzz.WRatio((ext_first + ext_last), (int_first + int_last))
        # Scenario 2: name is given reversed (i.e. john doe given as doe john)
        incorrect_accuracy = fuzz.WRatio((ext_last + ext_first), (int_first + int_last))
        # Scenario 3: check if there is a common nickname ordered correctly
        if constants.NICKNAMES.get(ext_first.upper()) == int_first.upper():
            ext_first = int_first
        elif constants.NICKNAMES.get(int_first.upper()) == ext_first.upper():
            ext_first = int_first
        nickname_accuracy = fuzz.WRatio((ext_first + ext_last), (int_first + int_last))

        self.fuzzy_amount += max(
            correct_accuracy, incorrect_accuracy, nickname_accuracy
        )

        #  Now we want to deal with the address (Street #, State, Zip Code)
        # Split up street name and street number
        ext_full = " ".join(
            (
                self.ext_request.street_number,
                self.ext_request.street_name,
                self.ext_request.city,
                self.ext_request.state,
            )
        )

        # Scenario 1: external address and internal address with apt match
        apt_accuracy = fuzz.WRatio(
            lower_no_spaces(record.full_address),
            lower_no_spaces(ext_full),
        )
        # Scenario 2: external address and internal address no apt match
        no_apt_accuracy = fuzz.WRatio(
            lower_no_spaces(record.full_address_no_apt),
            lower_no_spaces(ext_full),
        )

        # Try normalizing to account for street abbreviations
        normalized_int_record = normalize_address(record.full_address)
        normalized_int_record_no_apt = normalize_address(record.full_address_no_apt)
        normalized_ext_record = normalize_address(ext_full)

        # Scenario 3: normalized external address and internal address with apt match
        apt_accuracy_norm = fuzz.WRatio(normalized_int_record, normalized_ext_record)
        # Scenario 4: normalized external address and internal address no apt match
        no_apt_accuracy_norm = fuzz.WRatio(
            normalized_int_record_no_apt, normalized_ext_record
        )

        self.fuzzy_amount += max(
            apt_accuracy, no_apt_accuracy, apt_accuracy_norm, no_apt_accuracy_norm
        )

        record_to_return = record.to_identified_account()
        record_to_return.match_score = self.fuzzy_amount
        record_to_return.billing_account_number = record.account_number

        return record_to_return

    def confirmed_matches(self, clean_recordset: list) -> list[IdentifiedAccount]:
        """Perform fuzzy matching on the provided list."""
        return [self.check_match(record) for record in clean_recordset]

    #################################################################################################
    # Needs to be done AFTER account fuzzy matching has occurred with how we remove duplicates
    # Sorting on fuzzy score and then removing based on account number
    def clean_output_list(self) -> list[IdentifiedAccount]:
        sorted_data: list[IdentifiedAccount] = sorted(
            self.output_list, key=itemgetter('match_score'), reverse=True
        )
        # Remove duplicates based on the fourth item
        unique_data = []
        seen = set()
        for item in sorted_data:
            acct_num = item.billing_account_number
            if acct_num not in seen and acct_num != '':
                unique_data.append(item)
                seen.add(acct_num)

        return unique_data

    def full_search(self, search_input: FullIdentifier) -> list[IdentifiedAccount]:
        # Log the request to start so we have a record of its existence
        logger.info('This is the start of a new account identification process.')
        logger.info('Requestor info:')
        logger.info(search_input)

        # Fill out account_info dictionary, this will parse the data for all of the needed columns
        self.ext_request = GeneralRequest.from_full_identifier(search_input)

        # Search the spectrum core services api for phone account matches
        self.phone_search()
        # Search the spectrum core services api for name zip combo matches
        self.name_zip_search()
        # Search the spectrum core services api for email account matches
        self.email_search()
        # Search the spectrum core services api for address matches
        self.address_search()

        # Make the final call out to the finalAccountv1x0
        self.billing_search()
        # Call fuzzy match for the 1 billing api call
        self.output_list = self.confirmed_matches(self.core_services_list)

        # Run through the oracle des process
        self.oracle_des_process()
        # Call fuzzy match for the oracle des process
        self.output_list.extend(self.confirmed_matches(self.oracle_des_list))

        # Clean the dataset to get distinct account numbers for the first 1 billing api call to core services
        output = self.clean_output_list()

        logger.info('This is the end of an account identification process.')
        logger.info('\n')
        return output


def connect_to_oracle(
    username: str, password: str, connection_str: str
) -> oracledb.Connection:
    """Establishes connection to Oracle database.

    Args:
        username (str): Database username
        password (str): Database password
        host (str): Database host address
        port (str): Database port number
        service_name (str): Oracle service name

    Returns:
        cx_Oracle.Connection: Database connection object
    """


    dsn = oracledb.makedsn(host=host, port=port, service_name=service_name)
    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    # connection = oracledb.connect(user=username, password=password, dsn=connection_str)
    return connection


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


def search_with_address(external_record: GeneralRequest) -> list[OracleDESRecord]:
    query = """
            SELECT
            ACCT_NUM, ACCT_NAME, ACCT_TYPE_CD,
            BLR_ADDR2_LINE, CITY_NM_BLR, STATE_NM_BLR,
            EMAIL_ADDR, SPC_DIV_ID,
            'No uCan' as UCAN,
            ACCT_HOME_PHONE AS PRIMARY_NUMBER, SRC_SYS_CD,

            CASE
            WHEN REPLACE(upper(PSTL_CD_TXT), ' ', '' ) LIKE REPLACE(upper(:PSTL_CD_TXT), ' ', '' )
                THEN PSTL_CD_TXT
            WHEN REPLACE(upper(PSTL_CD_TXT_BLR), ' ', '' ) LIKE REPLACE(upper(:PSTL_CD_TXT_BLR), ' ', '' )
                THEN PSTL_CD_TXT
            ELSE
            ''
            END AS PSTL_CD_TXT_BLR,

            CASE
            WHEN REPLACE(upper(SRVC_ADDR1_LINE), ' ', '' ) = REPLACE(upper(:SRVC_ADDR1_LINE ), ' ', '' )
                THEN SRVC_ADDR1_LINE
            WHEN REPLACE(upper(BLR_ADDR1_LINE), ' ', '' ) = REPLACE(upper(:BLR_ADDR1_LINE), ' ', '' )
                THEN BLR_ADDR1_LINE
            ELSE
            ''
            END AS BLR_ADDR1_LINE,

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
            WHERE (REPLACE(upper(PSTL_CD_TXT), ' ', '' ) LIKE REPLACE(upper(:PSTL_CD_TXT), ' ', '' )
            OR REPLACE(upper(PSTL_CD_TXT_BLR), ' ', '' ) LIKE REPLACE(upper(:PSTL_CD_TXT_BLR), ' ', '' ))
            AND
            (REPLACE(upper(CITY_NM_BLR), ' ', '' ) = REPLACE(upper(:city ), ' ', '' ))
            AND
            (REPLACE(upper(STATE_NM_BLR), ' ', '' ) = REPLACE(upper(:state ), ' ', '' ))
            AND
            (REPLACE(upper(SRVC_ADDR1_LINE), ' ', '' ) = REPLACE(upper(:SRVC_ADDR1_LINE ), ' ', '' )
            OR REPLACE(upper(BLR_ADDR1_LINE), ' ', '' ) = REPLACE(upper(:BLR_ADDR1_LINE), ' ', '' ))
            """
    # Parameter values
    params = {
        "PSTL_CD_TXT": external_record.zipcode5 + "%",
        "PSTL_CD_TXT_BLR": external_record.zipcode5 + "%",
        "city": external_record.city,
        "state": external_record.state,
        "SRVC_ADDR1_LINE": (
            external_record.street_number + " " + external_record.street_name
        ),
        "BLR_ADDR1_LINE": (
            external_record.street_number + " " + external_record.street_name
        ),
    }
    return query_with_params(query, params)


def search_with_email(external_record: GeneralRequest) -> list[OracleDESRecord]:
    query = """
            SELECT
            ACCT_NUM, ACCT_NAME, ACCT_TYPE_CD,
            BLR_ADDR1_LINE,
            BLR_ADDR2_LINE, CITY_NM_BLR, STATE_NM_BLR, SRC_SYS_CD,
            PSTL_CD_TXT_BLR,
            EMAIL_ADDR, SPC_DIV_ID,
            'No uCan' as UCAN,
            ACCT_HOME_PHONE AS PRIMARY_NUMBER,
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
            WHERE REPLACE(upper(EMAIL_ADDR), ' ', '' ) = REPLACE(upper(:email_address), ' ', '' )
            """
    # Parameter values
    params = {"email_address": external_record.email_address}
    return query_with_params(query, params)


def search_with_zip_name(external_record: GeneralRequest) -> list[OracleDESRecord]:
    query = """
            SELECT
            ACCT_NUM, ACCT_NAME, ACCT_TYPE_CD,
            BLR_ADDR1_LINE,
            BLR_ADDR2_LINE, CITY_NM_BLR, STATE_NM_BLR, SRC_SYS_CD,
            PSTL_CD_TXT_BLR,
            EMAIL_ADDR, SPC_DIV_ID,
            'No uCan' as UCAN,
            ACCT_HOME_PHONE AS PRIMARY_NUMBER,
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
            WHERE REPLACE(upper(ACCT_NAME), ' ', '' ) = REPLACE(UPPER(:name), ' ', '' )
            AND PSTL_CD_TXT like UPPER(:zip)
            """
    # Parameter values
    params = {
        "name": external_record.last_name + "," + external_record.first_name,
        "zip": external_record.zipcode5 + "%",
    }

    return query_with_params(query, params)
