from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import options
from simple_history.models import HistoricalRecords


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("authoritative_fields",)

# 1,
# list_auth_fields = []
# if field in list:
#     then it's a super cool field
# else:
#     boring regular field

# 2,
# if field.is_authoritative:
#       then it's a super cool field
# else:
#       boring regular field


class FieldAuthoritativenessMixin:
    is_authoritative: bool = False

    def __init__(self, *args, **kwargs):
        self.is_authoritative = bool(kwargs.pop("is_authoritative", False))
        super().__init__(
            *args,
            **kwargs,
        )


class AuthoritativeCharField(FieldAuthoritativenessMixin, models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        ),


class AbstractHistoricalModel(models.Model):
    class Meta:
        abstract = True

    history = HistoricalRecords(
        inherit=True,
    )


class AbstractProfile(AbstractHistoricalModel):
    class Meta:
        authoritative_fields = []
        abstract = True

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.user.username


class PeopleFinderProfile(AbstractProfile):
    # class Meta:
    # authoritative_fields = {
    #     "fav_program": {
    #         "root_record": {
    #             "model": "Oracle",
    #             "field": "super_oracle",
    #         },
    #     },
    #     "super_important": {"root_record": "__self__"},
    # }

    fav_program = AuthoritativeCharField(
        verbose_name="fav_program",
        max_length=255,
        null=True,
        is_authoritative=False,
    )
    super_important = AuthoritativeCharField(
        verbose_name="super_important",
        max_length=255,
        null=True,
        is_authoritative=True,
    )
    team = models.ForeignKey(
        "PeopleFinderTeam",
        on_delete=models.SET_NULL,
        null=True,
    )


class PeopleFinderTeam(AbstractHistoricalModel):
    name = models.CharField(
        null=True,
    )

    def __str__(self):
        return self.name


class OracleProfile(AbstractProfile):
    costcode = models.ForeignKey(
        "OracleCostCodes",
        on_delete=models.SET_NULL,
        null=True,
    )
    # fav_program = models.ForeignKey(
    #     "PeopleFinderProfile",
    #     on_delete=models.SET_NULL,
    #     null=True,
    # )


class OracleCostCodes(AbstractHistoricalModel):
    code = models.CharField(
        null=True,
    )
    description = models.CharField(
        null=True,
    )

    def __str__(self):
        return self.code
