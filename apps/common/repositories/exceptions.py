class RepositoryException(Exception):
    ''' Exception base class related to repositories '''
    pass


class ObjectNotFoundException(Exception):
    ''' Exception raised when can't find a row '''
    pass
