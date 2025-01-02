This behavior typically occurs due to Django's model instance caching mechanism or database transaction isolation. Here are the main potential causes and solutions:

1. **QuerySet Cache**
The objects might be cached in your Django application. To force a fresh database query, you can try:

```python
Epic.objects.all().iterator()  # Uses less memory and bypasses cache
# or
Epic.objects.all().none()  # Clears the queryset cache
Epic.objects.all()         # Fresh query
```

2. **Database Transaction**
If you deleted the record directly in Oracle SQL UI while your Django application is running, the application might be operating in a different transaction that hasn't been synchronized. Try:

```python
from django.db import connection
connection.close()  # Force a new database connection

# Then query again
Epic.objects.all()
```

3. **Read Committed Isolation**
Oracle's default isolation level is "Read Committed". You might need to:
- Commit any pending transactions in Oracle
- Ensure your Oracle session that deleted the record is committed
- Check if any Django transaction is open:

```python
from django.db import transaction
with transaction.atomic():
    # Your query here
    Epic.objects.all()
```

To debug this, you can try:

```python
def create_or_update(self, epic_data: Dict):
    # Force a fresh connection
    from django.db import connection
    connection.close()
    
    # Print with more details
    for obj in Epic.objects.all():
        print(f"ID: {obj.id}, Created: {obj.created_at}")  # Add relevant fields
        
    # You can also check the raw SQL
    print(Epic.objects.all().query)
    
    Epic.objects.update_or_create(
        id=epic_data['id'],
        defaults=epic_data
    )
```

If the issue persists, you might want to:
1. Check if there are any uncommitted transactions in Oracle
2. Verify the connection settings in your Django database configuration
3. Double-check if the deletion in Oracle was properly committed
4. Consider using `select_for_update()` if concurrent access is an issue:

```python
with transaction.atomic():
    Epic.objects.select_for_update().filter(id=epic_data['id']).first()
```
