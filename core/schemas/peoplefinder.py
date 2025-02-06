from ninja import ModelSchema

from profiles.models.peoplefinder import (
    PeopleFinderProfile,
    PeopleFinderProfileTeam,
    PeopleFinderTeam,
    PeopleFinderTeamTree,
)


class PeopleFinderProfileSchema(ModelSchema):
    class Meta:
        model = PeopleFinderProfile
        fields = [
            "slug",
            "user_id",
            "first_name",
            "preferred_first_name",
            "last_name",
            "pronouns",
            "name_pronunciation",
            "email_id",
            "contact_email_id",
            "primary_phone_number",
            "secondary_phone_number",
            "photo",
            "photo_small",
            "grade",
            "manager_id",
            "not_employee",
            "workdays",
            "remote_working",
            "usual_office_days",
            "uk_office_location_id",
            "location_in_building",
            "international_building",
            "country_id",
            "professions",
            "additional_roles",
            "other_additional_roles",
            "key_skills",
            "other_key_skills",
            "learning_interests",
            "other_learning_interests",
            "fluent_languages",
            "intermediate_languages",
            "previous_experience",
            "is_active",
            "became_inactive",
            "edited_or_confirmed_at",
            "login_count",
            "profile_completion",
            "ical_token",
        ]


class PeopleFinderTeamSchema(ModelSchema):
    class Meta:
        model = PeopleFinderTeam
        fields = [
            "slug",
            "name",
            "abbreviation",
            "description",
            "leaders_ordering",
            "cost_code",
            "team_type",
        ]


class PeopleFinderProfileTeamSchema(ModelSchema):
    class Meta:
        model = PeopleFinderProfileTeam
        fields = [
            "peoplefinder_profile",
            "team",
            "job_title",
            "head_of_team",
            "leaders_position",
        ]


class PeopleFinderTeamTreeSchema(ModelSchema):
    class Meta:
        model = PeopleFinderTeamTree
        fields = ["parent", "child", "depth"]
