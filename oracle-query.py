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
