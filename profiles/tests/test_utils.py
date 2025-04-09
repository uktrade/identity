from ctypes import util
import pytest

from profiles import types, utils


pytestmark = pytest.mark.django_db

def test_get_file_from_storages():
    assert False

def test_write_file_to_storages():
    assert False

def test_get_storage_instance(mocker):
    with pytest.raises(KeyError):
        utils.get_storage_instance("nonexistent_backend")

    mock_storages = mocker.patch("profiles.utils.storages")
    utils.get_storage_instance("existing_backend")
    mock_storages.create_storage.assert_called_once_with(mock_storages.backends["existing_backend"])

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

    assert utils.get_filename_for_image_size(path, "and/sized") == "my/deeply/nested/and/sized/file.pdf"

def test_get_crop_values():
    orig_dimensions = (1000, 1000)
    amt = 100

    #
    # Crop into the WIDTH
    #
    dimension = types.Dimension.WIDTH
    focus = types.FocusPointOption.CENTER
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (50, 0, 950, 1000)

    focus = types.FocusPointOption.BOTTOM_MIDDLE
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (50, 0, 950, 1000)

    focus = types.FocusPointOption.TOP_MIDDLE
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (50, 0, 950, 1000)

    focus = types.FocusPointOption.TOP_LEFT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 900, 1000)

    focus = types.FocusPointOption.MIDDLE_LEFT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 900, 1000)

    focus = types.FocusPointOption.BOTTOM_LEFT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 900, 1000)

    focus = types.FocusPointOption.TOP_RIGHT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (100, 0, 1000, 1000)

    focus = types.FocusPointOption.MIDDLE_RIGHT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (100, 0, 1000, 1000)

    focus = types.FocusPointOption.BOTTOM_RIGHT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (100, 0, 1000, 1000)

    #
    # Crop into the HEIGHT
    #
    dimension = types.Dimension.HEIGHT
    focus = types.FocusPointOption.CENTER
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 50, 1000, 950)

    focus = types.FocusPointOption.BOTTOM_MIDDLE
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 100, 1000, 1000)

    focus = types.FocusPointOption.TOP_MIDDLE
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 1000, 900)

    focus = types.FocusPointOption.TOP_LEFT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 1000, 900)

    focus = types.FocusPointOption.MIDDLE_LEFT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 50, 1000, 950)

    focus = types.FocusPointOption.BOTTOM_LEFT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 100, 1000, 1000)

    focus = types.FocusPointOption.TOP_RIGHT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 1000, 900)

    focus = types.FocusPointOption.MIDDLE_RIGHT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 50, 1000, 950)

    focus = types.FocusPointOption.BOTTOM_RIGHT
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 100, 1000, 1000)

    #
    # Custom focus
    #
    dimension = types.Dimension.HEIGHT
    focus = (500, 500)  # type:ignore
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 50, 1000, 950)

    focus = (450, 450)  # type:ignore
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 1000, 900)

    focus = (750, 750)  # type:ignore
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 100, 1000, 1000)

    dimension = types.Dimension.WIDTH
    focus = (500, 500)  # type:ignore
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (50, 0, 950, 1000)

    focus = (450, 450)  # type:ignore
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (0, 0, 900, 1000)

    focus = (750, 750)  # type:ignore
    assert utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,) == (100, 0, 1000, 1000)

    focus = (1200, 1200)  # type: ignore
    with pytest.raises(ValueError):
        utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,)

    dimension = types.Dimension.HEIGHT
    with pytest.raises(ValueError):
        utils.get_crop_values(original_dimensions=orig_dimensions, dimension=dimension, amount_to_remove=amt, focus_point=focus,)

def test_get_crop_dimensions():
    orig_dimensions = (100, 300)
    tgt_dimensions = (100, 300)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (None, None)

    tgt_dimensions = (50, 150)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (None, None)

    tgt_dimensions = (200, 600)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (None, None)

    tgt_dimensions = (100, 600)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (types.Dimension.WIDTH, 50)

    tgt_dimensions = (300, 600)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (types.Dimension.HEIGHT, 100)

    orig_dimensions = (300, 100)

    tgt_dimensions = (100, 600)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (types.Dimension.WIDTH, 283)

    tgt_dimensions = (300, 600)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (types.Dimension.WIDTH, 250)

    tgt_dimensions = (600, 600)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (types.Dimension.WIDTH, 200)

    tgt_dimensions = (600, 300)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (types.Dimension.WIDTH, 100)

    tgt_dimensions = (1200, 300)
    assert utils.get_crop_dimensions(original_dimensions=orig_dimensions, target_dimensions=tgt_dimensions,) == (types.Dimension.HEIGHT, 25)


def test_resize_image():
    assert False

def test_get_or_create_sized_image():
    assert False
