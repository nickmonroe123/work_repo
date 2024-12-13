import msgspec
from account_identification.tasks import identify_accounts
from identifiers.structs import FullIdentifier
from rest_framework.response import Response
from utilities.views import MsgSpecAPIView


class IdentifyAccountsView(MsgSpecAPIView):

    def post(self, request, *args, **kwargs):
        search_input = msgspec.json.decode(request.data, type=FullIdentifier)
        results = identify_accounts(search_input=search_input)
        return Response(data=results)

from account_identification.structs import IdentifiedAccount
from identifiers.structs import FullIdentifier


def identify_accounts(search_input: FullIdentifier) -> list[IdentifiedAccount]:
    """Provide identified accounts based on the provided search input."""
    search_outputs = [
        IdentifiedAccount(
            name=search_input.name,
            phone_number=search_input.phone_number,
            email=search_input.email,
            address=search_input.address,
            match_score=1.0,
        ),
    ]
    return search_outputs
