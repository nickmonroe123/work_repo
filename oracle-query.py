class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        search_input = msgspec.json.decode(request.data, type=FullIdentifier)
        results = identify_accounts(search_input=search_input)
        return Response(data=results)


import re

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

    @property
    def ten_digits_only(self) -> str:
        starting_number = f"{self.area_code}{self.exchange}{self.line_number}"
        digits_only = re.sub(r"\D", "", starting_number)
        return digits_only[-10:]


class Address(msgspec.Struct):
    city: str
    state: str
    line1: str
    postal_code: str
    line2: str = ""
    country_code: str = ""

    def _street_name_and_number(self) -> tuple[str, str]:
        street_matches = re.search(r'^\s*(\d[^\s]*)?\s*(.*)?', self.line1)
        street_name = (street_matches.group(2) or '').strip()
        street_number = (street_matches.group(1) or '').strip()
        return street_name, street_number

    @property
    def street_name(self):
        return self._street_name_and_number()[0]

    @property
    def street_number(self):
        return self._street_name_and_number()[1]

    @property
    def simplified_postal_code(self):
        """First portion of a dash-separated postal code."""
        return self.postal_code.split("-")[0]


class FullIdentifier(msgspec.Struct):
    """Combine name, address, phone number, and email."""

    name: Name
    phone_number: PhoneNumber
    address: Address
    email: str
