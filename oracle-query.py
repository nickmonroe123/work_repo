class MsgspecJSONRenderer(BaseRenderer):
    """Allow rendering of MsgSpec Json."""

    media_type = 'application/json'
    format = 'json'

    def get_indent(self, accepted_media_type, renderer_context):
        if accepted_media_type:
            # If the media type looks like 'application/json; indent=4',
            # then pretty print the result.
            # Note that we coerce `indent=0` into `indent=None`.
            base_media_type, params = parse_header_parameters(accepted_media_type)
            with contextlib.suppress(KeyError, ValueError, TypeError):
                return zero_as_none(max(min(int(params['indent']), 8), 0))
        # If 'indent' is provided in the context, then pretty print the result.
        # E.g. If we're being called by the BrowsableAPIRenderer.
        return renderer_context.get('indent', None)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)
        try:
            print("hi1")
            print(data)
            print("hi2")
            json_bytes = msgspec.json.encode(data)
            return msgspec.json.format(json_bytes, indent=indent)
        except (msgspec.EncodeError, TypeError):
            return json.dumps(data, indent=indent).encode()

[IdentifiedAccount(name=Name(first_name='BTASANFEC', last_name='BTASTEAM', middle_name='', suffix='', prefix=''), phone_number=PhoneNumber(country_code='', area_code='555', exchange='123', line_number='4567', extension='', type_code=''), address=Address(city='', state='', line1='', postal_code='', line2='', country_code=''), email='', match_score=126, account_type='Residential Test', status='Former', source='CNT', ucan='No uCan', billing_account_number='8260130050663312', spectrum_core_account='8260130050663312', spectrum_core_division='NTX.8260'), IdentifiedAccount(name=Name(first_name='SPECTRUM', last_name='LLC2', middle_name='', suffix='', prefix=''), phone_number=PhoneNumber(country_code='', area_code='555', exchange='123', line_number='4567', extension='', type_code=''), address=Address(city='', state='', line1='', postal_code='', line2='', country_code=''), email='', match_score=118, account_type='Internal Use', status='Active', source='CST', ucan='No uCan', billing_account_number='8260141459964920', spectrum_core_account='8260141459964920', spectrum_core_division='STX.8260'), IdentifiedAccount(name=Name(first_name='', last_name='', middle_name='', suffix='', prefix=''), phone_number=PhoneNumber(country_code='', area_code='', exchange='', line_number='', extension='', type_code=''), address=Address(city='', state='', line1='', postal_code='', line2='', country_code=''), email='test@example.com', match_score=77, account_type=<member 'description' of 'Description' objects>, status='', source='', ucan='UCAN123', billing_account_number='12345', spectrum_core_account='12345', spectrum_core_division='')]
