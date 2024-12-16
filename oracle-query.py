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
