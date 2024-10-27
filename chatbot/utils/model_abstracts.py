import uuid
from django.db import models


class Model(models.Model):
    """
    Abstract base model class with a UUID primary key.

    Attributes:
        id (UUIDField): Primary key for the model, automatically generated using UUID4.

    Meta:
        abstract (bool): Indicates that this is an abstract base class and should not be used to create any database table.
    """

    id = models.UUIDField(primary_key=True, 
                          default=uuid.uuid4, 
                          editable=False)

    class Meta:
        abstract = True