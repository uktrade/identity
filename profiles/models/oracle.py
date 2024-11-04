from django.db import models as django_models
from simple_history.models import HistoricForeignKey

from profiles.models import AbstractHistoricalModel, AbstractProfile


class OracleProfile(AbstractProfile):
    costcode = HistoricForeignKey(
        "OracleCostCodes",
        on_delete=django_models.SET_NULL,
        null=True,
    )


class OracleCostCodes(AbstractHistoricalModel):
    code = django_models.CharField(
        null=True,
    )
    description = django_models.CharField(
        null=True,
    )

    def __str__(self):
        return self.code
