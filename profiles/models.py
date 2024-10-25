from django.contrib.auth import get_user_model
from django.db import models


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


class AbstractProfile(models.Model):
    class Meta:
        _authoritative_fields = []

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.user.username


class PeopleFinderProfile(AbstractProfile):
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


class PeopleFinderTeam(models.Model): ...


class OracleProfile(AbstractProfile):
    costcode = models.ForeignKey(
        "OracleCostCodes",
        on_delete=models.SET_NULL,
        null=True,
    )


class OracleCostCodes(models.Model): ...
