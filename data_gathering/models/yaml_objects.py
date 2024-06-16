from datetime import date

import yaml


class CurrentDate(yaml.YAMLObject):
    """
    A class for representing and handling the current date, integrating with YAML.

    This class extends `yaml.YAMLObject` to facilitate custom YAML deserialization. The `CurrentDate`
    class allows the current date to be injected dynamically when a specific placeholder is encountered
    in the YAML input.

    Attributes:
    -----------
    yaml_tag : str
        YAML tag used to identify this custom object type in YAML files.

    current_date : str
        The date stored in the instance, formatted as a string in "YYYY-MM-DD" format.

    Methods:
    --------
    __init__(self, current_date=None) -> None:
        Initializes a `CurrentDate` instance with the provided date, or defaults to today's date if none is given.

    __repr__(self) -> str:
        Returns a string representation of the `CurrentDate` instance.

    from_yaml(cls, loader, node):
        Class method to create a `CurrentDate` instance from YAML input. If the input is a placeholder for the
        current date, it substitutes it with today's date.
    """

    yaml_tag = "!TODAY"

    def __init__(self, current_date=None) -> None:
        """
        Initializes the CurrentDate instance.

        Parameters:
        -----------
        current_date : str, optional
            The date to initialize the instance with, formatted as "YYYY-MM-DD". Defaults to None,
            in which case the current date is used.
        """
        if current_date is None:
            current_date = date.today().strftime("%Y-%m-%d")
        self.current_date = current_date

    def __repr__(self) -> str:
        """
        Returns a string representation of the CurrentDate instance.

        Returns:
        --------
        str
            A string in the format "CurrentDate(current_date=YYYY-MM-DD)".
        """
        return f"{self.__class__.__name__}(current_date={self.current_date})"

    @classmethod
    def from_yaml(cls, loader, node):
        """
        Creates a CurrentDate instance from a YAML node.

        This method handles the deserialization of the custom YAML tag `!TODAY`. If the node contains
        the placeholder value "{{ CURRENT DATE }}", it is replaced with the actual current date.

        Parameters:
        -----------
        loader : yaml.Loader
            The YAML loader instance.
        node : yaml.Node
            The YAML node to deserialize.

        Returns:
        --------
        CurrentDate
            An instance of the CurrentDate class with the date set appropriately.
        """
        # Load the data from YAML
        data = loader.construct_scalar(node)

        # Check if the data is a placeholder value
        if isinstance(data, str) and data.strip() == "CURRENT_DATE":
            today = date.today().strftime("%Y-%m-%d")
            return cls(today)
        return cls(data)
