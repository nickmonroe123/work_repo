 I'll provide a complete example with a class method to handle multiple column names:

```python
from msgspec import Struct
from typing import Optional

class AccountInfo(Struct):
    account_number: Optional[str] = None
    balance: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict):
        # Try different possible column names for account number
        account_number = data.get('accountNumber') or data.get('ACCT_NUM')
        
        # You can do the same for other fields if needed
        balance = data.get('balance')
        
        return cls(
            account_number=account_number,
            balance=balance
        )

# Example usage
def main():
    # Test with different column names
    data1 = {"accountNumber": "12345", "balance": 1000.50}
    data2 = {"ACCT_NUM": "67890", "balance": 2000.75}

    # Parse using the custom class method
    account1 = AccountInfo.from_dict(data1)
    account2 = AccountInfo.from_dict(data2)

    print(account1)  # AccountInfo(account_number='12345', balance=1000.50)
    print(account2)  # AccountInfo(account_number='67890', balance=2000.75)

    # Optional: you can add error handling
    data3 = {"someOtherKey": "value"}
    account3 = AccountInfo.from_dict(data3)
    print(account3)  # AccountInfo(account_number=None, balance=None)

if __name__ == "__main__":
    main()
```

Key points:
- The `from_dict()` class method allows flexible parsing
- It checks multiple possible column names
- Uses `.get()` to safely retrieve values
- Returns an instance of the class with the parsed data
- Handles cases where the expected columns might be missing

This approach gives you maximum flexibility in handling different column name variations while keeping your code clean and readable.

Would you like me to elaborate on any part of this example?
