from datetime import datetime
import json
import re
from typing import List, Optional, Union
from pydantic import (
    BaseModel,
    PositiveInt,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
import pycountry

from xmltodict1 import parse_xml_to_json


def is_valid_currency_code(currency_code):
    # Regular expression pattern for ISO 4217 currency codes
    pattern = r"^[A-Z]{3}$"
    return bool(re.match(pattern, currency_code))


def is_iso8601(string):
    try:
        # Attempt to parse the string as an ISO 8601 formatted date
        datetime.fromisoformat(string)
        return True
    except ValueError:
        return False


def is_valid_iso_3166_alpha_2(code):
    try:
        pycountry.countries.lookup(code)
        return True
    except LookupError:
        return False


class Id(BaseModel):
    sequence: Optional[PositiveInt] = Field(alias="@sequence", default=None)
    source: Optional[str] = Field(alias="@source", default=None)


class Odometer(BaseModel):
    status: Optional[str] = Field(alias="@status", default=None)
    units: Optional[str] = Field(alias="@units", default=None)
    odometer: Optional[int] = Field(alias="#text", default=None)

    @field_validator("status")
    def validate_status(cls, value):
        if value not in (None, "unknown", "rolledover", "replaced", "original"):
            raise ValueError("Invalid Status input")
        return value

    @field_validator("units")
    def validate_units(cls, value):
        if value not in (None, "km", "mi"):
            raise ValueError("Invalid Units input")
        return value


class ColorCombination(BaseModel):
    interior_color: Optional[str] = None
    exterior_color: Optional[str] = None
    preference: Optional[int] = None

    @field_validator("preference")
    def validate_preference(cls, value):
        if value < 1:
            raise ValueError("Invalid Preference input")
        return value


class ImageTag(BaseModel):
    width: Optional[str] = Field(alias="@width", default=None)
    height: Optional[str] = Field(alias="@height", default=None)
    alt_text: Optional[str] = Field(alias="@alttext", default=None)
    image_tag: Optional[str] = Field(alias="#text", default=None)


class Price(BaseModel):
    type: Optional[str] = Field(alias="@type", default=None)
    currency: Optional[str] = Field(alias="@curreny", default=None)
    delta: Optional[str] = Field(alias="@delta", default=None)
    relative_to: Optional[str] = Field(alias="@relative_to", default=None)
    source: Optional[str] = Field(alias="@source", default=None)
    price: Optional[int] = Field(alias="@price", default=None)

    @field_validator("type")
    def validate_type(cls, value):
        if value not in (None, "quote", "offer", "msrp", "invoice", "call", "apraisal", "asking"):
            raise ValueError("Invalid Price Type input")
        return value

    @field_validator("currency")
    def validate_currency(cls, value):
        if is_valid_currency_code(value) == False:
            raise ValueError("Invalid Currency input")
        return value
    
    @field_validator("delta")
    def validate_delta(cls, value):
        if value not in (None, "absolute", "relative", "percentage"):
            raise ValueError("Invalid Price Delta input")
        return value
    
    @field_validator("relative_to")
    def validate_relativeto(cls, value):
        if value not in (None, "msrp", "invoice"):
            raise ValueError("Invalid Price Type input")
        return value


class Option(BaseModel):
    option_name: Optional[str] = None
    manufacture_code: Optional[str] = None
    stock: Optional[str] = None
    weighting: Optional[int] = None
    price: Optional[Price] = None

    @field_validator("weighting")
    def validate_weighting(cls, value):
        if value >= 100 or value <= -100:
            raise ValueError("Invalid Weighting input")
        return value


class Amount(BaseModel):
    type: Optional[str] = Field(alias="@type", default=None)
    limit: Optional[str] = Field(alias="@limit", default=None)
    currency: Optional[str] = Field(alias="@currency", default=None)
    amount: Optional[int] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value not in (None, "downpayment", "monthly", "total"):
            raise ValueError("Invalid Type input")
        return value

    @field_validator("limit")
    def validate_limit(cls, value):
        if value not in (None, "maximum", "minimum", "exact"):
            raise ValueError("Invalid Limit input")
        return value

    @field_validator("currency")
    def validate_currency(cls, value):
        if is_valid_currency_code(value) == False:
            raise ValueError("Invalid Currency input")
        return value


class Balance(BaseModel):
    type: Optional[str] = Field(alias="@type", default=None)
    currency: Optional[str] = Field(alias="@currency", default=None)
    balance: Optional[int] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value not in (None, "finance", "residual"):
            raise ValueError("Invalid Type input")
        return value

    @field_validator("currency")
    def validate_currency(cls, value):
        if is_valid_currency_code(value) == False:
            raise ValueError("Invalid Currency input")
        return value


class Finance(BaseModel):
    method: Optional[str] = None
    amount: Optional[Amount] = None
    balance: Optional[Balance] = None

    @field_validator("method")
    def validate_method(cls, value):
        if value not in (None, "cash", "finance", "lease"):
            raise ValueError("Invalid Status input")
        return value


class Vehicle(BaseModel):
    interest: Optional[str] = Field(alias="@interest", default=None)
    status: Optional[str] = Field(alias="@status", default=None)
    id: Optional[Id] = None
    year: str
    make: str
    model: str
    vin: Optional[str] = None
    stock: Optional[str] = None
    trim: Optional[str] = None
    doors: Optional[str] = None
    bodystyle: Optional[str] = None
    odometer: Optional[Odometer] = None
    condition: Optional[str] = None
    color_combination: Optional[Union[ColorCombination, List[ColorCombination]]] = None
    imagetag: Optional[ImageTag] = None
    price: Optional[Price] = None
    price_comments: Optional[str] = None
    option: Optional[Option] = None
    finance: Optional[Finance] = None
    comments: Optional[str] = None

    @model_validator(mode="after")
    def check_required_fields(cls, vehicle):
        required_fields = {"year", "make", "model"}  # Add all required field names here
        empty_required_fields = [
            field for field in required_fields if getattr(vehicle, field) is None
        ]
        if empty_required_fields:
            raise ValueError(
                f"The following required fields in Vehicle are missing: {', '.join(empty_required_fields)}"
            )
        return vehicle

    @field_validator("interest")
    def validate_interest(cls, value):
        if value not in (None, "buy", "lease", "sell", "trade-in", "test-drive"):
            raise ValueError("Invalid Interest input")
        return value

    @field_validator("status")
    def validate_status(cls, value):
        if value not in (None, "new", "used"):
            raise ValueError("Invalid Status input")
        return value

    @field_validator("condition")
    def validate_conditon(cls, value):
        if value not in (None, "excellent", "good", "fair", "poor", "unknown"):
            raise ValueError("Invalid Condition input")
        return value


class Name(BaseModel):
    part: Optional[str] = Field(alias="@part", default=None)
    type: Optional[str] = Field(alias="@type", default=None)
    name: Optional[str] = Field(alias="#text", default=None)

    @field_validator("part")
    def validate_part(cls, value):
        if value not in (None, "first", "middle", "suffix", "last", "full"):
            raise ValueError("Invalid Name Part input")
        return value

    @field_validator("type")
    def validate_type(cls, value):
        if value not in (None, "individual", "business"):
            raise ValueError("Invalid Name Type input")
        return value


class Email(BaseModel):
    preferred_contact: Optional[int] = Field(alias="@preferredcontact", default=None)
    email: Optional[str] = Field(alias="#text", default=None)


class Phone(BaseModel):
    type: Optional[str] = Field(alias="@type", default=None)
    time: Optional[str] = Field(alias="@time", default=None)
    preferred_contact: Optional[int] = Field(alias="@preferredcontact", default=None)
    phone: Optional[str] = Field(alias="#text", default=None)

    @field_validator("type")
    def validate_type(cls, value):
        if value not in (None, "phone", "fax", "cellphone", "pager"):
            raise ValueError("Invalid Phone Type input")
        return value

    @field_validator("time")
    def validate_time(cls, value):
        if value not in (
            None,
            "morning",
            "afternoon",
            "evening",
            "nopreference",
            "day",
        ):
            raise ValueError("Invalid Phone Time input")
        return value


class Street(BaseModel):
    line: Optional[str]= Field(alias="@line", default=None)
    street: Optional[str] = Field(alias="#text", default=None)

    @field_validator("line")
    def validate_line(cls, value):
        if value not in (None, '1', '2', '3', '4', '5'):
            raise ValueError("Invalid Street Line input")
        return value


class Address(BaseModel):
    type: Optional[str] = Field(alias="@type", default=None)
    street: Optional[Street] = None
    apartment: Optional[str] = None
    city: Optional[str] = None
    regioncode: Optional[str] = None
    postalcode: Optional[str] = None
    country: Optional[str] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value not in (None, "work", "home", "delivery"):
            raise ValueError("Invalid Address Type input")
        return value

    @field_validator("country")
    def validate_country(cls, value):
        if is_valid_iso_3166_alpha_2(value) == False:
            raise ValueError("Invalid Country input")
        return value


class Contact(BaseModel):
    primary_contact: Optional[int] = Field(alias="@primarycontact", default=None)
    name: Optional[Union[str, Name, List[Name]]] = None
    email: Optional[Union[str, Email]] = None
    phone: Optional[Union[str, Phone, List[Phone]]] = None
    address: Optional[Address] = None

    @model_validator(mode="after")
    def check_required_fields(cls, contact):
        required_fields = {"name"}  # Add all required field names here
        empty_required_fields = [
            field for field in required_fields if getattr(contact, field) is None
        ]
        if empty_required_fields:
            raise ValueError(
                f"The following required fields in Contact are missing: {', '.join(empty_required_fields)}"
            )
        return contact


class TimeFrame(BaseModel):
    description: Optional[str] = None
    earliest_date: Optional[str] = None
    latest_date: Optional[str] = None

    @model_validator(mode='after')
    def validate_dates(cls, values):
        print(values)
        # earliest_date = getattr(values, earliest_date)
        # latest_date = getattr(values, latest_date)
        if (
            getattr(values, "earliest_date") is None
            and getattr(values, "latest_date") is None
        ):
            raise ValueError("At least one of 'earliest_date' or 'latest_date' must be provided.")
        return values

    @field_validator("earliest_date")
    def validate_earliest_date(cls, value):
        if is_iso8601(value) == False:
            raise ValueError("Invalid Earliest Date input")
        return value

    @field_validator("latest_date")
    def validate_latest_date(cls, value):
        if is_iso8601(value) == False:
            raise ValueError("Invalid Latest Date input")
        return value


class Customer(BaseModel):
    contact: Optional[Contact] = None
    id: Optional[Id] = None
    timeframe: Optional[TimeFrame] = None
    comments: Optional[str] = None

    @model_validator(mode="after")
    def check_required_fields(cls, customer):
        required_fields = {}  # Add all required field names here
        empty_required_fields = [
            field for field in required_fields if getattr(customer, field) is None
        ]
        if empty_required_fields:
            raise ValueError(
                f"The following required fields in Customer are missing: {', '.join(empty_required_fields)}"
            )
        return customer


class Vendor(BaseModel):
    id: Optional[Id] = None
    vendorname: Optional[str] = None
    url: Optional[str] = None
    contact: Optional[Contact] = None

    @model_validator(mode="after")
    def check_required_fields(cls, vendor):
        required_fields = {"vendorname"}  # Add all required field names here
        empty_required_fields = [
            field for field in required_fields if getattr(vendor, field) is None
        ]
        if empty_required_fields:
            raise ValueError(
                f"The following required fields in Vendor are missing: {', '.join(empty_required_fields)}"
            )
        return vendor


class Provider(BaseModel):
    id: Optional[Id] = None
    name: Optional[Name] = None
    service: Optional[str] = None
    url: Optional[str] = None
    email: Optional[Email] = None
    phone: Optional[Phone] = None
    contact: Optional[Contact] = None

    @model_validator(mode="after")
    def check_required_fields(cls, provider):
        required_fields = {"name"}  # Add all required field names here
        empty_required_fields = [
            field for field in required_fields if getattr(provider, field) is None
        ]
        if empty_required_fields:
            raise ValueError(
                f"The following required fields in Provider are missing: {', '.join(empty_required_fields)}"
            )
        return provider


class Prospect(BaseModel):
    status: Optional[str] = Field(alias="@status", default=None)
    id: Optional[Id] = None
    request_date: Optional[str] = Field(alias="requestdate", default=None)
    vehicle: Optional[Union[Vehicle, List[Vehicle]]] = None
    customer: Optional[Customer] = None
    vendor: Optional[Vendor] = None
    provider: Optional[Provider] = None


class ADF(BaseModel):
    prospect: Optional[Prospect] = None


class Lead(BaseModel):
    adf: Optional[ADF] = None

data = {}
lead = Lead()

# try:
#     xml_file_path = "lead1.xml"
#     data = parse_xml_to_json(xml_file_path)
# except Exception as e:
#     print(f"An error occurred: {e}")

# print(data)
# print(lead)
try:
    print(data)
    file_path = input("Enter the path to the JSON file: ")
    with open(file_path, "r") as f:
        data = json.load(f)

    # print(json.dumps(data, indent=2))
    # xml_file_path = "lead1.xml"
    # data = parse_xml_to_json(xml_file_path)
    lead = Lead(**data)

    print(lead)
    print(json.dumps(lead.model_dump(), indent=4))

except FileNotFoundError:
    print("File not found. Please provide a valid file path.")
except json.JSONDecodeError:
    print("Invalid JSON format in the file.")
except ValidationError as e:
    error_messages = []
    for error in e.errors():
        if error["type"] == "value_error":
            error_messages.append(error["msg"])
    if error_messages:
        print("\n".join(error_messages))
    else:
        print("Validation error occured:", e)
except Exception as e:
    print(f"An error occurred: {e}")


# lead = Lead(**data)
# print(lead)
# print(json.dumps(lead.model_dump(), indent=4))

""" adf = ADF(
    prospect=Prospect(
        status="new",
        id=Id(sequence=1, source="ABC"),
        request_date="2019-01-15T18:46:36-06:00",
        vehicle=Vehicle(
            interest="buy", status="used", year="2023", make="Hyundai", model="i30"
        ),
        customer=Customer(
            contact=Contact(
                primary_contact=1,
                name=[
                    Name(part="first", type="individual", name="John"),
                    Name(part="middle", type="individual", name=None),
                    Name(part="last", type="individual", name="Test01292019"),
                ],
                email=Email(preferred_contact=1, email="testemail@domain.com"),
                phone=[
                    Phone(
                        type="phone",
                        time="morning",
                        preferred_contact=1,
                        phone="1234567890",
                    ),
                    Phone(
                        type="cellphone",
                        time="afternoon",
                        preferred_contact=0,
                        phone="9999999999",
                    ),
                    Phone(
                        type="pager",
                        time="evening",
                        preferred_contact=0,
                        phone="9999999999",
                    ),
                    Phone(
                        type="fax", time="day", preferred_contact=0, phone="9999999999"
                    ),
                ],
                address=Address(
                    type="home",
                    street=Street(line="1", street="6299 Airport Road"),
                    apartment=None,
                    city="Mississauga",
                    regioncode="ON",
                    postalcode="L4V1N3",
                    country="Canada",
                ),
            ),
            comments="Date of Birth: 1980-11-17\n            Monthly Payment: 1450\n            Rent_or_own: Rent\n            Time at address: 11 years 2 months\n            Occupation: Occupation1\n            Employer: EmployerName\n            Time with Employer: 2 years 2\n            Monthly Income: 5500\n            Lead Timestamp: 08/31/2019 04:30pm\n            IP Address: 70.25.4.55\n            Comments: looking for SUV, new to the country...",
        ),
        vendor=Vendor(
            vendorname="Approval Genie",
            contact=Contact(
                primary_contact=None,
                name="John B",
                email="john@approvalgenie.ca",
                phone=None,
                address=None,
            ),
        ),
        provider=Provider(
            name=Name(part="full", type="business", name="PROSPECT"),
            email=Email(preferred_contact=1, email="leadprovideremail@domain.com"),
            url="leadprovider.domain.com",
        ),
    )
) """


# {
#     "adf": {
#         "prospect": {
#             "@status": "new",
#             "id": {"@sequence": "1", "@source": "ABC"},
#             "requestdate": "2019-01-15T18:46:36-06:00",
#             "vehicle": {
#                 "@interest": "buy",
#                 "@status": "used",
#                 "make": "Hyundai",
#                 "model": "i30",
#             },
#             "customer": {
#                 "contact": {
#                     "@primarycontact": "1",
#                     "name": [
#                         {"@part": "first", "@type": "individual", "#text": "John"},
#                         {"@part": "middle", "@type": "individual"},
#                         {
#                             "@part": "last",
#                             "@type": "individual",
#                             "#text": "Test01292019",
#                         },
#                     ],
#                     "email": {
#                         "@preferredcontact": "1",
#                         "#text": "testemail@domain.com",
#                     },
#                     "phone": [
#                         {
#                             "@type": "phone",
#                             "@time": "morning",
#                             "@preferredcontact": "1",
#                             "#text": "1234567890",
#                         },
#                         {
#                             "@type": "cellphone",
#                             "@time": "afternoon",
#                             "@preferredcontact": "0",
#                             "#text": "9999999999",
#                         },
#                         {
#                             "@type": "pager",
#                             "@time": "evening",
#                             "@preferredcontact": "0",
#                             "#text": "9999999999",
#                         },
#                         {
#                             "@type": "fax",
#                             "@time": "day",
#                             "@preferredcontact": "0",
#                             "#text": "9999999999",
#                         },
#                     ],
#                     "address": {
#                         "@type": "home",
#                         "street": {"@line": "1", "#text": "6299 Airport Road"},
#                         "apartment": None,
#                         "city": "Mississauga",
#                         "regioncode": "ON",
#                         "postalcode": "L4V1N3",
#                         "country": "Canada",
#                     },
#                 },
#                 "comments": "Date of Birth: 1980-11-17\n            Monthly Payment: 1450\n            Rent_or_own: Rent\n            Time at address: 11 years 2 months\n            Occupation: Occupation1\n            Employer: EmployerName\n            Time with Employer: 2 years 2\n            Monthly Income: 5500\n            Lead Timestamp: 08/31/2019 04:30pm\n            IP Address: 70.25.4.55\n            Comments: looking for SUV, new to the country...",
#             },
#             "vendor": {
#                 "vendorname": "Approval Genie",
#                 "contact": {"name": "John B", "email": "john@approvalgenie.ca"},
#             },
#             "provider": {
#                 "name": {"@part": "full", "@type": "business", "#text": "PROSPECT"},
#                 "email": {
#                     "@preferredcontact": "1",
#                     "#text": "leadprovideremail@domain.com",
#                 },
#                 "url": "leadprovider.domain.com",
#             },
#         }
#     }
# }
