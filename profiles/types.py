from enum import Enum, StrEnum


# This constant lets us distinguish between function params we explicitly are
# trying to unset (e.g. on update actions) vs ones we don't know about
class Unset(str): ...


UNSET = Unset("__unset__")


#
# Image related
#
type Width = int
type Height = int
type ImageDimensions = tuple[Width, Height]
type Point = tuple[int, int]


class Dimension(Enum):
    WIDTH = "w"
    HEIGHT = "h"


class RatioApproach(Enum):
    CROP = "c"
    FILL = "f"
    SQUASH = "s"


class FocusPointOption(Enum):
    BOTTOM_LEFT = 0
    BOTTOM_MIDDLE = 1
    BOTTOM_RIGHT = 2
    MIDDLE_LEFT = 3
    CENTER = 4
    MIDDLE_RIGHT = 5
    TOP_LEFT = 6
    TOP_MIDDLE = 7
    TOP_RIGHT = 8


class ImageStandardSizes(Enum):
    ORIGINAL = 0
    MAIN = 512
    SMALL = 216
    THUMBNAIL = 40

    @property
    def dimensions(self) -> ImageDimensions:
        return (self.value, self.value)

    @property
    def prefix(self) -> str:
        if self.value == 0:
            return ""
        return f"{self.value}x{self.value}"
