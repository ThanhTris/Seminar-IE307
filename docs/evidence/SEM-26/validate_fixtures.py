"""Kiểm fixture SEM-26 trong tài liệu; không gọi network hay chạy server/Android."""

from datetime import datetime
import json
from pathlib import Path
import re
from uuid import UUID

ROOT = Path(__file__).resolve().parents[3]
API = ROOT / 'docs/API.md'
EVENTS = ROOT / 'docs/EVENT_SCHEMA.md'
VERSION = '2.0.0'
MAX_VERSION = 2**53 - 1
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
FIELDS = {
    'schema_version', 'event_id', 'event_type', 'origin', 'run_id', 'mode',
    'source', 'device_alias', 'timestamp_utc', 'elapsed_realtime_ms',
    'boot_session_id', 'data_version', 'cached_version', 'version_hint',
    'request_id', 'work_id', 'work_attempt', 'network_call_id', 'update_id',
    'signal_ids', 'send_attempt_id', 'message_id', 'ttl_ms', 'http_status',
    'provider_code', 'outcome', 'reason',
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f'Duplicate JSON key: {key}'
        result[key] = value
    return result


def parse_json(value):
    return json.loads(value, object_pairs_hook=unique_object)


def uuid_string(value, *, v4=False):
    assert isinstance(value, str)
    parsed = UUID(value)
    assert str(parsed) == value.lower()
    if v4:
        assert parsed.version == 4


def uint(value):
    return type(value) is int and 0 <= value <= MAX_VERSION


def assert_snapshot(snapshot):
    assert snapshot['api_version'] == VERSION and uint(snapshot['version'])
    assert snapshot['last_modified_utc'].endswith('Z')
    datetime.fromisoformat(snapshot['last_modified_utc'].replace('Z', '+00:00'))
    assert isinstance(snapshot['items'], list) and len(snapshot['items']) <= 100
    ids = set()
    versions = []
    for item in snapshot['items']:
        assert set(item) == {'id', 'title', 'body', 'version'}
        assert ID.fullmatch(item['id']) and item['id'] not in ids
        assert isinstance(item['title'], str) and item['title'].strip()
        assert 1 <= len(item['title']) <= 256
        assert isinstance(item['body'], str) and len(item['body']) <= 4096
        assert type(item['version']) is int and 1 <= item['version'] <= snapshot['version']
        versions.append(item['version'])
        ids.add(item['id'])
    assert versions == sorted(set(versions), reverse=True)
    if snapshot['version'] == 0:
        assert not versions
    else:
        assert versions and versions[0] == snapshot['version']


def assert_event(event):
    assert set(event) == FIELDS
    assert event['schema_version'] == VERSION
    uuid_string(event['event_id'], v4=True)
    for key in ('run_id', 'device_alias'):
        assert isinstance(event[key], str) and ID.fullmatch(event[key])
    for key in ('boot_session_id', 'request_id', 'update_id', 'send_attempt_id'):
        assert event[key] is None or isinstance(event[key], str) and ID.fullmatch(event[key])
    for key in ('data_version', 'cached_version', 'version_hint', 'work_attempt'):
        assert event[key] is None or uint(event[key])
    for key in ('work_id', 'network_call_id'):
        if event[key] is not None:
            uuid_string(event[key])
    assert event['mode'] in {'PUSH', 'PERIODIC', 'HYBRID'}
    assert event['source'] in {'PUSH', 'PERIODIC', 'MANUAL', None}
    assert event['timestamp_utc'].endswith('Z')
    datetime.fromisoformat(event['timestamp_utc'].replace('Z', '+00:00'))
    assert isinstance(event['signal_ids'], list)
    assert all(isinstance(x, str) and ID.fullmatch(x) for x in event['signal_ids'])
    assert len(set(event['signal_ids'])) == len(event['signal_ids'])
    assert event['message_id'] is None or isinstance(event['message_id'], str) and 1 <= len(event['message_id']) <= 512
    assert event['http_status'] is None or type(event['http_status']) is int and 100 <= event['http_status'] <= 599
    if event['origin'] == 'SERVER':
        assert event['elapsed_realtime_ms'] is None and event['boot_session_id'] is None
    else:
        assert event['origin'] == 'ANDROID' and uint(event['elapsed_realtime_ms'])
    expected = {
        'push_send_accepted': ('SERVER', 'PUSH', 'accepted'),
        'push_received': ('ANDROID', 'PUSH', 'received'),
        'work_started': ('ANDROID', 'PUSH', 'started'),
        'snapshot_applied': ('ANDROID', 'PUSH', 'applied'),
    }
    assert (event['origin'], event['source'], event['outcome']) == expected[event['event_type']]
    if event['event_type'] == 'push_send_accepted':
        assert event['message_id'] is not None and event['send_attempt_id'] is not None
        assert type(event['ttl_ms']) is int and 0 <= event['ttl_ms'] <= 2419200000
    if event['event_type'] in {'push_send_accepted', 'push_received'}:
        assert len(event['signal_ids']) == 1
    if event['event_type'] in {'work_started', 'snapshot_applied'}:
        assert event['request_id'] and event['work_id'] and uint(event['work_attempt'])
    if event['event_type'] == 'snapshot_applied':
        assert uint(event['data_version']) and event['data_version'] == event['cached_version']


def main():
    api_text = API.read_text(encoding='utf-8')
    api_blocks = [parse_json(block) for block in re.findall(r'```json\n(.*?)\n```', api_text, re.S)]
    assert len(api_blocks) == 5
    health, read_snapshot, update, committed, error = api_blocks
    assert health == {'api_version': VERSION, 'status': 'ok'}
    assert_snapshot(read_snapshot)
    assert set(update) == {'update_id', 'run_id', 'mode', 'device_alias', 'title', 'body'}
    assert all(ID.fullmatch(update[k]) for k in ('update_id', 'run_id', 'device_alias'))
    assert update['mode'] in {'PUSH', 'PERIODIC', 'HYBRID'}
    assert_snapshot({k: committed[k] for k in ('api_version', 'version', 'last_modified_utc', 'items')})
    assert committed['replayed'] is False
    assert committed['run_id'] == update['run_id'] and committed['update_id'] == update['update_id']
    assert committed['items'][0]['id'] == f"bulletin-{committed['version']}"
    assert committed['items'][0]['title'] == update['title']
    assert committed['items'][0]['body'] == update['body']
    multi = {**read_snapshot, 'version': 2, 'items': [
        {'id': 'bulletin-2', 'title': 'Mới', 'body': '', 'version': 2},
        *read_snapshot['items'],
    ]}
    assert_snapshot(multi)  # Item cũ giữ version riêng; không đồng nhất với version snapshot.
    for invalid_snapshot in (
        {**multi, 'items': [multi['items'][0], multi['items'][0]]},
        {**multi, 'items': list(reversed(multi['items']))},
        {**multi, 'version': MAX_VERSION + 1},
    ):
        try:
            assert_snapshot(invalid_snapshot)
        except AssertionError:
            continue
        raise AssertionError('Snapshot fixture sai không bị validator phát hiện')
    assert error['api_version'] == VERSION and error['error']['request_id'] is None

    event_text = EVENTS.read_text(encoding='utf-8')
    blocks = re.findall(r'```jsonl\n(.*?)\n```', event_text, re.S)
    assert len(blocks) == 1
    events = [parse_json(line) for line in blocks[0].splitlines()]
    assert [x['event_type'] for x in events] == [
        'push_send_accepted', 'push_received', 'work_started', 'snapshot_applied'
    ]
    for event in events:
        assert_event(event)
        assert event['run_id'] == update['run_id']
        assert event['device_alias'] == update['device_alias']
        assert event['signal_ids'] == ['signal-demo-001']
    assert len({x['event_id'] for x in events}) == len(events)
    assert events[0]['message_id'] == '<fixture-fcm-response-id>'  # Fixture, không phải FCM ID thật.
    assert events[1]['message_id'] is None
    assert events[2]['request_id'] == events[3]['request_id']
    assert events[2]['work_id'] == events[3]['work_id']
    assert events[3]['data_version'] == committed['version']
    android = events[1:]
    assert len({x['boot_session_id'] for x in android}) == 1
    assert [x['elapsed_realtime_ms'] for x in android] == sorted(x['elapsed_realtime_ms'] for x in android)

    # Các thay đổi sai này phải bị phát hiện; đây không phải test server hay FCM.
    for invalid in (
        {**events[0], 'message_id': None},
        {**events[1], 'signal_ids': []},
        {**events[2], 'work_attempt': '0'},
        {**events[3], 'cached_version': 0},
    ):
        try:
            assert_event(invalid)
        except AssertionError:
            continue
        raise AssertionError('Fixture sai không bị validator phát hiện')
    try:
        parse_json('{"version":1,"version":2}')
    except AssertionError:
        pass
    else:
        raise AssertionError('Duplicate JSON key không bị phát hiện')
    print('PASS: 5 ví dụ JSON API, 4 JSONL events, correlation chéo; 3 snapshot, 4 event sai và duplicate key bị phát hiện')
    print('Không gọi HTTP/FCM; đây không phải kiểm thử runtime hoặc schema validator đầy đủ.')


if __name__ == '__main__':
    main()
