from django.db.models.enums import TextChoices


class EntryCommands(TextChoices):
    CREATE_ENTRY = 'create_entry'
    RETRIEVE_ENTRY = 'retrieve_entry'
    UPDATE_ENTRY =  'update_entry'
    DESTROY_ENTRY = 'destroy_entry'
    LIST_ENTRIES = 'list_entries'
    NO_COMMAND = 'no_command'