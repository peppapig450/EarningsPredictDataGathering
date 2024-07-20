from typing import Protocol, runtime_checkable


@runtime_checkable
class SymbolFilteringProtocol(Protocol):
    """
    A protocol for defining the methods required for classes that handle symbol filtering
    according to API-specific rules. This protocol ensures that any class implementing it
    can define its own criteria for validating and filtering symbols based on the API's
    requirements.

    Methods:
    -------
    - get_api_name: Returns the name of the API for which the protocol is implemented. This
      method allows the filtering system to distinguish between different APIs and apply
      the appropriate filtering logic accordingly.
    - get_valid_currencies: Returns a list of valid currencies (or exchanges) that are acceptable
      for the API. This method provides the criteria for which symbols are considered valid
      based on the API's supported currencies or exchanges.
    - get_regex_filter_pattern: Returns a regex pattern used to validate and filter
      symbols according to the API's rules. This method ensures that symbols are in the correct
      format and meet the API's pattern requirements.

    Example:
    -------
        Implementing a class that follows this protocol would need to provide logic for 
        determining which symbols are valid and how to format them according to the API's 
        specifications. For instance, a class implementing this protocol might filter symbols
        to only include those that match a specific format or are listed on certain exchanges.

    Notes:
    ------
        The `get_api_name` method helps identify the API-specific implementation, which
        can be useful for managing multiple APIs with different filtering criteria, and for 
        caching filtered symbols in a dictionary with the API as the key.
    """
    def get_api_name(self) -> str:
        """Return the API name that the protocol is implementing filtering for."""
        return ""
    
    def get_valid_currencies(self) -> list[str]:
        """Return a list of valid currencies (or exchanges) supported by the API, which are
        considered acceptable for the API's symbol filtering criteria."""
        return [""]
        
    def get_regex_filter_pattern(self) -> str:
        """Return a regex pattern used to filter out symbols that do not match
        the API's expected format or pattern requirements."""
        return ""