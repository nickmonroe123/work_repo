Story.objects.update_or_create(
            id=story_data['id'],
            defaults={**story_data, 'parent': parent_epic} if parent_epic else story_data
        )
This part of the code runs endlessly and never throws out an error or executes?
