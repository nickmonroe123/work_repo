def transform_record(record):
    # Helper function to safely get nested attributes
    def safe_get(obj, attr, default=''):
        try:
            # Split the attribute path
            parts = attr.split('.')
            for part in parts:
                obj = getattr(obj, part) if hasattr(obj, part) else obj[part]
            return obj
        except (AttributeError, KeyError, TypeError):
            return default

    # Parse phone number
    phone_number = safe_get(record, 'phone_number', '')
    
    json_dt = {
        "match_score": record.get('match_score', 0),
        "account_type": safe_get(record, '_account_type.description', ''),
        "status": record.get('account_status', ''),
        "source": record.get('source', ''),
        "ucan": record.get('ucan', ''),
        "billing_account_number": record.get('billing_account_number', ''),
        "spectrum_core_account": record.get('spectrum_core_account', ''),
        "spectrum_core_division": record.get('spectrum_core_division', ''),
        "name": {
            "first_name": record.get('first_name', ''),
            "last_name": record.get('last_name', ''),
            "middle_name": "",  # No middle name in the original record
            "suffix": "",  # No suffix in the original record
            "prefix": ""  # No prefix in the original record
        },
        "phone_number": {
            "country_code": safe_get(record, 'country_code', ''),
            "area_code": phone_number[:3] if phone_number else '',
            "exchange": phone_number[3:6] if len(phone_number) >= 6 else '',
            "line_number": phone_number[6:] if len(phone_number) >= 6 else '',
            "extension": "",  # No extension in the original record
            "type_code": "",  # No type code in the original record
        },
        "address": {
            "city": record.get('city', ''),
            "state": record.get('state', ''),
            "line1": record.get('_address_line_1', ''),
            "postal_code": record.get('zipcode5', ''),
            "line2": record.get('_address_line_2', ''),
            "country_code": record.get('country_code', '')
        },
        "email": record.get('email_address', '')
    }
    
    return json_dt

# Example usage
temp = {'match_score': 299, 'billing_account_number': '8301100100157210', 'spectrum_core_account': 'UNSURE', 'spectrum_core_division': 'UNSURE', 'complete_record': InternalRecord(country_code='', phone_number='9809149591', first_name='IOCTPCSI', last_name='DDTDP', zipcode5='93250', email_address='mobilebuyflow6@charter.com', street_number='264', street_name='264 INDUSTRIAL ST', city='MC FARLAND', state='CA', apartment='', ucan='52550478747', division_id='BHR.8301', account_status='Inactive', secondary_number='', account_number='8301100100157210', account_description='Residential', source='BHN', full_address='264 INDUSTRIAL ST MC FARLAND CA', full_address_no_apt='', _account_type=Description(description='Residential'), _address_line_1='264 INDUSTRIAL ST', _address_line_2='')}

# Transform the record
result = transform_record(temp['complete_record'])
print(result)
