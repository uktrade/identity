class ProfileIsArchived(Exception):
    def __init__(self, message):
        self.message = message


class ProfileIsNotArchived(Exception):
    def __init__(self, message):
        self.message = message


class ProfileExists(Exception):
    def __init__(self, message):
        self.message = message


class NonCombinedProfileExists(Exception):
    def __init__(self, message):
        self.message = message


# Team exceptions
class TeamExists(Exception):
    def __init__(self, message):
        self.message = message


class TeamRootError(Exception):
    def __init__(self, message):
        self.message = message


class TeamChildError(Exception):
    def __init__(self, message):
        self.message = message


class TeamParentError(Exception):
    def __init__(self, message):
        self.message = message


class TeamMemberError(Exception):
    def __init__(self, message):
        self.message = message


class ParentTeamDoesNotExist(Exception):
    def __init__(self, message):
        self.message = message


class TeamSlugError(Exception):
    def __init__(self, message):
        self.message = message
