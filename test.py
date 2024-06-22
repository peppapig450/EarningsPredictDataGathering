from enum import StrEnum


class Categories(StrEnum):
    HISTORICAL = "HistoricalClass"
    FUNDAMENTAL = "FundamentalClass"


class Meta(type):
    def __call__(cls, *args, **kwargs):
        category = kwargs.get("category")
        category_class_name = Categories(category)

        category_class = next(
            (
                subclass
                for subclass in cls.__subclasses__()
                if subclass.__name__ == category_class_name
            ),
            None,
        )

        # print(category_class.__dict__)
        # print(cls.__dict__)
        if category_class is None:
            raise TypeError(f"Unknown category class")

        CategoryClass = type(
            category_class_name,
            (category_class, cls),
            {
                attr: getattr(cls, attr)
                for attr in cls.__dict__
                if not callable(getattr(cls, attr))
            },
        )

        # Dynamically add methods from category_class to the new class
        for attr, method in category_class.__dict__.items():
            if callable(method):
                setattr(CategoryClass, attr, method)

        return CategoryClass.__new__(*args, **kwargs)


class MyClass(metaclass=Meta):
    def __init__(self, /, category):
        self.category = category


class HistoricalClass(MyClass):
    def run(self):
        print("Running historical analysis...")


class FundamentalClass(MyClass):
    pass


instance = MyClass(category=Categories.HISTORICAL)
print(instance.run())
