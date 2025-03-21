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


class TeamExists(Exception):
    def __init__(self, message):
        self.message = message


class TeamParentError(Exception):
    def __init__(self, message):
        self.message = message
