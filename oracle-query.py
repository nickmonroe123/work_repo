import json
import logging
import re
from typing import Tuple
from fuzzywuzzy import fuzz
from operator import itemgetter
import models as oracle_functions


import msgspec
import requests
import constants
from structs import (
    FullIdentifier,
    GeneralRequest,
    IdentifiedAccount,
    InternalRecord,
    OracleDESRecord,
)
from django.conf import settings
from structs_full import Address, Name, PhoneNumber

logger = logging.getLogger(__name__)

request_data = {
        "name": {
            "last_name": "DDTDP",
            "first_name": "ISEPPCSI",
            "middle_name": "",
            "prefix": "",
            "suffix": ""
        },
        "address": {
            "city": "CANOGA PARK",
            "line1": "7330 ETON AVENUE",
            "postal_code": "91303",
            "state": "CA",
            "line2": "",
            "country_code": ""
        },
        "phone_number": {
            "area_code": "980",
            "exchange": "914",
            "line_number": "9590",
            "country_code": "",
            "extension": "",
            "type_code": "Home"
        },
        "email": "mobilebuyflow6@charter.com"
}
# request_data = {
#         "name": {
#             "last_name": "ITPMJULI",
#             "first_name": "PCSRESI",
#             "middle_name": "",
#             "prefix": "",
#             "suffix": ""
#         },
#         "address": {
#             "city": "ROSAMOND",
#             "line1": "1041 Hastings Ave",
#             "postal_code": "93560",
#             "state": "CA",
#             "line2": "",
#             "country_code": ""
#         },
#         "phone_number": {
#             "area_code": "637",
#             "exchange": "123",
#             "line_number": "4997",
#             "country_code": "",
#             "extension": "",
#             "type_code": "Home"
#         },
#         "email": "mobilebuyflow6@charter.com"
# }



class AccountProcess:
    """Valuable Links to Overall Process
    Account Identification Process: https://chalk.charter.com/display/ITDMIG/Account+Identification+and+Hydration
    getSPCAccountv1x1 shown in process above: https://chalk.charter.com/display/EWS/getSpcAccountDivision+V+1.1#
    findAccountx1x0 shown in process above: https://chalk.charter.com/display/EWS/findAccount+V+1.0
    """

    # Spectrum Core
    SPECTRUM_CORE_API = "https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept"
    SPECTRUM_CORE_ACCOUNT = f"{SPECTRUM_CORE_API}/getSpcAccountDivisionV1x1"
    SPECTRUM_CORE_BILLING = f"{SPECTRUM_CORE_API}/findAccountV1x0"
    SPECTRUM_CORE_SYSTEM_ID = "ComplianceService"

    system_id = SPECTRUM_CORE_SYSTEM_ID
    url_accounts = SPECTRUM_CORE_ACCOUNT
    url_billing = SPECTRUM_CORE_BILLING

    # This list encompasses the f irst 5 api calls to getSpcAccountDivisionV1x1 (4) and findAccountV1x0 (1)
    core_services_list = []

    # This list encompasses the queries against the oracle des database
    oracle_des_list = []

    # External vs Internal Record
    ext_request = GeneralRequest()
    int_record = InternalRecord()

    # For nicknames and such:
    name_dict = constants.NICKNAMES

    # For street acronyms
    street_dict = constants.STREET_ACRO

    # Keep Track of the Fuzzy Amount
    fuzzy_amount = 0

    # Bad phone number list
    bad_numbers = constants.BAD_NUMBERS

    ###########################################################################################################
    # Here is the process for parsing out the request information/discovered information
    def ext_request_init(self, search_input: FullIdentifier):

        self.ext_request.phone_number = self.phone_parse(search_input.phone_number)
        (
            self.ext_request.first_name,
            self.ext_request.last_name,
            self.ext_request.zipcode5,
        ) = self.zip_name_parse(search_input)
        self.ext_request.email_address = search_input.email
        (
            self.ext_request.street_number,
            self.ext_request.street_name,
            self.ext_request.city,
            self.ext_request.state,
            self.ext_request.apartment,
        ) = self.address_parse(search_input.address)

    def int_record_init(self, json_dt: dict, msgspec_type: msgspec.Struct):
        """Parse the data into an internal record type."""
        self.int_record = msgspec.json.decode(
            json.dumps(json_dt).encode('utf-8'), type=msgspec_type
        )

    # This first function will be the retrieval of accounts that have a phone # number match
    def phone_parse(self, phone_number: PhoneNumber) -> str:
        num_to_search = (
            f"{phone_number.area_code}{phone_number.exchange}{phone_number.line_number}"
        )

        # Error is raised if the regular expression fails (remove all non-digits)
        try:
            digits = re.sub(r'\D', '', num_to_search)
        except re.error as e:
            logger.info(f"Invalid pattern: {e}")
            return ''

        return digits[-10:]

    def zip_name_parse(self, search_input: FullIdentifier) -> Tuple[str, str, str]:
        zipcode = search_input.address.postal_code
        # Deal with cases of 62002-2131 vs just 62002
        zipcode = zipcode.split('-')[0]
        first_name = search_input.name.first_name
        last_name = search_input.name.last_name
        return first_name, last_name, zipcode

    def address_parse(self, address: Address) -> Tuple[str, str, str, str, str]:
        # Pull out the starting element with digits as street number and anything else as street name
        street_matches = re.search('^\s*(\d[^\s]*)?\s*(.*)?', address.line1)
        if street_matches:
            street_name = (street_matches.group(2) or '').strip()
            street_number = (street_matches.group(1) or '').strip()
        else:
            street_name = ''
            street_number = ''
        city = address.city
        state = address.state
        apartment = address.line2
        return street_number, street_name, city, state, apartment

    ###################################################################################################
    # Here is the process of the 4 api calls that call spectrum core services

    def _parse_spectrum_core_account_api(
            self, payload: dict, function_name: str, post_processing_function=None
    ):
        """Helper function for parsing information from spectrum core services
        account API."""
        # try:
        # Make the post request call out to spectrum core services
        # TODO: Need to add the certificate authentication here
        print("ASDOIASDOIAJSDOINASD")
        print(payload)
        print("ASDOIASDOIAJSDOINASD")
        response = requests.request("POST", self.url_accounts, json=payload)
        # Will return an HTTPError object if an error has occurred during the process
        response.raise_for_status()
        # For now if it fails return empty list. Its possible there are just no records here
        account_division_response = response.json().get(
            'getSpcAccountDivisionResponse'
        )
        if account_division_response is None:
            logger.error(
                f"The format of the JSON has been changed during {function_name}! New format: {response.json()}"
            )
            raise ValueError('Format of Spectrum Core Account API has changed')
        core_services_list_to_add = account_division_response.get(
            'spcAccountDivisionList', []
        )
        if post_processing_function is not None:
            core_services_list_to_add = post_processing_function(
                core_services_list_to_add
            )
        self.core_services_list += core_services_list_to_add
        return core_services_list_to_add
        # except requests.exceptions.RequestException as e:
        #     logger.error(f"Error in spectrum core api search: {function_name}")
        #     raise e

    def phone_search(self):
        """/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1
        Type of Possible Requests: Post
        Determines the divisionID, unique account ID and other account information
        """
        # Core services requires phone number to be 10 digits to search.
        if (
                len(self.ext_request.phone_number) != 10
                or self.ext_request.phone_number in self.bad_numbers
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
        self.core_services_list += self._parse_spectrum_core_account_api(
            payload, function_name='phone_search'
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
        self.core_services_list += self._parse_spectrum_core_account_api(
            payload, function_name='name_zip_search'
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
        self.core_services_list += self._parse_spectrum_core_account_api(
            payload, function_name='email_search'
        )

    def clean_address_search(self, json_list: dict) -> list:
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
            len(self.ext_request.state) != 2 or len(self.ext_request.zipcode5) != 5:
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
        self.core_services_list += self._parse_spectrum_core_account_api(
            payload,
            function_name='email_search',
            post_processing_function=lambda x: self.clean_address_search(x),
        )

    #################################################################################################
    # Here is the 1 api that we call core spectrum for to get info based on billing records
    # Get the UCAN and email address for any billing records that are found
    def billing_info_specific(self, dataset: list) -> list:
        changing_dataset = dataset
        for record in changing_dataset:
            # If bad data just leave
            if record['accountNumber'] == "":
                logger.warning(f"Account number is missing, cannot continue!")
                continue

            # Set up the api call itself, only using phone number here
            payload = {
                "getSpcAccountDivisionRequest": {
                    "systemID": self.system_id,
                    "accountNumber": record['accountNumber'],
                }
            }
            account_division_list = self._parse_spectrum_core_account_api(
                payload,
                function_name='phone_search',
            )
            if not account_division_list:
                logger.warning(
                    f"We have found no matching records for this  account number: {record['accountNumber']}"
                )
                continue
            # populate the specific values
            account_division_response = account_division_list[0]
            record['uCAN'] = account_division_response.get('uCAN', '')
            record['emailAddress'] = account_division_response.get('emailAddress', '')
        return changing_dataset

    # This fifth function will be the retrieval of accounts that have an billing address match
    def billing_search(self):
        try:
            # If bad data just leave
            if (self.ext_request.last_name == "" or self.ext_request.first_name == "" or
                    len(self.ext_request.state) != 2 or len(self.ext_request.zipcode5) != 5):
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
            # TODO: Need to add the certificate authentication here
            response = requests.request("POST", self.url_billing, json=payload)
            # Will return an HTTPError object if an error has occurred during the process
            response.raise_for_status()
            # For now if it fails return empty list. Its possible there are just no records here
            account_division_response = response.json().get('findAccountResponse')
            if account_division_response is None:
                logger.error(
                    f"The format of the JSON has been changed during phone_search! New format: {response.json()}"
                )
                raise ValueError('Format of Spectrum Core Account API has changed')
            self.core_services_list += self.billing_info_specific(
                account_division_response.get('accountList', [])
            )
            return
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in billing api search: {e}")
            raise e

    #################################################################################################
    # Here is the process that we use to get oracle information (references models.py)
    def oracle_des_process(self):
        """One thing we want to setup is to only call the specific queries IF
        the value is populated in the json!"""
        try:
            try:
                # Only do this first query if the phone number is valid!
                if (
                        len(self.ext_request.phone_number) == 10
                        and self.ext_request.phone_number not in self.bad_numbers
                ):
                    phone_list = oracle_functions.search_with_phone(self.ext_request)
                else:
                    phone_list = []
            except Exception as e:
                logger.info(f"Error in oracle_des_process during phone search!: {e}")
                phone_list = []

            try:
                if (
                        self.ext_request.street_name != ""
                        and self.ext_request.street_number != ""
                ):
                    address_list = oracle_functions.search_with_address(
                        self.ext_request
                    )
                else:
                    address_list = []
            except Exception as e:
                logger.info(f"Error in oracle_des_process during address search!: {e}")
                address_list = []

            try:
                if self.ext_request.email_address != "":
                    email_list = oracle_functions.search_with_email(self.ext_request)
                else:
                    email_list = []
            except Exception as e:
                logger.info(f"Error in oracle_des_process during email search!: {e}")
                email_list = []

            try:
                if self.ext_request.first_name != "" or self.ext_request.zipcode5 != "":
                    name_zip_list = oracle_functions.search_with_zip_name(
                        self.ext_request
                    )
                else:
                    name_zip_list = []
            except Exception as e:
                logger.info(f"Error in oracle_des_process during name/zip search!: {e}")
                name_zip_list = []

            # Concat all the lists together so we can work on removing duplicates based on match count
            self.oracle_des_list = (
                    phone_list + email_list + address_list + name_zip_list
            )
            return
        except Exception as e:
            # TODO: This should throw out a larger error!
            logger.info(f"Error in oracle_des_process when making connection!: {e}")
            return

    ###################################################################################
    # Start of Fuzzy searching
    def normalize_phone_number(self, phone: str) -> str:
        """Remove all non-digits and take the first 10 numbers."""
        phone_without_backslashes = phone.replace('//', '')
        digits = re.sub(r'\D', '', phone_without_backslashes)
        return digits[-10:]

    def are_names_equal(self, name1: str, name2: str) -> bool:
        name1 = name1.strip()
        name2 = name2.strip()
        return self.name_dict.get(name1.upper()) == name2.upper()

    def normalize_address(self, address: str) -> str:
        address = address.upper()
        for abbr, full in self.street_dict.items():
            pattern = r'\b{}\b'.format(re.escape(abbr))
            if re.search(pattern, address):
                return full
        return address

    def check_match(self, record: dict, source: str) -> dict:
        # Init the record and set both the fuzzy amount and match count to 0
        if source == "sc":
            self.int_record_init(record, InternalRecord)
        elif source == "oracle":
            self.int_record_init(record, OracleDESRecord)

        self.fuzzy_amount = 0

        # we want to normalize the three? phone numbers to clean them up
        self.ext_request.phone_number = self.normalize_phone_number(
            self.ext_request.phone_number
        )

        # Only run the process if external AND 1 of the 2 internal phone numbers are valid
        if self.ext_request.phone_number not in self.bad_numbers and (
                self.int_record.phone_number not in self.bad_numbers
                or self.int_record.secondary_number not in self.bad_numbers
        ):
            phone_accuracy_primary_number = fuzz.WRatio(
                self.ext_request.phone_number, self.int_record.phone_number
            )
            phone_accuracy_secondary_number = fuzz.WRatio(
                self.ext_request.phone_number, self.int_record.secondary_number
            )
            self.fuzzy_amount += max(
                phone_accuracy_primary_number, phone_accuracy_secondary_number
            )

        # Now we want to calculate the fuzzy score for email address
        self.fuzzy_amount += fuzz.WRatio(
            self.ext_request.email_address.lower().replace(' ', ''),
            self.int_record.email_address.lower().replace(' ', ''),
        )

        # Now we want to check on the name
        ext_first = self.ext_request.first_name.lower().replace(' ', '')
        ext_last = self.ext_request.last_name.lower().replace(' ', '')
        int_first = self.int_record.first_name.lower().replace(' ', '')
        int_last = self.int_record.last_name.lower().replace(' ', '')
        # Get the fuzzy score for a couple scenarios
        # Scenario 1: name is given correctly
        correct_accuracy = fuzz.WRatio((ext_first + ext_last), (int_first + int_last))
        # Scenario 2: name is given reversed (i.e. john doe given as doe john)
        incorrect_accuracy = fuzz.WRatio((ext_last + ext_first), (int_first + int_last))
        # Scenario 3: check if there is a common nickname ordered correctly
        if self.name_dict.get(ext_first.upper()) == int_first.upper():
            ext_first = int_first
        elif self.name_dict.get(int_first.upper()) == ext_first.upper():
            ext_first = int_first
        nickname_accuracy = fuzz.WRatio((ext_first + ext_last), (int_first + int_last))

        self.fuzzy_amount += max(
            correct_accuracy, incorrect_accuracy, nickname_accuracy
        )

        #  Now we want to deal with the address (Street #, State, Zip Code)
        # Split up street name and street number
        ext_full = (
                self.ext_request.street_number
                + " "
                + self.ext_request.street_name
                + " "
                + self.ext_request.city
                + " "
                + self.ext_request.state
        )

        # Scenario 1: external address and internal address with apt match
        apt_accuracy = fuzz.WRatio(
            self.int_record.full_address.lower().replace(' ', ''),
            ext_full.lower().replace(' ', ''),
        )
        # Scenario 2: external address and internal address no apt match
        no_apt_accuracy = fuzz.WRatio(
            self.int_record.full_address_no_apt.lower().replace(' ', ''),
            ext_full.lower().replace(' ', ''),
        )

        # Try normalizing to account for street abbreviations
        normalized_int_record = (
            ' '.join(
                [
                    self.normalize_address(word)
                    for word in self.int_record.full_address.split()
                ]
            )
            .lower()
            .replace(' ', '')
        )
        normalized_int_record_no_apt = (
            ' '.join(
                [
                    self.normalize_address(word)
                    for word in self.int_record.full_address_no_apt.split()
                ]
            )
            .lower()
            .replace(' ', '')
        )
        normalized_ext_record = (
            ' '.join([self.normalize_address(word) for word in ext_full.split()])
            .lower()
            .replace(' ', '')
        )

        # Scenario 3: normalized external address and internal address with apt match
        apt_accuracy_norm = fuzz.WRatio(normalized_int_record, normalized_ext_record)
        # Scenario 4: normalized external address and internal address no apt match
        no_apt_accuracy_norm = fuzz.WRatio(
            normalized_int_record_no_apt, normalized_ext_record
        )

        self.fuzzy_amount += max(
            apt_accuracy, no_apt_accuracy, apt_accuracy_norm, no_apt_accuracy_norm
        )

        record_to_return = {
            "match_score": self.fuzzy_amount,
            "billing_account_number": self.int_record.account_number,
            "complete_record": self.int_record,
        }

        return record_to_return

    def confirmed_matches(self, clean_recordset: list, source: str) -> list:
        """Perform fuzzy matching on the provided list."""
        final_dataset = []
        for record in clean_recordset:
            final_dataset.append(self.check_match(record, source))
        return final_dataset

    #################################################################################################
    # Needs to be done AFTER account fuzzy matching has occured with how we remove duplicates
    # Sorting on fuzzy score and then removing based on account number
    def clean_core_services_list(self):
        try:
            sorted_data = sorted(
                self.core_services_list, key=itemgetter('match_score'), reverse=True
            )
            # Remove duplicates based on the fourth item
            unique_data = []
            seen = set()
            for item in sorted_data:
                acct_num = item.get('billing_account_number', '')
                if acct_num not in seen and acct_num != '':
                    unique_data.append(item)
                    seen.add(acct_num)

            self.core_services_list = unique_data
            return
        except Exception as e:
            print(
                f"Error in cleaning out the duplicate records - clean_find_account_list: {e}"
            )
            return

    def create_output_list(self) -> list[IdentifiedAccount]:
        output_list = []
        if len(self.core_services_list) == 0:
            return output_list
        try:
            # if no records, no need to waste time
            for record in self.core_services_list:
                # Helper function to safely get nested attributes
                def safe_get(obj, attr, default=''):
                    try:
                        # Split the attribute path
                        parts = attr.split('.')
                        for part in parts:
                            obj = (
                                getattr(obj, part) if hasattr(obj, part) else obj[part]
                            )
                        return obj
                    except (AttributeError, KeyError, TypeError):
                        return default

                # Parse phone number
                internal_record = safe_get(record, 'complete_record', '')
                description = safe_get(internal_record, '_account_type', '')
                phone_number = safe_get(internal_record, 'phone_number', '')
                json_dt = {
                    "match_score": record.get('match_score', 0),
                    "account_type": safe_get(description, 'description', ''),
                    "status": safe_get(internal_record, 'account_status', ''),
                    "source": safe_get(internal_record, 'source', ''),
                    "ucan": safe_get(internal_record, 'ucan', ''),
                    "billing_account_number": record.get('billing_account_number', ''),
                    "spectrum_core_account": safe_get(internal_record, 'account_number', ''),
                    "spectrum_core_division": safe_get(internal_record, 'division_id', ''),
                    "name": {
                        "first_name": safe_get(internal_record, 'first_name', ''),
                        "last_name": safe_get(internal_record, 'last_name', ''),
                        "middle_name": "",  # No middle name in the original record
                        "suffix": "",  # No suffix in the original record
                        "prefix": "",  # No prefix in the original record
                    },
                    "phone_number": {
                        "country_code": safe_get(internal_record, 'country_code', ''),
                        "area_code": phone_number[:3] if phone_number else '',
                        "exchange": phone_number[3:6] if len(phone_number) >= 6 else '',
                        "line_number": (
                            phone_number[6:] if len(phone_number) >= 6 else ''
                        ),
                        "extension": "",  # No extension in the original record
                        "type_code": "",  # No type code in the original record
                    },
                    "address": {
                        "city": safe_get(internal_record, 'city', ''),
                        "state": safe_get(internal_record, 'state', ''),
                        "line1": safe_get(internal_record, '_address_line_1', ''),
                        "postal_code": safe_get(internal_record, 'zipcode5', ''),
                        "line2": safe_get(internal_record, '_address_line_2', ''),
                        "country_code": safe_get(internal_record, 'country_code', ''),
                    },
                    "email": safe_get(internal_record, 'email_address', ''),
                }

                output_list.append(
                    msgspec.json.decode(
                        json.dumps(json_dt).encode('utf-8'), type=IdentifiedAccount
                    )
                )

            return output_list
        except Exception as e:
            logger.warning(f"Error in creating the output list: {e}")
        return []

    def full_search(self, search_input: FullIdentifier) -> list[IdentifiedAccount]:
        try:
            # Log the request to start so we have a record of its existence
            logger.info('This is the start of a new account identification process.')
            logger.info('Requestor info:')
            logger.info(search_input)

            # Fill out account_info dictionary, this will parse the data for all of the needed columns
            self.ext_request_init(search_input)

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
            self.core_services_list = self.confirmed_matches(
                self.core_services_list, "sc"
            )

            # Run through the oracle des process
            self.oracle_des_process()
            # Call fuzzy match for the oracle des process
            self.core_services_list += self.confirmed_matches(
                self.oracle_des_list, "oracle"
            )

            # CLean the dataset to get distinct account numbers for the first 1 billing api call to core services
            self.clean_core_services_list()

            logger.info('This is the end of an account identification process.')
            logger.info('\n')
            return self.create_output_list()
            # return self.core_services_list
        except Exception as e:
            print(f"Error in the API process: {e}")


view = AccountProcess()
search_input = msgspec.json.decode(json.dumps(request_data).encode('utf-8'), type=FullIdentifier)
result = view.full_search(search_input=search_input)

print("Number of records found: " + str(len(result)))
for record in result:
    print(record)
    print("\n")


import msgspec
from structs_full import FullIdentifier


class IdentifiedAccount(FullIdentifier):
    match_score: float = 0.0
    account_type: str = ""
    status: str = ""
    source: str = ""
    ucan: str = ""
    billing_account_number: str = ""
    spectrum_core_account: str = ""
    spectrum_core_division: str = ""


class GeneralRequest(msgspec.Struct):
    country_code: str = msgspec.field(name="countryCode", default = "")
    phone_number: str = msgspec.field(name="primaryPhone", default = "")
    first_name: str = msgspec.field(name="firstName", default = "")
    last_name: str = msgspec.field(name="lastName", default = "")
    zipcode5: str = msgspec.field(name="zipCode5", default = "")
    email_address: str = msgspec.field(name="emailAddress", default = "")
    street_number: str = msgspec.field(name="streetNumber", default = "")
    street_name: str = msgspec.field(name="streetName", default = "")
    city: str = msgspec.field(name="city", default = "")
    state: str = msgspec.field(name="state", default = "")
    apartment: str = msgspec.field(name="line2", default = "")


class Description(msgspec.Struct):
    description: str = ""


class InternalRecord(GeneralRequest):
    ucan: str = msgspec.field(name="uCAN", default = "")
    division_id: str = msgspec.field(name="divisionID", default = "")
    account_status: str = msgspec.field(name="accountStatus", default = "")
    secondary_number: str = msgspec.field(name="secondaryPhone", default = "")
    account_number: str = msgspec.field(name="accountNumber", default = "")
    account_description: str = ""
    source: str = msgspec.field(name="sourceMSO", default = "")
    full_address: str = ""
    full_address_no_apt: str = ""
    _account_type: Description = msgspec.field(name="accountType", default = Description)
    _address_line_1: str = msgspec.field(name="addressLine1", default = "")
    _address_line_2: str = msgspec.field(name="addressLine2", default = "")

    def __post_init__(self):
        try:
            self.street_number, self.street_name = self._address_line_1.split(' ')[0], self._address_line_1
        except:
            self.street_number, self.street_name = "", ""
        self.account_description = self._account_type.description
        if self._address_line_2 == "":
            self.full_address = self.street_name + " " + self.city + " " + self.state
        else:
            self.full_address = self.street_name + " " + self._address_line_2 + " " + self.city + " " + self.state
            self.full_address_no_apt = self.street_name + " " + self.city + " " + self.state


class OracleDESRecord(msgspec.Struct):
    account_number: str = msgspec.field(name="ACCT_NUM", default = "")
    phone_number: str = msgspec.field(name="PRIMARY_NUMBER", default = "")
    secondary_number: str = msgspec.field(name="secondaryPhone", default = "")
    first_name: str = msgspec.field(name="ACCT_NAME", default = "")
    last_name: str = ""
    zipcode5: str = msgspec.field(name="PSTL_CD_TXT_BLR", default = "")
    email_address: str = msgspec.field(name="EMAIL_ADDR", default = "")
    street_number: str = ""
    street_name: str = ""
    city: str = msgspec.field(name="CITY_NM_BLR", default = "")
    state: str = msgspec.field(name="STATE_NM_BLR", default = "")
    ucan: str = msgspec.field(name="UCAN", default = "")
    division_id: str = msgspec.field(name="SPC_DIV_ID", default = "")
    account_status: str = msgspec.field(name="ACCOUNTSTATUS", default = "")
    account_description: str = msgspec.field(name="ACCT_TYPE_CD", default = "")
    source: str = msgspec.field(name="SRC_SYS_CD", default = "")
    full_address: str = ""
    full_address_no_apt: str = ""
    _address_line_1: str = msgspec.field(name="BLR_ADDR1_LINE", default = "")
    _address_line_2: str = msgspec.field(name="BLR_ADDR2_LINE", default = "")

    def __post_init__(self):
        try:
            self.street_number, self.street_name = self._address_line_1.split(' ')[0], self._address_line_1
        except:
            self.street_number, self.street_name = "", ""
        try:
            self.first_name, self.last_name = self.first_name.split(',')[1], self.first_name.split(',')[0]
        except:
            self.first_name, self.last_name = "", ""
        if self._address_line_2 == "":
            self.full_address = self.street_name + " " + self.city + " " + self.state
        else:
            self.full_address = self.street_name + " " + self._address_line_2 + " " + self.city + " " + self.state
            self.full_address_no_apt = self.street_name + " " + self.city + " " + self.state

import msgspec


class Name(msgspec.Struct):
    first_name: str
    last_name: str
    middle_name: str = ""
    suffix: str = ""
    prefix: str = ""


class PhoneNumber(msgspec.Struct):
    country_code: str = ""
    area_code: str = ""
    exchange: str = ""
    line_number: str = ""
    extension: str = ""
    type_code: str = ""


class Address(msgspec.Struct):
    city: str
    state: str
    line1: str
    postal_code: str
    line2: str = ""
    country_code: str = ""


class FullIdentifier(msgspec.Struct):
    """Combine name, address, phone number, and email."""

    name: Name
    phone_number: PhoneNumber
    address: Address
    email: str
