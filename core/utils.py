from django.db import models


def update_model_fields(kwargs, model: models.Model, valid_fields: list):
    for field in kwargs.keys():
        if field not in valid_fields:
            raise ValueError(
                f"{field} is not a valid field for model {model.__str__()}"
            )
    # Update model attributes with provided keyword arguments
    for field, value in kwargs.items():
        if hasattr(model, field):
            setattr(model, field, value)

    model.save()
    return model
