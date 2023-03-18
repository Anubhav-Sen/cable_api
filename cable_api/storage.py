from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    """
    A class that defines methods to overwrite storage.
    """
    def get_available_name(self, name, max_length=None):
        """
        A storage method overriden to:
        - Check if a filename exists.
        - Delete the file with that name to make the name available.
        - Return the name.
        """
        if self.exists(name):
             
            self.delete(name)

        return name 