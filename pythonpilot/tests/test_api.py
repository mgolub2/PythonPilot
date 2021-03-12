import pythonpilot.api.api as api
import pytest
import os

OBJ_ID = os.environ['PHASEONE_DB_OBJ'] 


@pytest.mark.asyncio
@pytest.mark.dependency()
async def test_get_session_id(client):
    session = await api.get_session(client)
    assert session
    pytest.session = session


@pytest.mark.asyncio
@pytest.mark.dependency(depends=['test_get_session_id'])
async def test_get_db_info(client):
    data = await api.get_db_information(client, pytest.session)
    assert data


@pytest.mark.asyncio
@pytest.mark.dependency(depends=['test_get_session_id'])
async def test_list_properties(client):
    data = await api.list_properties(client, pytest.session, OBJ_ID)
    assert data


@pytest.mark.asyncio
@pytest.mark.dependency(depends=['test_get_session_id'])
async def test_filter_props_rw(client):
    data = await api.list_properties(client, pytest.session, OBJ_ID)
    rw_props = await api.filter_props(data, filter=api.Permission.RW)
    assert len(data) > len(rw_props) and rw_props
    with open('rw.txt', 'w') as f:
        for p in rw_props:
            f.write(f'{p}\n')


@pytest.mark.asyncio
@pytest.mark.dependency(depends=['test_get_session_id'])
async def test_set_property(client):
    """
    Save current iso, change it to max allowed,
    check if it changed, then set it back to normal
    Property(value='1600', permissions='rw', name='ISO', prop_id='kCameraProperty_ExposureISO', possible_values='200#400#800#1600#3200#6400#12800#25600#51200#')
    """
    data = await api.list_properties(client, pytest.session, OBJ_ID)
    rw_props = await api.filter_props(data, filter=api.Permission.RW)
    iso = next(filter(lambda x: x.name == 'ISO', rw_props))
    max_iso = iso.possible_values[-1]
    await api.set_property(client, pytest.session, iso.name, 
        max_iso, OBJ_ID, 'kCameraProperty_ExposureISO', api.ObjectType.camera.value)
    data = await api.list_properties(client, pytest.session, OBJ_ID)
    iso_new = next(filter(lambda x: x.name == 'ISO', data)) 
    assert iso_new.possible_values[-1] == max_iso
    await api.set_property(client, pytest.session, iso.name, 
        iso.value, OBJ_ID, 'kCameraProperty_ExposureISO', api.ObjectType.camera.value)
    data = await api.list_properties(client, pytest.session, OBJ_ID)
    iso_reset = next(filter(lambda x: x.name == 'ISO', data))
    assert iso_reset.value == iso.value