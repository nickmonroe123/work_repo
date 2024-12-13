def normalize_address(address: str) -> str:
    """Normalize an address by replacing street abbreviations, removing spaces,
    and lowercasing."""
    cleaned = []
    for word in address.split():
        word = word.upper()
        for abbr, full in constants.STREET_ACRO.items():
            pattern = r'\b{}\b'.format(re.escape(abbr))
            if re.search(pattern, word):
                cleaned.append(full.lower())
        cleaned.append(word.lower())
    return ''.join(cleaned)
