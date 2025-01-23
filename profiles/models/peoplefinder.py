from django.db import models

# United Kingdom
DEFAULT_COUNTRY_PK = "CTHMTC00260"




class LearningInterest(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="unique_learning_interest_code"
            ),
            models.UniqueConstraint(
                fields=["name"], name="unique_learning_interest_name"
            ),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class AdditionalRole(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="unique_additional_role_code"
            ),
            models.UniqueConstraint(
                fields=["name"], name="unique_additional_role_name"
            ),
        ]
        ordering = ["name"]

    code = models.CharField(max_length=40)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


def person_photo_path(instance, filename):
    return f"peoplefinder/person/{instance.slug}/photo/{filename}"


def person_photo_small_path(instance, filename):
    return f"peoplefinder/person/{instance.slug}/photo/small_{filename}"
