Here is the struct code. Can you help me prove that the test_query_with_params_success receives the correct final output from query_with_params being a OracleDESRecord?

from typing import TypeVar

import msgspec
from identifiers.structs import Address, FullIdentifier, Name, PhoneNumber


class IdentifiedAccount(FullIdentifier):
    match_score: float = 0.0
    account_type: str = ""
    status: str = ""
    source: str = ""
    ucan: str = ""
    billing_account_number: str = ""
    spectrum_core_account: str = ""
    spectrum_core_division: str = ""


InternalRequestLike = TypeVar(
    'InternalRequestLike', bound='OracleDESRecord | InternalRecord'
)


class ToIdentifiedAccountMixin:
    """Provide a function to convert to an identified account."""

    def to_identified_account(self: InternalRequestLike) -> IdentifiedAccount:
        return IdentifiedAccount(
            name=Name(
                first_name=self.first_name,
                last_name=self.last_name,
            ),
            phone_number=PhoneNumber(
                area_code=self.phone_number[:3] if self.phone_number else '',
                exchange=self.phone_number[3:6] if len(self.phone_number) >= 6 else '',
                line_number=self.phone_number[6:] if len(self.phone_number) > 6 else '',
                extension='',
                type_code='',
            ),
            address=Address(
                city=self.city,
                state=self.state,
                line1=self._address_line_1,
                line2=self._address_line_2,
                postal_code=self.zipcode5,
            ),
            email=self.email_address,
            account_type=self.account_description,
            status=self.account_status,
            source=self.source,
            ucan=self.ucan,
            spectrum_core_account=self.account_number,
            spectrum_core_division=self.division_id,
        )


class GeneralRequest(msgspec.Struct):
    country_code: str = msgspec.field(name="countryCode", default="")
    phone_number: str = msgspec.field(name="primaryPhone", default="")
    first_name: str = msgspec.field(name="firstName", default="")
    last_name: str = msgspec.field(name="lastName", default="")
    zipcode5: str = msgspec.field(name="zipCode5", default="")
    email_address: str = msgspec.field(name="emailAddress", default="")
    street_number: str = msgspec.field(name="streetNumber", default="")
    street_name: str = msgspec.field(name="streetName", default="")
    city: str = msgspec.field(name="city", default="")
    state: str = msgspec.field(name="state", default="")
    apartment: str = msgspec.field(name="line2", default="")

    @classmethod
    def from_full_identifier(cls, full_id: FullIdentifier):
        return cls(
            phone_number=full_id.phone_number.ten_digits_only,
            first_name=full_id.name.first_name,
            last_name=full_id.name.last_name,
            zipcode5=full_id.address.simplified_postal_code,
            email_address=full_id.email,
            street_number=full_id.address.street_number,
            street_name=full_id.address.street_name,
            city=full_id.address.city,
            state=full_id.address.state,
            apartment=full_id.address.line2,
        )


class Description(msgspec.Struct):
    description: str = ""


class InternalRecord(ToIdentifiedAccountMixin, GeneralRequest):
    ucan: str = msgspec.field(name="uCAN", default="")
    division_id: str = msgspec.field(name="divisionID", default="")
    account_status: str = msgspec.field(name="accountStatus", default="")
    secondary_number: str = msgspec.field(name="secondaryPhone", default="")
    account_number: str = msgspec.field(name="accountNumber", default="")
    account_description: str = ""
    source: str = msgspec.field(name="sourceMSO", default="")
    full_address: str = ""
    full_address_no_apt: str = ""
    _account_type: Description = msgspec.field(name="accountType", default=Description)
    _address_line_1: str = msgspec.field(name="addressLine1", default="")
    _address_line_2: str = msgspec.field(name="addressLine2", default="")

    def __post_init__(self):
        try:
            self.street_number, self.street_name = (
                self._address_line_1.split(' ')[0],
                self._address_line_1,
            )
        except:
            self.street_number, self.street_name = "", ""
        self.account_description = self._account_type.description
        if self._address_line_2 == "":
            self.full_address = self.street_name + " " + self.city + " " + self.state
        else:
            self.full_address = (
                self.street_name
                + " "
                + self._address_line_2
                + " "
                + self.city
                + " "
                + self.state
            )
            self.full_address_no_apt = (
                self.street_name + " " + self.city + " " + self.state
            )


class OracleDESRecord(ToIdentifiedAccountMixin, msgspec.Struct):
    account_number: str = msgspec.field(name="ACCT_NUM", default="")
    phone_number: str = msgspec.field(name="PRIMARY_NUMBER", default="")
    secondary_number: str = msgspec.field(name="secondaryPhone", default="")
    first_name: str = msgspec.field(name="ACCT_NAME", default="")
    last_name: str = ""
    zipcode5: str = msgspec.field(name="PSTL_CD_TXT_BLR", default="")
    email_address: str = msgspec.field(name="EMAIL_ADDR", default="")
    street_number: str = ""
    street_name: str = ""
    city: str = msgspec.field(name="CITY_NM_BLR", default="")
    state: str = msgspec.field(name="STATE_NM_BLR", default="")
    ucan: str = msgspec.field(name="UCAN", default="")
    division_id: str = msgspec.field(name="SPC_DIV_ID", default="")
    account_status: str = msgspec.field(name="ACCOUNTSTATUS", default="")
    account_description: str = msgspec.field(name="ACCT_TYPE_CD", default="")
    source: str = msgspec.field(name="SRC_SYS_CD", default="")
    full_address: str = ""
    full_address_no_apt: str = ""
    _address_line_1: str = msgspec.field(name="BLR_ADDR1_LINE", default="")
    _address_line_2: str = msgspec.field(name="BLR_ADDR2_LINE", default="")

    def __post_init__(self):
        try:
            self.street_number, self.street_name = (
                self._address_line_1.split(' ')[0],
                self._address_line_1,
            )
        except:
            self.street_number, self.street_name = "", ""
        try:
            self.first_name, self.last_name = (
                self.first_name.split(',')[1],
                self.first_name.split(',')[0],
            )
        except:
            self.first_name, self.last_name = "", ""
        if self._address_line_2 == "":
            self.full_address = self.street_name + " " + self.city + " " + self.state
        else:
            self.full_address = (
                self.street_name
                + " "
                + self._address_line_2
                + " "
                + self.city
                + " "
                + self.state
            )
            self.full_address_no_apt = (
                self.street_name + " " + self.city + " " + self.state
            )
