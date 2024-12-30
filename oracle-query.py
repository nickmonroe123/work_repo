Ah, I understand - you want to explicitly close the transaction to release any locks. Here's how to modify the code to ensure proper transaction cleanup:

```python
def create_or_update(self, story_data: Dict):
    """Create or update Story records."""
    from django.db import Error as DBError
    from django.db.utils import OperationalError
    from django.db import transaction, connection

    try:
        # Remove epic_key from defaults since it's not a model field
        epic_key = story_data.pop('parent', None)

        print(f"Processing story {story_data['id']} with epic_key {epic_key}")

        # First, try to find the parent epic
        parent_epic = None
        if epic_key:
            try:
                parent_epic = Epic.objects.get(id=epic_key)
                print(f"Found parent epic {epic_key}")
            except Epic.DoesNotExist:
                print(f"Parent Epic {epic_key} not found for Story {story_data['id']}")

        # Prepare the defaults
        defaults = story_data.copy()
        if parent_epic:
            defaults['parent'] = parent_epic

        print(f"Attempting to update/create story with defaults: {defaults}")

        # Create or update the story within a transaction
        with transaction.atomic():
            print("hi1")
            story, created = Story.objects.update_or_create(
                id=story_data['id'],
                defaults=defaults
            )
            print("hi2")

            action = "Created" if created else "Updated"
            print(f"{action} story {story.id} successfully")

        # Explicitly close the transaction and release locks
        connection.close()
        
        return story

    except DBError as e:
        print(f"Database error while processing story {story_data['id']}: {str(e)}")
        connection.close()  # Ensure connection is closed even on error
        raise
    except Exception as e:
        print(f"Unexpected error while processing story {story_data['id']}: {str(e)}")
        connection.close()  # Ensure connection is closed even on error
        raise
    finally:
        # Make absolutely sure the connection is closed
        try:
            connection.close()
        except:
            pass
```

Key changes:
1. Added `connection.close()` after successful operation
2. Added `connection.close()` in error handlers
3. Added a `finally` block to ensure the connection is always closed
4. Using `with transaction.atomic():` to properly scope the transaction

The `connection.close()` call will:
1. Commit any pending transactions
2. Release any locks held by the connection
3. Return the connection to the connection pool
4. Free up resources on both the Python and database side

This should help prevent the "resource busy" errors by ensuring that connections and locks are properly released after each operation. Let me know if you're still seeing any lock-related issues!
