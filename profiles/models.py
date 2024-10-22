from django.contrib.auth import get_user_model
from django.db import models


class FieldAuthoritativenessMixin():
    def __init__(self,*args, **kwargs):
        if "is_authoritative" not in kwargs:
            raise TypeError()
        
        self.is_authoritative = kwargs['is_authoritative']
        super(FieldAuthoritativenessMixin,self).__init__(*args,**kwargs)

class CharField(models.CharField,FieldAuthoritativenessMixin):
    ...


class AbstractProfile(models.Model):
    class Meta:
        _authoritative_fields = []

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )


class PeopleFinderProfile(AbstractProfile):
    fav_progarm = CharField(max_length=255, null=True)
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
