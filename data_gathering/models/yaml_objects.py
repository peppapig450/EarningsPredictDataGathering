from datetime import date
import yaml


class CurrentDate(yaml.YAMLObject):
    yaml_tag = "!TODAY"

    def __init__(self, current_date=None) -> None:
        if current_date is None:
            current_date = date.today().strftime("%Y-%m-%d")
        self.current_date = current_date

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(current_date={self.current_date})"

    @classmethod
    def from_yaml(cls, loader, node):
        # Load the data from YAML
        data = loader.construct_scalar(node)

        # Check if the data is a placeholder value
        if isinstance(data, str) and data.strip() == "{{ CURRENT DATE }}":
            today = date.today().strftime("%Y-%m-%d")
            return cls(today)
        return cls(data)
