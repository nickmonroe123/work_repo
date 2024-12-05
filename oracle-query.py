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
