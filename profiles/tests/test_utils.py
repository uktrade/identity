import pytest

from profiles import utils


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
    assert False

def test_get_filename_for_image_size():
    assert False

def test_get_crop_values():
    assert False

def test_get_crop_dimensions():
    assert False

def test_resize_image():
    assert False
