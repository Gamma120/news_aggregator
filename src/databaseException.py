
from logging import WARNING, ERROR, INFO

#######################
#   ERROR EXCEPTION   #
#######################

class DatabaseError(Exception):
    """Base class for database exceptions."""
    
    def __init__(self, level=ERROR, message="Error appended in database") -> None:
        self.message = message
        self.level = level
        super().__init__(self.message)
        
    def __str__(self) -> str:
        return super().__str__()
    
class RowNotFound(DatabaseError):
    """Exception raised when no row is found."""
    
    def __init__(self, table_name, message="No row matched query.") -> None:
        self.table_name = table_name
        self.message = message
        super().__init__(ERROR, message)
  
    def __str__(self) -> str:
        return f'{self.message} Table : {self.table_name}'
    
class MultipleValuesError(DatabaseError):
    """Exception raised when multiple values match.

    Attributes:
        table_name (String):  table queried
        rows       (Dict):   dictionnary of rows queried
        message    (String): explanation of the warining
    """
    
    def __init__(self, table_name, rows, message="Multiple rows match query.") -> None:
        self.table_name = table_name
        self.rows = rows
        self.message = message
        super().__init__(ERROR, message)
        
    def __str__(self) -> str:
        return f'{self.message} Table : {self.table_name}. Rows : {self.rows}'


#########################
#   WARNING EXCEPTION   #
#########################

class DatabaseWarning(UserWarning):
    """Base class for database warnings."""

    def __init__(self, level=WARNING, message="Warning appended in database") -> None:
        self.message = message
        self.level = level
        super().__init__(self.message)


class MultipleValuesWarning(DatabaseWarning):
    """Exception raised when multiple values match.

    Attributes:
        table_name (String):  table queried
        rows       (Dict):   dictionnary of rows queried
        message    (String): explanation of the warining
    """
    
    def __init__(self, table_name, rows, message="Multiple rows match query.") -> None:
        self.table_name = table_name
        self.rows = rows
        self.message = message
        super().__init__(WARNING, message)
        
    def __str__(self) -> str:
        return f'{self.message} Table : {self.table_name}. Rows : {self.rows}'