from PIL import Image

type ImageDimensions = tuple[float, float]


def resize_image(
    original_filename: str,
    target_filename: str,
    target_dimensions: ImageDimensions,
    original_dimensions: ImageDimensions | None = None,
    approach="CROP",
):
    image = Image.open(original_filename)

    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")

    if original_dimensions is None:
        original_dimensions = image.size

    orig_width, orig_height = original_dimensions
    tgt_width, tgt_height = target_dimensions
    original_ratio = orig_width / orig_height
    target_ratio = tgt_width / tgt_height

    if approach == "CROP" and original_ratio > target_ratio:
        # photo aspect is wider than destination ratio
        width = int(round(tgt_height * original_ratio))

        image = image.resize((width, tgt_height), Image.Resampling.BICUBIC)
        l = int(round((width - tgt_width) / 2.0))
        image = image.crop((l, 0, l + tgt_width, tgt_height))
    elif approach == "CROP" and original_ratio < target_ratio:
        # photo aspect is taller than destination ratio
        height = int(round(tgt_width / original_ratio))

        image = image.resize((tgt_width, height), Image.Resampling.BICUBIC)
        t = int(round((height - tgt_height) / 2.0))
        image = image.crop((0, t, tgt_width, t + tgt_height))
    else:
        # photo aspect matches the destination ratio
        image = image.resize(target_dimensions, Image.Resampling.BICUBIC)

    image.save(target_filename)
