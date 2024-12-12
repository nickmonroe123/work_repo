    def _street_name_and_number(self) -> tuple[str, str]:
        street_matches = re.search(r'^\s*(\d[^\s]*)?\s*(.*)?', self.line1)
        if street_matches:
            street_name = (street_matches.group(2) or '').strip()
            street_number = (street_matches.group(1) or '').strip()
        else:
            street_name = ''
            street_number = ''
        return street_name, street_number
