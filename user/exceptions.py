class UserExists(Exception):
    def __init__(self, message):
        self.message = message


class UserIsArchived(Exception):
    def __init__(self, message):
        self.message = message


class UserIsNotArchived(Exception):
    def __init__(self, message):
        self.message = message
