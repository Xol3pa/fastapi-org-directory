from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Базовая схема, позволяющая читать данные из ORM."""

    model_config = ConfigDict(from_attributes=True)

