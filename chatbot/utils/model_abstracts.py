import uuid
from django.db import models


class Model(models.Model):
    """
    Abstract model to add UUID as primary key
    """
    id = models.UUIDField(primary_key=True, 
                          default=uuid.uuid4, 
                          editable=False)

    class Meta:
        abstract = True