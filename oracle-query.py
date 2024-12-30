    def create_or_update(self, story_data: Dict):
        """Create or update Story records."""
        from django.db import Error as DBError

        print("hi1")

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

            # Create or update the story with a timeout
            from django.db import connection
            connection.execute_wrapper = None  # Reset any existing wrappers

            print("hi1")
            story, created = Story.objects.update_or_create(
                id=story_data['id'],
                defaults=defaults
            )
            print("hi2")

            action = "Created" if created else "Updated"
            print(f"{action} story {story.id} successfully")

            return story

        except DBError as e:
            print(f"Database error while processing story {story_data['id']}: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error while processing story {story_data['id']}: {str(e)}")
            raise

hi1
Processing story DPCP-2884 with epic_key DPCP-10
Found parent epic DPCP-10
�Attempting to update/create story with defaults: {'id': 'DPCP-2884', 'status': 'NEW', 'issue_type': 'STORY', 'close_date': None, 'parent': <Epic: Epic object (DPCP-10)>}
hi1
Heres my above code and output. As you can see, it never gets to hi2?
