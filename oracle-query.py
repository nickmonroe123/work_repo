        try:
            self.street_number, self.street_name = (
                self._address_line_1.split(' ')[0],
                self._address_line_1,
            )
        except:
            self.street_number, self.street_name = "", ""
