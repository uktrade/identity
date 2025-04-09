import os
from typing import Literal

from django.core.files.storage import storages
from PIL import Image, ImageOps

from profiles.types import (
    Dimension,
    FocusPointOption,
    ImageDimensions,
    ImageStandardSizes,
    Point,
    RatioApproach,
)


def get_or_create_sized_image(
    original_filename: str, size: ImageDimensions, prefix: str
):
    filename = get_filename_for_image_size(original_filename, prefix)

    # if not profile.photo.storage.exists(filename):
    #     resize_image(profile.photo.name, filename, size,)
    # @TODO need to edit this all to use storages or boto to talk to S3


# @TODO maybe dont do actual file operations in here so we can more easily use storages - see https://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
def resize_image(
    original_filename: str,
    target_filename: str,
    target_dimensions: ImageDimensions,
    focus_point: FocusPointOption | Point = FocusPointOption.CENTER,
    approach: RatioApproach = RatioApproach.CROP,
):
    # @TODO maybe get_file_from_storages?
    image: Image.Image = Image.open(original_filename)
    original_dimensions = image.size
    orig_width, orig_height = original_dimensions
    tgt_width, tgt_height = target_dimensions

    if tgt_width > orig_width or tgt_height > orig_height:
        # upscaling isn't going to look great, better to have a minimum ORIGINAL size
        raise NotImplementedError()

    if approach != RatioApproach.CROP:
        # only CROP seems worth implementing for profile photos
        raise NotImplementedError()

    # ensure image right way up and right colour space
    image = ImageOps.exif_transpose(image)  # type: ignore
    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")

    # crop if needed
    dimension, amount = get_crop_dimensions(
        original_dimensions=original_dimensions,
        target_dimensions=target_dimensions,
    )
    if dimension is not None and amount is not None:
        image = image.crop(
            get_crop_values(
                original_dimensions=original_dimensions,
                dimension=dimension,
                amount_to_remove=amount,
                focus_point=focus_point,
            )
        )

    image = image.resize(target_dimensions, Image.Resampling.BICUBIC)
    # @TODO maybe write_file_to_storages ?
    image.save(target_filename)


def get_crop_dimensions(
    original_dimensions: ImageDimensions,
    target_dimensions: ImageDimensions,
) -> tuple[Dimension, int] | tuple[None, None]:
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
        else:
            if type(focus_point) not in (Point, tuple, ):
                raise TypeError("focus_point is not FocusPointOption or Point")

            x, _ = focus_point  # type: ignore
            if x > orig_width:
                raise ValueError("Focus point value must be within image dimensions")

            amount_to_keep = orig_width - amount_to_remove
            midpoint = int(amount_to_keep / 2)
            left = x - midpoint
            if left <= 0:
                left = 0
            elif (left + amount_to_keep) > orig_height:
                left = amount_to_remove
            right = orig_height - (amount_to_remove - left)
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
        else:
            if type(focus_point) not in (Point, tuple, ):
                raise TypeError("focus_point is not FocusPointOption or Point")

            _, y = focus_point  # type: ignore
            if y > orig_height:
                raise ValueError("Focus point value must be within image dimensions")

            amount_to_keep = orig_height - amount_to_remove
            midpoint = int(amount_to_keep / 2)
            top = y - midpoint
            if top <= 0:
                top = 0
            elif (top + amount_to_keep) > orig_height:
                top = amount_to_remove
            bottom = orig_height - (amount_to_remove - top)
    return (left, top, right, bottom)


def get_filename_for_image_size(original_filename: str, prefix: str):
    head, tail = os.path.split(original_filename)
    return f"{head}/{prefix}/{tail}"


def get_dimensions_and_prefix_from_standard_size(
    standard_size: ImageStandardSizes,
) -> tuple[ImageDimensions, str]:
    return (standard_size.dimensions, standard_size.prefix)


def get_storage_instance(backend:str="default"):
    return storages.create_storage(storages.backends[backend])


def get_file_from_storages(filename):
    # @TODO get file if exists, compatible with django-storages but avoiding FileField
    raise NotImplementedError()


def write_file_to_storages(filename):
    # @TODO write file, compatible with django-storages but avoiding FileField
    raise NotImplementedError()
