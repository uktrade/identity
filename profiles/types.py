# This constant lets us distinguish between function params we explicitly are
# trying to unset (e.g. on update actions) vs ones we don't know about
class Unset(str): ...


UNSET = Unset("__unset__")
