I have the following dictionary: temp = {'match_score': 299, 'billing_account_number': '8301100100157210', 'spectrum_core_account': 'UNSURE', 'spectrum_core_division': 'UNSURE', 'complete_record': InternalRecord(country_code='', phone_number='9809149591', first_name='IOCTPCSI', last_name='DDTDP', zipcode5='93250', email_address='mobilebuyflow6@charter.com', street_number='264', street_name='264 INDUSTRIAL ST', city='MC FARLAND', state='CA', apartment='', ucan='52550478747', division_id='BHR.8301', account_status='Inactive', secondary_number='', account_number='8301100100157210', account_description='Residential', source='BHN', full_address='264 INDUSTRIAL ST MC FARLAND CA', full_address_no_apt='', _account_type=Description(description='Residential'), _address_line_1='264 INDUSTRIAL ST', _address_line_2='')}
i need help in python converting it to the following. What you see now is a base example. only match_score is being done correctly!
json_dt = {
                    "match_score": record.get('match_score', 0),
                    "account_type": record.get('_account_type.description', ''),
                    "status": record.get('match_score', 0),
                    "source": record.get('match_score', 0),
                    "ucan": record.get('match_score', 0),
                    "billing_account_number": record.get('match_score', 0),
                    "spectrum_core_account": record.get('match_score', 0),
                    "spectrum_core_division": record.get('match_score', 0),
                    "name": {
                        "first_name": record.get('match_score', 0),
                        "last_name": record.get('match_score', 0),
                        "middle_name": record.get('match_score', 0),
                        "suffix": record.get('match_score', 0),
                        "prefix": record.get('match_score', 0)
                    },
                    "phone_number": {
                        "country_code": record.get('match_score', 0),
                        "area_code": record.get('match_score', 0),
                        "exchange": record.get('match_score', 0),
                        "line_number": record.get('match_score', 0),
                        "extension": record.get('match_score', 0),
                        "type_code": record.get('match_score', 0),
                    },
                    "address": {
                        "city": record.get('match_score', 0),
                        "state": record.get('match_score', 0),
                        "line1": record.get('match_score', 0),
                        "postal_code": record.get('match_score', 0),
                        "line2": record.get('match_score', 0),
                        "country_code": record.get('match_score', 0)
                    },
                    "email": ""

                }
