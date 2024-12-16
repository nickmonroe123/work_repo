    def clean_output_list(self) -> list[IdentifiedAccount]:
        sorted_data: list[IdentifiedAccount] = sorted(
            self.output_list, key=itemgetter('match_score'), reverse=True
        )
        # Remove duplicates based on the fourth item
        unique_data = []
        seen = set()
        for item in sorted_data:
            acct_num = item.billing_account_number
            if acct_num not in seen and acct_num != '':
                unique_data.append(item)
                seen.add(acct_num)

        return unique_data

class IdentifiedAccount(FullIdentifier):
    match_score: float = 0.0
    account_type: str = ""
    status: str = ""
    source: str = ""
    ucan: str = ""
    billing_account_number: str = ""
    spectrum_core_account: str = ""
    spectrum_core_division: str = ""

TypeError at /account_identification/api/
'IdentifiedAccount' object is not subscriptable
