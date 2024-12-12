@patch('core.models.Request.handle_new_request', Mock())
class TestRequestEligibility(TestCase):

    # fmt: off
    @parameterized.expand([
        ('fully_eligible', date(year=2021, month=1, day=1), date(year=2020, month=1, day=1), True),
        ('ineligible_by_date', date(year=2019, month=1, day=1), date(year=2020, month=1, day=1), False),
        ('ineligible_by_no_regulation', date(year=2021, month=1, day=1), None, False),
    ])

    # fmt: on
    def test_eligible_by_state(
        self, test_name, request_date, regulation_effective_date, expected
    ):
        request_fields = dict(
            request_datetime=request_date,
        )
        if regulation_effective_date:
            request_fields['regulation_cd__effective_date'] = regulation_effective_date
        req = baker.make(
            Request,
            **request_fields,
        )
        self.assertEqual(req.eligible_by_state(), expected)
