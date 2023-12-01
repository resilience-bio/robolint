"""Exceptions."""


class NoStepTypeIdError(AttributeError):
    def __init__(self, class_name: str) -> None:
        super().__init__(f"The step type ID has not been defined as a class attribute for {class_name}")
