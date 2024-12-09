# Extensive Parametrized Tests
@pytest.mark.parametrize("test_input", [
    # Standard full name
    create_test_full_identifier(first_name="John", last_name="Doe"),

    # Unicode names
    create_test_full_identifier(first_name="José", last_name="García"),

    # Very long names
    create_test_full_identifier(first_name="A" * 50, last_name="B" * 50),

    # Minimal information - just name
    FullIdentifier(
        name=Name(first_name="Mini", last_name="User"),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code=""),
        email=""
    ),

    # Minimal information - just phone number
    FullIdentifier(
        name=Name(first_name="", last_name=""),
        phone_number=PhoneNumber(area_code="555", exchange="666", line_number="7777"),
        address=Address(city="", state="", line1="", postal_code=""),
        email=""
    ),

    # Minimal information - just bad phone number
    FullIdentifier(
        name=Name(first_name="", last_name=""),
        phone_number=PhoneNumber(area_code="2555", exchange="6266", line_number="77727"),
        address=Address(city="", state="", line1="", postal_code=""),
        email=""
    ),


    # Minimal information - just address
    FullIdentifier(
        name=Name(first_name="", last_name=""),
        phone_number=PhoneNumber(),
        address=Address(city="Alton", state="IL", line1="213 street", postal_code="62002"),
        email=""
    ),

    # Minimal information - just email
    FullIdentifier(
        name=Name(first_name="", last_name=""),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code=""),
        email="testemail@outlook.com"
    ),

    # Minimal information - full name, bad state
    FullIdentifier(
        name=Name(first_name="Luke", last_name="Test"),
        phone_number=PhoneNumber(),
        address=Address(city="", state="ASD", line1="", postal_code=""),
        email="testemail@outlook.com"
    ),

    # Minimal information - full name, bad zip
    FullIdentifier(
        name=Name(first_name="Luke", last_name="Test"),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code="123"),
        email="testemail@outlook.com"
    ),

    # Full data, bad input
    FullIdentifier(
        name=Name(first_name="Luke", last_name="Test"),
        phone_number=PhoneNumber(area_code="2555", exchange="6266", line_number="77727"),
        address=Address(city="", state="ALS", line1="", postal_code="123"),
        email=""
    ),

    # International address
    create_test_full_identifier(
        street_line1="789 International St",
        city="Toronto",
        state="ON",
        postal_code="M5V 2T6"
    )
])
def test_comprehensive_full_identifier_processing(test_input):
    account_process = AccountProcess()

    try:
        # Run full search
        results = account_process.full_search(test_input)

        # Basic validation
        assert isinstance(results, list)

        # Optional: More specific checks based on type of input
        if results:
            for result in results:
                assert isinstance(result, IdentifiedAccount)

    except Exception as e:
        # Unexpected errors should fail the test
        pytest.fail(f"Unexpected error in processing: {e}")
