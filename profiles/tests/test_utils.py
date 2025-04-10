from re import A
from unittest.mock import call

import pytest

from profiles import types, utils


pytestmark = pytest.mark.django_db


def test_open_file_from_storages(mocker):
    mock_s = mocker.Mock()
    mock_s.open.return_value = "a-file"
    mock_get_storages = mocker.patch(
        "profiles.utils.get_storage_instance", return_value=mock_s
    )

    file = utils.open_file_from_storages("file_name")
    assert file == "a-file"
    mock_get_storages.assert_called_once()
    mock_s.open.assert_called_once_with("file_name", mode="rb")


def test_save_file_to_storages(mocker):
    mock_s = mocker.Mock()
    mock_s.save.return_value = "a-file-name"
    mock_get_storages = mocker.patch(
        "profiles.utils.get_storage_instance", return_value=mock_s
    )
    file = mocker.Mock()

    filename = utils.save_file_to_storages("file_name", content=file)
    assert filename == "a-file-name"
    mock_get_storages.assert_called_once()
    mock_s.save.assert_called


def test_get_storage_instance(mocker):
    with pytest.raises(KeyError):
        utils.get_storage_instance("nonexistent_backend")

    mock_storages = mocker.patch("profiles.utils.storages")
    utils.get_storage_instance("existing_backend")
    mock_storages.create_storage.assert_called_once_with(
        mock_storages.backends["existing_backend"]
    )

    utils.get_storage_instance()
    mock_storages.create_storage.assert_called_with(mock_storages.backends["default"])


def test_get_dimensions_and_prefix_from_standard_size():
    assert len(types.ImageStandardSizes) == 4
    for size in types.ImageStandardSizes:
        dimensions, prefix = utils.get_dimensions_and_prefix_from_standard_size(size)
        assert dimensions == size.dimensions
        assert prefix == size.prefix


def test_get_filename_for_image_size():
    path = "my/deeply/nested/file.pdf"

    assert (
        utils.get_filename_for_image_size(path, "and/sized")
        == "my/deeply/nested/and/sized/file.pdf"
    )


def test_get_crop_values():
    orig_dimensions = (1000, 1000)
    amt = 100

    #
    # Crop into the WIDTH
    #
    dimension = types.Dimension.WIDTH
    focus = types.FocusPointOption.CENTER
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (50, 0, 950, 1000)

    focus = types.FocusPointOption.BOTTOM_MIDDLE
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (50, 0, 950, 1000)

    focus = types.FocusPointOption.TOP_MIDDLE
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (50, 0, 950, 1000)

    focus = types.FocusPointOption.TOP_LEFT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 900, 1000)

    focus = types.FocusPointOption.MIDDLE_LEFT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 900, 1000)

    focus = types.FocusPointOption.BOTTOM_LEFT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 900, 1000)

    focus = types.FocusPointOption.TOP_RIGHT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (100, 0, 1000, 1000)

    focus = types.FocusPointOption.MIDDLE_RIGHT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (100, 0, 1000, 1000)

    focus = types.FocusPointOption.BOTTOM_RIGHT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (100, 0, 1000, 1000)

    #
    # Crop into the HEIGHT
    #
    dimension = types.Dimension.HEIGHT
    focus = types.FocusPointOption.CENTER
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 50, 1000, 950)

    focus = types.FocusPointOption.BOTTOM_MIDDLE
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 100, 1000, 1000)

    focus = types.FocusPointOption.TOP_MIDDLE
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 1000, 900)

    focus = types.FocusPointOption.TOP_LEFT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 1000, 900)

    focus = types.FocusPointOption.MIDDLE_LEFT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 50, 1000, 950)

    focus = types.FocusPointOption.BOTTOM_LEFT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 100, 1000, 1000)

    focus = types.FocusPointOption.TOP_RIGHT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 1000, 900)

    focus = types.FocusPointOption.MIDDLE_RIGHT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 50, 1000, 950)

    focus = types.FocusPointOption.BOTTOM_RIGHT
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 100, 1000, 1000)

    #
    # Custom focus
    #
    dimension = types.Dimension.HEIGHT
    focus = (500, 500)  # type:ignore
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 50, 1000, 950)

    focus = (450, 450)  # type:ignore
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 1000, 900)

    focus = (750, 750)  # type:ignore
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 100, 1000, 1000)

    dimension = types.Dimension.WIDTH
    focus = (500, 500)  # type:ignore
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (50, 0, 950, 1000)

    focus = (450, 450)  # type:ignore
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (0, 0, 900, 1000)

    focus = (750, 750)  # type:ignore
    assert utils.get_crop_values(
        original_dimensions=orig_dimensions,
        dimension=dimension,
        amount_to_remove=amt,
        focus_point=focus,
    ) == (100, 0, 1000, 1000)

    focus = (1200, 1200)  # type: ignore
    with pytest.raises(ValueError):
        utils.get_crop_values(
            original_dimensions=orig_dimensions,
            dimension=dimension,
            amount_to_remove=amt,
            focus_point=focus,
        )

    dimension = types.Dimension.HEIGHT
    with pytest.raises(ValueError):
        utils.get_crop_values(
            original_dimensions=orig_dimensions,
            dimension=dimension,
            amount_to_remove=amt,
            focus_point=focus,
        )


def test_get_crop_dimensions():
    orig_dimensions = (100, 300)
    tgt_dimensions = (100, 300)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (None, None)

    tgt_dimensions = (50, 150)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (None, None)

    tgt_dimensions = (200, 600)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (None, None)

    tgt_dimensions = (100, 600)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (types.Dimension.WIDTH, 50)

    tgt_dimensions = (300, 600)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (types.Dimension.HEIGHT, 100)

    orig_dimensions = (300, 100)

    tgt_dimensions = (100, 600)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (types.Dimension.WIDTH, 283)

    tgt_dimensions = (300, 600)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (types.Dimension.WIDTH, 250)

    tgt_dimensions = (600, 600)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (types.Dimension.WIDTH, 200)

    tgt_dimensions = (600, 300)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (types.Dimension.WIDTH, 100)

    tgt_dimensions = (1200, 300)
    assert utils.get_crop_dimensions(
        original_dimensions=orig_dimensions,
        target_dimensions=tgt_dimensions,
    ) == (types.Dimension.HEIGHT, 25)


def test_resize_image(mocker):
    PILImage = mocker.patch("profiles.utils.Image")
    PILImageOps = mocker.patch("profiles.utils.ImageOps")
    file = mocker.Mock()
    img = mocker.Mock()
    img.mode = "HSB"
    PILImage.open.return_value = img
    PILImageOps.exif_transpose.return_value = img
    img.convert.return_value = img
    img.crop.return_value = img

    approach = types.RatioApproach.CROP
    img.size = (100, 100)
    with pytest.raises(NotImplementedError):
        utils.resize_image(
            file=file,
            target_dimensions=(1000, 1000),
            focus_point=types.FocusPointOption.CENTER,
            approach=approach,
        )
    PILImage.open.assert_called_once_with(file)

    img.size = (100, 2000)
    with pytest.raises(NotImplementedError):
        utils.resize_image(
            file=img,
            target_dimensions=(1000, 1000),
            focus_point=types.FocusPointOption.CENTER,
            approach=approach,
        )

    img.size = (2000, 2000)
    with pytest.raises(NotImplementedError):
        utils.resize_image(
            file=img,
            target_dimensions=(1000, 1000),
            focus_point=types.FocusPointOption.CENTER,
            approach=types.RatioApproach.FILL,
        )

    with pytest.raises(NotImplementedError):
        utils.resize_image(
            file=img,
            target_dimensions=(1000, 1000),
            focus_point=types.FocusPointOption.CENTER,
            approach=types.RatioApproach.SQUASH,
        )

    mock_crop_dimensions = mocker.patch(
        "profiles.utils.get_crop_dimensions", return_value=("-dimension-", "-amount-")
    )
    mock_crop_values = mocker.patch(
        "profiles.utils.get_crop_values", return_value="crop-vals"
    )
    output = utils.resize_image(
        file=img,
        target_dimensions=(1000, 1000),
        focus_point=types.FocusPointOption.CENTER,
        approach=approach,
    )
    PILImageOps.exif_transpose.assert_called_once_with(img)
    img.convert.assert_called_once_with("RGB")
    mock_crop_dimensions.assert_called_once_with(
        original_dimensions=(2000, 2000), target_dimensions=(1000, 1000)
    )
    mock_crop_values.assert_called_once_with(
        original_dimensions=(2000, 2000),
        dimension="-dimension-",
        amount_to_remove="-amount-",
        focus_point=types.FocusPointOption.CENTER,
    )
    img.crop.assert_called_once_with("crop-vals")
    img.resize.assert_called_once_with((1000, 1000), PILImage.Resampling.BICUBIC)
    assert output == img.resize.return_value

    img.mode = "L"
    img.convert.reset_mock()
    assert (
        utils.resize_image(
            file=img,
            target_dimensions=(1000, 1000),
            focus_point=types.FocusPointOption.CENTER,
            approach=approach,
        )
        == img.resize.return_value
    )
    img.convert.assert_not_called()

    img.mode = "RGB"
    img.convert.reset_mock()
    assert (
        utils.resize_image(
            file=img,
            target_dimensions=(1000, 1000),
            focus_point=types.FocusPointOption.CENTER,
            approach=approach,
        )
        == img.resize.return_value
    )
    img.convert.assert_not_called()

    mock_crop_values.reset_mock()
    assert (
        utils.resize_image(
            file=img,
            target_dimensions=(1000, 1000),
            focus_point=(200, 200),
            approach=approach,
        )
        == img.resize.return_value
    )
    mock_crop_values.assert_called_once_with(
        original_dimensions=(2000, 2000),
        dimension="-dimension-",
        amount_to_remove="-amount-",
        focus_point=(200, 200),
    )

    mock_crop_dimensions.return_value = (None, None)
    img.crop.reset_mock()
    assert (
        utils.resize_image(
            file=img,
            target_dimensions=(1000, 1000),
            focus_point=types.FocusPointOption.CENTER,
            approach=approach,
        )
        == img.resize.return_value
    )
    img.crop.assert_not_called()


def test_get_or_create_sized_image(mocker):
    file = mocker.Mock()
    sized_file = mocker.Mock()
    img = mocker.Mock()
    get_filename = mocker.patch(
        "profiles.utils.get_filename_for_image_size", return_value="--filename--"
    )
    open_file = mocker.patch(
        "profiles.utils.open_file_from_storages", return_value=file
    )
    resize_img = mocker.patch("profiles.utils.resize_image", return_value=img)
    BytesIO = mocker.patch("profiles.utils.BytesIO", return_value=sized_file)
    save_file = mocker.patch(
        "profiles.utils.save_file_to_storages", return_value=sized_file
    )

    assert (
        utils.get_or_create_sized_image(
            "orig",
            (350, 350),
            "-prefix-",
        )
        == file
    )
    get_filename.assert_called_once_with("orig", "-prefix-")
    open_file.assert_called_once_with("--filename--")
    resize_img.assert_not_called()
    save_file.assert_not_called()

    open_file.side_effect = [
        FileNotFoundError,  # uncreated sizxed file
        file,  # oringinal file
        sized_file,  # newly created sized file
    ]
    open_file.reset_mock()
    assert (
        utils.get_or_create_sized_image(
            "orig",
            (350, 350),
            "-prefix-",
        )
        == sized_file
    )
    open_file.assert_has_calls(
        [
            call("--filename--"),
            call("orig"),
        ]
    )
    resize_img.assert_called_once_with(file=file, target_dimensions=(350, 350))
    img.save.assert_called_once_with(sized_file, format="JPEG")
    save_file.assert_called_once_with("--filename--", sized_file)

    # if original file is not found error bubbles up
    open_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        utils.get_or_create_sized_image(
            "orig",
            (350, 350),
            "-prefix-",
        )
