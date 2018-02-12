import falcon
from falcon import testing
import json
import pytest
from datalad.api import Dataset

from datalad_server.app import create_app
from .dataset_fixtures import *


def test_get_file(client):
    ds_id = 'ds000001'
    result = client.simulate_get(
        '/datasets/{}/files/dataset_description.json'.format(ds_id), file_wrapper=FileWrapper)
    content_len = int(result.headers['content-length'])
    assert content_len == len(result.content)
    assert json.loads(result.content)['BIDSVersion'] == '1.0.2'


def test_get_missing_file(client):
    ds_id = 'ds000001'
    result = client.simulate_get(
        '/datasets/{}/files/thisdoesnotexist.json'.format(ds_id), file_wrapper=FileWrapper)
    assert result.status == falcon.HTTP_NOT_FOUND


def test_add_file(client, annex_path):
    ds_id = 'ds000001'
    file_data = 'Test dataset README'
    response = client.simulate_post(
        '/datasets/{}/files/README'.format(ds_id), body=file_data)
    assert response.status == falcon.HTTP_OK
    # Load the dataset to check for this file
    ds_obj = Dataset(str(annex_path.join(ds_id)))
    test_files = ds_obj.get('README')
    assert test_files
    assert len(test_files) == 1
    with open(test_files.pop()['path']) as f:
        assert f.read() == file_data


def test_add_existing_file(client):
    ds_id = 'ds000001'
    file_data = 'should not update'
    response = client.simulate_post(
        '/datasets/{}/files/dataset_description.json'.format(ds_id), body=file_data)
    assert response.status == falcon.HTTP_CONFLICT


def test_update_file(client, annex_path):
    ds_id = 'ds000001'
    file_data = 'Test dataset LICENSE'
    # First post a file
    response = client.simulate_post(
        '/datasets/{}/files/LICENSE'.format(ds_id), body=file_data)
    assert response.status == falcon.HTTP_OK
    # Then update it
    file_data = 'New test LICENSE'
    response = client.simulate_put(
        '/datasets/{}/files/LICENSE'.format(ds_id), body=file_data)
    assert response.status == falcon.HTTP_OK
    # Load the dataset to check for the updated file
    ds_obj = Dataset(str(annex_path.join(ds_id)))
    test_files = ds_obj.get('LICENSE')
    assert test_files
    assert len(test_files) == 1
    with open(test_files.pop()['path']) as f:
        assert f.read() == file_data