import msgspec
from rest_framework.response import Response
from utilities.views import MsgSpecAPIView
from identifiers.structs import FullIdentifier
from account_identification.services import AccountProcess


class IdentifyAccountsView(MsgSpecAPIView):
    def post(self, request, *args, **kwargs):
        search_input = msgspec.json.decode(request.data, type=FullIdentifier)
        account_processor = AccountProcess()
        results = account_processor.full_search(search_input=search_input)
        return Response(data=results)
