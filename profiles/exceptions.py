class ProfileIsArchived(Exception):
    def __init__(self, message):
        self.message = message


class ProfileIsNotArchived(Exception):
    def __init__(self, message):
        self.message = message


class ProfileExists(Exception):
    def __init__(self, message):
        self.message = message
