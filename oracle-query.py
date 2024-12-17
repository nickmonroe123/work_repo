    def _parse_spectrum_core_api(
        self,
        payload: dict,
        function_url: str,
        function_name: str,
        post_processing_function=None,
        response_key='getSpcAccountDivisionResponse',
        response_list_key='spcAccountDivisionList',
    ) -> list[InternalRecord]:
        """Helper function for parsing information from spectrum core services
        account API."""
        try:
            # Make the post request call out to spectrum core services
            # TODO: Need to add the certificate authentication here
            response = requests.request("POST", function_url, json=payload)
            # Will return an HTTPError object if an error has occurred during the process
            response.raise_for_status()
            # For now if it fails return empty list. Its possible there are just no records here
            response_key_contents = response.json().get(response_key)
            if response_key_contents is None:
                logger.error(
                    f"The format of the JSON has been changed during {function_name}! New format: {response.json()}"
                )
                raise ValueError('Format of Spectrum Core Account API has changed')
            core_services_list_to_add = response_key_contents.get(response_list_key, [])
            if post_processing_function is not None:
                core_services_list_to_add = post_processing_function(
                    core_services_list_to_add
                )
            core_services_list_to_add = [
                msgspec.convert(x, type=InternalRecord)
                for x in core_services_list_to_add
            ]
            return core_services_list_to_add
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in spectrum core api search: {function_name}")
            raise e
