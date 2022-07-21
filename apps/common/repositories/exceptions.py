class RepositoryException(Exception):
    """Exception base class related to repositories."""


class ObjectNotFoundException(Exception):
    """Exception raised when can't find a row."""


class ObjectAlreadyExistsException(Exception):
    """Exception raised when unique constraint failes."""
