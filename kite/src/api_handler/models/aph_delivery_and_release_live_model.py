# ------------------------------------------------------------------------------
# Model
# ------------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class MainModel(BaseModel):
    """
    Base model configuration for all Pydantic models in the application.

    This class sets a common configuration for alias generation and name population
    for any model that inherits from it. It uses camelCase for JSON field names.

    Attributes:
        model_config (ConfigDict): Configuration for Pydantic models, including:
            alias_generator (function): A function to generate field aliases.
                Here, it uses `to_camel` to convert field names to camelCase.
            populate_by_name (bool): Allows population of fields by name when using Pydantic models.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class OrderModel(MainModel):
    """
    Pydantic model representing a Order.

     Attributes:
        order_number (int): The order numner of the Order (not nullable).
        kpid (String): The kpid of the order.
        coi (String): The coi of the order (not nullable).
        material_type (String): material_type of the order.
        product (String): The product number of the order (not nullable, unique).
        country (String): The country details of the order (not nullable).
        run_type (String): The run type in the order's position.
        process_type (String): The process_type to which the order belongs.
        mfg_organization (String): The mfg_organization of the order.
    """
    order_number: int
    kpid: str
    coi: str
    material_type: str
    product: str
    country: str
    run_type: str
    process_type: str
    mfg_organization: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj)
