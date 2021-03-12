import asyncio
import uuid
from typing import List, Dict

import httpx
import time
from urllib.parse import urljoin as uj
import socket

from .models import Property, Permission, ObjectType

PROTOCOL_VERSION = '3.1'
DATA_FORMAT = 'json'
UUID = str(uuid.uuid1())
USER = 'Guest'


class SessionError(Exception):
    pass


class DBInformationError(Exception):
    pass

class SetPropertyError(Exception):
    pass


DEFAULT_HEADERS = {'Host': 'PhaseOne.local.'}


class DB(object):

    def __init__(self, host: str, capture_only: bool, object_id: str) -> None:
        self.capture_only = int(capture_only)
        self.host = host
        self.client = httpx.Client(base_url=self.host, headers=DEFAULT_HEADERS)
        self.session_id = asyncio.run(get_session(self.client, self.capture_only))
        self.properties: Dict[Property] = None
        self.object_id = f"{object_id}-3"
        self.object_type = ObjectType.camera.value

    def refresh_session_id(self):
        self.session_id = asyncio.run(get_session(self.client, self.capture_only))

    def refresh_db_properties(self):
        try:
            properties = asyncio.run(list_properties(self.client, self.session_id))
        except ValueError:
            self.refresh_session_id()
            properties = asyncio.run(list_properties(self.client, self.session_id))
        self.properties = {prop.name: prop for prop in properties}

    def set_property(self, property: str, value: str):
        try:
            trg_prop: Property = self.properties[property]
            if trg_prop.permissions != filter.RW.value:
                raise SetPropertyError(f"Property {property} permissions not set to {filter.RW.value}")
            asyncio.run(set_property(self.client, self.session_id, property,
            value, self.object_id, trg_prop.prop_id, self.object_type))
        except KeyError:
            raise KeyError(f"Property {property} not found in self.properties")


async def get_session(client: httpx.Client, capture_only: int = 1, retry: bool = True) -> int:
    """
    Creates a new session on the digital back. Use the returned ID for all sessionID query params.
    :param retry: Retry getting a session
    :param capture_only: Only allow capture controls
    :param host: The hostname (with port!) of the digital back.
    :return: The sessionID integer
    """
    path = '/connectToService'
    params = {
        'timestamp': round(time.time()),
        'protocolVersion': PROTOCOL_VERSION,
        'deviceName': socket.gethostname(),
        'deviceIdentifier': UUID,
        'dataFormat': DATA_FORMAT,
        'captureControlsOnly': 1 if capture_only else 0
    }
    auth = (USER, '')
    r: httpx.Response = await client.get(path, params=params, auth=auth)
    try:
        return int(r.text)
    except ValueError:
        if retry:
            await asyncio.sleep(2)
            return await get_session(client, capture_only=capture_only, retry=False)
        raise SessionError(f"Could not get session integer from {path}: {r.text}")


async def get_db_information(client: httpx.Client, session_id: int) -> dict:
    path = '/getServerChanges'
    params = {
        'sessionID': session_id
    }
    r: httpx.Response = await client.get(path, params=params, timeout=10)
    try:
        return r.json()
    except ValueError:
        raise DBInformationError("Could not get information JSON from Digital Back.")


async def list_properties(client: httpx.Client, session_id: int, object_id: str) -> List[Property]:
    data = await get_db_information(client, session_id)
    props = []
    try:
        for obj in data['objects']:
            if obj.get('kObjectKey_ObjectID') == object_id:
                for prop in obj['kObjectKey_Properties']:
                    props.append(Property(
                        name=prop['kObjectProperty_PropertyName'],
                        prop_id=prop['kObjectProperty_PropertyID'],
                        permissions=prop['kObjectProperty_Permissions'],
                        value=prop['kObjectProperty_CurrentValue'],
                        possible_values=prop['kObjectProperty_Values'].split('#') if prop['kObjectProperty_Values'] else ''
                    ))
                return props
    except KeyError:
        raise DBInformationError("Error creating properties from digital back json.")


async def connect_get_properties(client: httpx.Client) -> List[Property]:
    session = await get_session(client, capture_only=1)
    return await list_properties(client, session)


async def filter_props(props: List[Property], filter: Permission):
    return [i for i in props if i.permissions == filter.RW.value]


async def set_property(client: httpx.Client, session_id: int, prop: Property, 
        value: str, objectID: str, propertyID: str, objectType: str):
    path = '/setProperty'
    params = {
        'sessionID': session_id,
        'propertyValue': value,
        'objectID': objectID,
        'propertyID': propertyID,
        'objectType': objectType
    }
    r: httpx.Response = await client.get(path, params=params)
    if r.status_code != 200:
        raise SetPropertyError(f"Unable to set the property {prop} on host {client.base_url}!")


# if __name__ == '__main__':
#     data = asyncio.run(connect_get_properties('http://PhaseOne.local:3300'))
#     print(data)