from enum import Enum, StrEnum
from typing import Literal

from PIL import Image


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


def resize_image(
    original_filename: str,
    target_filename: str,
    target_dimensions: ImageDimensions,
    focus_point: FocusPointOption | Point = FocusPointOption.CENTER,
    approach: RatioApproach = RatioApproach.CROP,
):
    if approach != RatioApproach.CROP:
        # theoretically FILL and SQUASH are options but not ones worth implementing for profile photos
        raise NotImplementedError()

    image: Image.Image = Image.open(original_filename)
    original_dimensions = image.size
    orig_width, orig_height = original_dimensions
    tgt_width, tgt_height = target_dimensions

    if tgt_width > orig_width or tgt_height > orig_height:
        # upscaling isn't going to look great
        raise NotImplementedError()

    dimension, amount = get_crop_dimensions(
        original_dimensions=original_dimensions,
        target_dimensions=target_dimensions,
    )
    if dimension is not None:
        image = image.crop(
            get_crop_values(
                original_dimensions=original_dimensions,
                dimension=dimension,
                amount_to_remove=amount,  # type: ignore
                focus_point=focus_point,
            )
        )

    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")

    image = image.resize(target_dimensions, Image.Resampling.BICUBIC)

    image.save(target_filename)


def get_crop_dimensions(
    original_dimensions: ImageDimensions,
    target_dimensions: ImageDimensions,
) -> (
    tuple[Literal[Dimension.WIDTH], int]
    | tuple[Literal[Dimension.HEIGHT], int]
    | tuple[None, None]
):
    orig_width, orig_height = original_dimensions
    tgt_width, tgt_height = target_dimensions
    original_ratio = orig_width / orig_height
    target_ratio = tgt_width / tgt_height

    if original_ratio > target_ratio:
        # original aspect ratio is shorter or wider than target ratio; width needs to br cropped
        crop_width = orig_width - round((orig_height / tgt_height) * tgt_width)
        return (Dimension.WIDTH, crop_width)

    if original_ratio < target_ratio:
        # original aspect ratio is narrower or taller than target ratio; height needs to be cropped
        crop_height = orig_height - round((orig_width / tgt_width) * tgt_height)
        return (Dimension.HEIGHT, crop_height)

    # No crop needed
    return (None, None)


def get_crop_values(
    original_dimensions: ImageDimensions,
    dimension: Dimension,
    amount_to_remove: int,
    focus_point: Point | FocusPointOption,
):
    orig_width, orig_height = original_dimensions
    left = 0
    top = 0
    right = orig_width
    bottom = orig_height
    if dimension == Dimension.WIDTH:
        if focus_point in (
            FocusPointOption.BOTTOM_LEFT,
            FocusPointOption.MIDDLE_LEFT,
            FocusPointOption.TOP_LEFT,
        ):
            right = orig_width - amount_to_remove
        elif focus_point in (
            FocusPointOption.BOTTOM_MIDDLE,
            FocusPointOption.CENTER,
            FocusPointOption.TOP_MIDDLE,
        ):
            left = int(amount_to_remove / 2)
            right = orig_width - int(amount_to_remove / 2)
        elif focus_point in (
            FocusPointOption.BOTTOM_RIGHT,
            FocusPointOption.MIDDLE_RIGHT,
            FocusPointOption.TOP_RIGHT,
        ):
            left = amount_to_remove
        elif type(focus_point) == Point:
            x, _ = focus_point  # type: ignore
            amount_to_keep = orig_width - amount_to_remove
            left = min(int(x - (amount_to_keep / 2)), 0)
            right = orig_width - (amount_to_remove - left)
    elif dimension == Dimension.HEIGHT:
        if focus_point in (
            FocusPointOption.BOTTOM_LEFT,
            FocusPointOption.BOTTOM_MIDDLE,
            FocusPointOption.BOTTOM_RIGHT,
        ):
            top = amount_to_remove
        elif focus_point in (
            FocusPointOption.MIDDLE_LEFT,
            FocusPointOption.CENTER,
            FocusPointOption.MIDDLE_RIGHT,
        ):
            top = int(amount_to_remove / 2)
            bottom = orig_height - int(amount_to_remove / 2)
        elif focus_point in (
            FocusPointOption.TOP_LEFT,
            FocusPointOption.TOP_MIDDLE,
            FocusPointOption.TOP_RIGHT,
        ):
            bottom = orig_height - amount_to_remove
        elif type(focus_point) == Point:
            _, y = focus_point  # type: ignore
            amount_to_keep = orig_height - amount_to_remove
            top = min(int(y - (amount_to_keep / 2)), 0)
            bottom = orig_height - (amount_to_remove - bottom)
    return (left, top, right, bottom)
