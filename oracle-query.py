import re
import requests
import json
from django.views import View
from fuzzywuzzy import fuzz
from nameparser import HumanName
from typing import Tuple
import os
import msgspec

import logging
# Configure the logging
logging.basicConfig(filename='app.log', level=logging.INFO)
# Create a logger
logger = logging.getLogger(__name__)


# Import needed things from other files
from structs import *
import models as oracle_functions


class AccountProcessView(View):
    """ Valuable Links to Overall Process
    Account Identification Process: https://chalk.charter.com/display/ITDMIG/Account+Identification+and+Hydration
    getSPCAccountv1x1 shown in process above: https://chalk.charter.com/display/EWS/getSpcAccountDivision+V+1.1#
    findAccountx1x0 shown in process above: https://chalk.charter.com/display/EWS/getSpcAccountDivision+V+1.1#
    """
    if os.getenv('ENVIRONMENT') == 'prod':
        system_id = "ComplianceService"
        url = "https://spectrumcore.charter.com/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1"
        url_billing = "https://spectrumcore.charter.com/spectrum-core/services/account/ept/findAccountV1x0"
    elif os.getenv('ENVIRONMENT') == 'uat':
        system_id = "ComplianceService"
        url = "https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1"
        url_billing = "https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept/findAccountV1x0"
    # Temp set the local instance as being the uat as well
    else:
        system_id = "ComplianceService"
        url = "https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1"
        url_billing = "https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept/findAccountV1x0"

    # This list encompasses the first 4 api calls to getSpcAccountDivisionV1x1
    core_services_list = []

    # This list encompasses the queries against the oracle des database
    oracle_des_list = []

    # External vs Internal Record
    ext_request = GeneralRequest()
    int_record = InternalRecord()

    # For nicknames and such:
    name_dict = json.load(open("name_comp.txt"))

    # Keep Track of the Fuzzy Amount and Match Count
    match_count = 0
    fuzzy_amount = 0

    # Bad phone number list
    bad_numbers = ["0000000000", "1111111111", "2222222222", "3333333333", "4444444444", "5555555555",
                   "6666666666", "7777777777", "8888888888", "9999999999", ""]

    ###########################################################################################################
    # Here is the process for parsing out the request information/discovered information
    def ext_request_init(self, json_dt: dict):
        self.ext_request.country_code, self.ext_request.phone_number = self.phone_parse(json_dt)
        self.ext_request.first_name, self.ext_request.last_name, self.ext_request.zipcode5 = self.zip_name_parse(json_dt)
        self.ext_request.email_address = self.email_parse(json_dt)
        self.ext_request.street_number, self.ext_request.street_name, self.ext_request.city, self.ext_request.state = self.address_parse(json_dt)


    def int_record_init(self, json_dt: dict):
        self.int_record = msgspec.json.decode(json.dumps(json_dt).encode('utf-8'), type=InternalRecord)


    def int_record_init_oc(self, json_dt: dict):
        self.int_record = msgspec.json.decode(json.dumps(json_dt).encode('utf-8'), type=OracleDESRecord)


    # This first function will be the retrieval of accounts that have a phone # number match
    def phone_parse(self, json_dt: dict) -> Tuple[str, str]:
        try:
            num_to_search = str(json_dt['areaCode']) + str(json_dt['exchange']) + str(json_dt['lineNumber'])

            # Error is raised if the regular expression fails (remove all non-digits)
            try:
                digits = re.sub(r'\D', '', num_to_search)
            except re.error as e:
                print(f"Invalid pattern: {e}")
                return '', ''

            # split country code and phone number (should already be split but double-checking)
            if len(digits) > 10:
                country_cd = digits[:-10]
                phone_number = digits[-10:]
            else:
                country_cd = ''
                phone_number = digits

            return country_cd, phone_number
        except (KeyError, TypeError) as e:
            print(f"Error in parsing phone number: {e}")
            return '', ''


    def zip_name_parse(self, json_data: dict) -> Tuple[str, str, str]:
        try:
            zipcode = json_data['postalCode']
            first_name = json_data['givenName']
            last_name = json_data['familyName']
            return first_name, last_name, zipcode
        except (KeyError, TypeError) as e:
            print(f"Error in parsing name and zip: {e}")
            return '', '', ''


    def email_parse(self, json_data: dict) -> str:
        try:
            email_address = json_data['emailAddress']
            return email_address
        except (KeyError, TypeError) as e:
            print(f"Error in parsing email: {e}")
            return ''


    def address_parse(self, json_data: dict) -> Tuple[str, str, str, str, str]:
        try:
            address1 = json_data['line1']
            city = json_data['city']
            state = json_data['territoryCode']
            # Split up street name and street number
            temp = address1.split(' ')
            streetNumber = temp[0]
            streetName = ""

            for i in range(1, len(temp)):
                streetName += temp[i]
                if i < len(temp) - 1:
                    streetName += " "
            return streetNumber, streetName, city, state
        except (KeyError, TypeError) as e:
            print(f"Error in parsing address: {e}")
            return '', '', '', '', ''



    def post(self, json_dt: dict) -> list:
        try:
            # Log the request to start so we have a record of its existence
            logger.info('This is the start of a new account identification process.')
            logger.info('Requestor info:')
            logger.info(json_dt)

            # Fill out account_info dictionary, this will parse the data for all of the needed columns
            self.ext_request_init(json_dt)

            return self.core_services_list
        except Exception as e:
            print(f"Error in the API process: {e}")


input_dataset1 = {
        "familyName": "ITPMJULI",
        "givenName": "PCSRESI",
        "city": "WOODLAND HILLS",
        "line1": "6201 JACKIE AVE",
        "postalCode": "91367",
        "territoryCode": "CA",
        "line2": "",
        "areaCode": "637",
        "exchange": "123",
        "lineNumber": "4997",
      "emailAddress": "mobilebuyflow6@charter.com"
        }

view = AccountProcessView()
result = view.post(input_dataset1)

print("Number of records found: " + str(len(result)))
for record in result:
    print(record)
