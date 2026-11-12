"""Audit single-owner tasks; --apply refreshes input readiness and documentation.

Requires Python 3.10+ and authenticated gh with repo/project scopes.
Never changes workflow Status, Assignees, Owner, Deadline or creates task cards.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = 'PVT_kwHOCnL5Fs4BpUDU'
BOARD = 'https://github.com/users/ThanhTris/projects/3/views/1'
REPO = 'https://github.com/ThanhTris/Seminar-IE307/blob/main/'
INPUT_FIELD = 'Input status'
WAITING_FIELD = 'Còn chờ'
DEADLINE_FIELD = 'Deadline (UTC+7)'
READINESS_SPECS = (
    ('Sẵn sàng', 'GREEN', 'Cột Todo: Đủ đầu vào ở gate bắt đầu; có thể bắt tay thực hiện ngay.'),
    ('Chờ đầu vào', 'ORANGE', 'Cột Todo: Còn task tiên quyết ở gate bắt đầu chưa Done; chờ đầu vào bàn giao.'),
    ('Đang thực hiện', 'BLUE', 'Cột In Progress: Người được giao đang trực tiếp triển khai task.'),
    ('Chờ kiểm tra', 'YELLOW', 'Cột Review: Đầu ra đã bàn giao, đang chờ kiểm tra nghiệm thu.'),
    ('Cần cập nhật', 'RED', 'Cột Needs Update: Owner cần chỉnh sửa theo kết quả kiểm tra.'),
    ('Đã hoàn thành', 'PURPLE', 'Cột Done: Task đã hoàn tất và nghiệm thu; đầu ra sẵn sàng cho task sau.'),
)
READINESS = tuple(name for name, _, _ in READINESS_SPECS)


def format_deadline(task):
    if task.get('due_at'):
        return datetime.fromisoformat(task['due_at']).strftime('%d/%m/%Y %H:%M') + ' (UTC+7)'
    return task['due']


def gh(*args, payload=None):
    raw = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None
    result = subprocess.run(['gh', *args], input=raw, capture_output=True, cwd=ROOT)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', 'replace') + result.stdout.decode('utf-8', 'replace'))
    return json.loads(result.stdout)


def gql(query, variables=None):
    # All GraphQL mutations used here are idempotent updates.
    for attempt in range(3):
        try:
            result = gh('api', 'graphql', '--input', '-', payload={'query': query, 'variables': variables or {}})
            if result.get('errors'):
                raise ValueError(json.dumps(result['errors'], ensure_ascii=False))
            return result['data']
        except (RuntimeError, json.JSONDecodeError):
            if attempt == 2:
                raise
            time.sleep(2)


def project_snapshot():
    return gql('''query {user(login:"ThanhTris"){projectV2(number:3){id readme
      views(first:20){nodes{id number name layout}}
      items(first:100){pageInfo{hasNextPage} nodes{id fullDatabaseId isArchived
        content{... on DraftIssue{id title body assignees(first:10){nodes{login}}}}
        fieldValues(first:30){nodes{
          ... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2SingleSelectField{name}}}
          ... on ProjectV2ItemFieldDateValue{date field{... on ProjectV2Field{name}}}
          ... on ProjectV2ItemFieldTextValue{text field{... on ProjectV2Field{name}}}
        }}
      }}
    }}}''')['user']['projectV2']


def values(item):
    return {v['field']['name']: v.get('name', v.get('date', v.get('text')))
            for v in item['fieldValues']['nodes'] if v.get('field')}


def audit(catalog, snapshot):
    tasks = catalog['tasks']
    by = {t['id']: t for t in tasks}
    assert len(by) == len(tasks) == 45, 'Expected 45 distinct task specifications.'
    if catalog.get('deadline_at'):
        assert all(t.get('due_at') for t in tasks), 'Every task needs a full deadline with timezone.'
    assert not snapshot['items']['pageInfo']['hasNextPage'], 'Fetch all pages before auditing.'
    active = [i for i in snapshot['items']['nodes'] if not i['isArchived']]
    assert len(active) == 45, f'Expected 45 active cards, got {len(active)}.'
    lookup = {}
    for item in active:
        match = re.match(r'(SEM-\d+) — ', item['content']['title'])
        assert match, item['content']['title']
        tid = match.group(1)
        assert tid in by and tid not in lookup, ('Unknown/duplicate', tid)
        lookup[tid] = item
        t, fields = by[tid], values(item)
        assert item['content']['title'] == f"{tid} — {t['title']}"
        assert [a['login'] for a in item['content']['assignees']['nodes']] == [t['github']], (tid, 'Assignees')
        assert fields['Owner'] == t['owner'], (tid, 'Owner')
        assert fields['Deadline'] == t['due'], (tid, 'Deadline')
        if t.get('due_at'):
            due_at = datetime.fromisoformat(t['due_at'])
            assert due_at.utcoffset() == timedelta(hours=7), (tid, 'Timezone')
            assert due_at.date().isoformat() == t['due'], (tid, 'Date/time mismatch')
            assert fields.get(DEADLINE_FIELD) == format_deadline(t), (tid, DEADLINE_FIELD)
            assert due_at <= datetime.fromisoformat(catalog['deadline_at']), (tid, 'Final deadline')
        assert fields['Status'] in ('Todo', 'In Progress', 'Review', 'Needs Update', 'Done')
        assert not fields.get('Task Reviewer'), (tid, 'Extra reviewer')
    assert sum(t['effort'] for t in tasks) == 100
    assert sum(t['effort'] for t in tasks if t['category'] == 'practice') == 80
    assert sum(t['effort'] for t in tasks if t['category'] == 'research') == 20
    visiting, visited = set(), set()
    def visit(tid):
        assert tid not in visiting, ('Dependency cycle', tid)
        if tid in visited:
            return
        visiting.add(tid)
        for d in by[tid]['start_dependencies'] + by[tid]['finish_dependencies']:
            assert d in by and by[d]['due'] <= by[tid]['due'], (tid, d)
            if by[tid].get('due_at'):
                assert datetime.fromisoformat(by[d]['due_at']) < datetime.fromisoformat(by[tid]['due_at']), (tid, d, 'Deadline order')
            visit(d)
        visiting.remove(tid)
        visited.add(tid)
    for tid in by:
        visit(tid)
    return by, lookup


def compute_todo_unlocks(tasks, prev_inputs, statuses):
    unlocked = []
    for t in tasks:
        tid = t['id']
        if statuses.get(tid) == 'Todo':
            curr_inp = input_status(t, statuses)
            prev_inp = prev_inputs.get(tid)
            if prev_inp == 'Chờ đầu vào' and curr_inp == 'Sẵn sàng':
                done_deps = [d for d in t['start_dependencies'] if statuses.get(d) == 'Done']
                unlocked.append((t, done_deps))
    return unlocked


def sync_project_field_options(field_id, existing_options):
    existing_by_name = {o['name']: o for o in existing_options}
    specs_to_apply = []
    for name, color, desc in READINESS_SPECS:
        item = {'name': name, 'color': color, 'description': desc}
        if name in existing_by_name:
            item['id'] = existing_by_name[name]['id']
        specs_to_apply.append(item)
    res = gql('''mutation($input:UpdateProjectV2FieldInput!){updateProjectV2Field(input:$input){projectV2Field{... on ProjectV2SingleSelectField{options{id name}}}}}''',
              {'input': {'fieldId': field_id, 'singleSelectOptions': specs_to_apply}})
    return {o['name']: o['id'] for o in res['updateProjectV2Field']['projectV2Field']['options']}


def waiting_on(task, statuses):
    """Unfinished prerequisites of an open task: (start gate, finish gate)."""
    if statuses.get(task['id']) == 'Done':
        return [], []
    return ([d for d in task['start_dependencies'] if statuses[d] != 'Done'],
            [d for d in task['finish_dependencies'] if statuses[d] != 'Done'])


def waiting_text(task, statuses, prefix=None):
    start, finish = waiting_on(task, statuses)
    fmt = (lambda i: f'[{i}]({prefix}{i}.md)') if prefix is not None else (lambda i: i)
    parts = []
    if start:
        parts.append('Bắt đầu: ' + ', '.join(map(fmt, start)))
    if finish:
        parts.append('Hoàn tất: ' + ', '.join(map(fmt, finish)))
    return '; '.join(parts) or 'Không'


def report(catalog, statuses):
    """Per-owner summary: what can start now and which unfinished task each gate waits on."""
    by = {t['id']: t for t in catalog['tasks']}

    def who(ids):
        return ', '.join(f"{i} ({by[i]['owner']}, {statuses[i]})" for i in ids)

    lines = []
    for name in catalog['members']:
        mine = [t for t in catalog['tasks'] if t['owner'] == name and statuses[t['id']] != 'Done']
        lines.append(f'## {name}')
        if not mine:
            lines.append('  Không còn task mở.')
        for t in mine:
            start, finish = waiting_on(t, statuses)
            head = 'BỊ CHẶN bởi ' + who(start) if start else 'LÀM ĐƯỢC NGAY'
            tail = f' | Done cần thêm: {who(finish)}' if finish else ''
            lines.append(f"  {t['id']} [{statuses[t['id']]}] {head}{tail} — {t['title']}")
    odd = []
    for t in catalog['tasks']:
        open_deps = [d for d in t['start_dependencies'] + t['finish_dependencies'] if statuses[d] != 'Done']
        if statuses[t['id']] == 'Done' and open_deps:
            odd.append(f"  {t['id']} đã Done nhưng gate {', '.join(open_deps)} chưa Done")
    if odd:
        lines += ['## Cần xem lại'] + odd
    return chr(10).join(lines)


def input_status(task, statuses):
    st = statuses.get(task['id'])
    if st == 'Done':
        return 'Đã hoàn thành'
    if st == 'In Progress':
        return 'Đang thực hiện'
    if st == 'Review':
        return 'Chờ kiểm tra'
    if st == 'Needs Update':
        return 'Cần cập nhật'
    if any(statuses[d] != 'Done' for d in task['start_dependencies']):
        return 'Chờ đầu vào'
    return 'Sẵn sàng'


def refs(ids, prefix=''):
    return ', '.join(f'[{i}]({prefix}{i}.md)' for i in ids) or 'Không có.'


def input_section(t, by, statuses, stamp):
    bases = [('Kế hoạch/phạm vi', '../../docs/PLAN.md')]
    n = int(t['id'].split('-')[1])
    if n in (13, 15, 17, 18, 20, 21, 22):
        bases.append(('Nguồn kỹ thuật và nghiên cứu', '../../research/README.md'))
    if n in (12, 16, 24, 29, 34, 41, 42, 43, 44, 45):
        bases.append(('Protocol cốt lõi', '../../docs/EXPERIMENT_PROTOCOL.md'))
    if n >= 46:
        bases.append(('Kịch bản 15 phút', '../../docs/PRESENTATION_PLAN.md'))
    section = '<!-- task-inputs:start -->\n## Đầu vào cần nhận\n\n'
    section += 'Tài liệu nền đã có: ' + ' · '.join(f'[{name}]({path})' for name, path in bases) + '.\n\n'
    deps = [('Bắt đầu', d) for d in t['start_dependencies']] + [('Hoàn tất', d) for d in t['finish_dependencies']]
    if deps:
        section += '| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |\n|---|---|---|---|---|---|\n'
        for gate, dep in deps:
            producer = by[dep]
            artifacts = '<br>'.join(f'`{p}`' for p in producer['outputs'])
            section += f"| {gate} | [{dep} — {producer['title']}]({dep}.md) | {producer['owner']} | {artifacts} | `docs/evidence/{dep}/CHECKS.md` | {statuses[dep]} |\n"
        section += '\nĐây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.\n'
    else:
        section += 'Không cần nhận đầu ra từ task khác để bắt đầu. Owner thực hiện từ tài liệu nền và tự ghi các blocker môi trường/quyền truy cập trong CHECKS của task này.\n'
    section += f'\nStatus nguồn được đối chiếu Project lúc **{stamp}**; mở link task nguồn để xem cập nhật mới hơn.\n<!-- task-inputs:end -->\n\n'
    return section


def update_docs(catalog, by, statuses, stamp):
    catalog['snapshot_at'] = stamp
    catalog['snapshot_source'] = BOARD
    for t in catalog['tasks']:
        t['status'] = statuses[t['id']]
        t['input_status'] = input_status(t, statuses)
        start_wait, finish_wait = waiting_on(t, statuses)
        t['waiting_on'] = {'start': start_wait, 'finish': finish_wait}
        t['inputs'] = [{'source_task': dep, 'required_for': phase,
                        'producer': by[dep]['owner'], 'artifacts': by[dep]['outputs'],
                        'checks': f'docs/evidence/{dep}/CHECKS.md', 'source_status': statuses[dep]}
                       for phase, ids in [('start', t['start_dependencies']), ('finish', t['finish_dependencies'])]
                       for dep in ids]
        p = ROOT / 'tasks/backlog' / f"{t['id']}.md"
        body = p.read_text(encoding='utf-8')
        body = re.sub(r'(?m)^- Trạng thái:.*$', f"- Trạng thái: **{t['status']}** (Project).", body)
        body = re.sub(r'(?m)^- Hạn:.*$', f"- Hạn: **{format_deadline(t)}**.", body)
        body = re.sub(r'(?m)^- (Trạng thái đầu vào|Còn chờ|Đối chiếu Project):.*\n', '', body)
        body = body.replace(f"- Trạng thái: **{t['status']}** (Project).\n",
                            f"- Trạng thái: **{t['status']}** (Project).\n- Trạng thái đầu vào: **{t['input_status']}**.\n- Còn chờ: {waiting_text(t, statuses, '')}.\n- Đối chiếu Project: {stamp}.\n", 1)
        body = re.sub(r'(?s)<!-- task-inputs:start -->.*?<!-- task-inputs:end -->\s*', '', body)
        at = body.index('\n## Việc ')
        body = body[:at] + '\n' + input_section(t, by, statuses, stamp) + body[at:]
        p.write_text(body, encoding='utf-8')
    (ROOT / 'tasks/catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    p = ROOT / 'tasks/README.md'
    body = p.read_text(encoding='utf-8')
    table_at = body.index('| Task | Người thực hiện duy nhất |')
    body = body[:table_at]
    body = re.sub(r'Cập nhật 29/10/2026\. \*\*45 task SEM-11…SEM-55\*\*, mỗi task đúng một người thực hiện;.*?Hạn cuối',
                  'Phân công 29/10/2026: **45 task SEM-11…SEM-55**, mỗi task đúng một người thực hiện. Tiến độ được đối chiếu Project trong snapshot bên dưới. Hạn cuối', body)
    body = re.sub(r'(?s)<!-- input-snapshot:start -->.*?<!-- input-snapshot:end -->\s*', '', body)
    body = re.sub(r'(?s)<!-- deadline-policy:start -->.*?<!-- deadline-policy:end -->\s*', '', body)
    if catalog.get('deadline_at'):
        body += '''<!-- deadline-policy:start -->
## Deadline từng task

[Lịch đầy đủ theo từng người](DEADLINES.md). Mỗi task có ngày và giờ bàn giao theo UTC+7; cột `Deadline (UTC+7)` trên Project hiển thị đầy đủ. Các gate trong cùng ngày được xếp giờ bàn giao trước task nhận đầu vào. Gói cuối SEM-55 hạn 12/11/2026 22:00, ngày 13/11 dành dự phòng đến 22:00.
<!-- deadline-policy:end -->

'''
    counts = Counter(t['input_status'] for t in catalog['tasks'])
    body += f'''<!-- input-snapshot:start -->
## Trạng thái đối chiếu Project

Snapshot **{stamp}**. Status là tiến độ thực hiện; Input status là trạng thái tương ứng theo từng cột:
- **Cột Todo:** Sẵn sàng **{counts.get('Sẵn sàng', 0)}**, Chờ đầu vào **{counts.get('Chờ đầu vào', 0)}**.
- **Cột In Progress:** Đang thực hiện **{counts.get('Đang thực hiện', 0)}**.
- **Cột Review:** Chờ kiểm tra **{counts.get('Chờ kiểm tra', 0)}**.
- **Cột Needs Update:** Cần cập nhật **{counts.get('Cần cập nhật', 0)}**.
- **Cột Done:** Đã hoàn thành **{counts.get('Đã hoàn thành', 0)}**.

- Đã hoàn thành: task đã hoàn tất và nghiệm thu ở cột Done; đầu ra sẵn sàng cho task sau.
- Đang thực hiện: người được giao đang trực tiếp triển khai task ở cột In Progress.
- Chờ kiểm tra: đầu ra đã sẵn sàng, đang chờ kiểm tra nghiệm thu ở cột Review.
- Cần cập nhật: owner cần chỉnh sửa theo kết quả kiểm tra ở cột Needs Update.
- Sẵn sàng: task ở cột Todo có toàn bộ đầu vào ở gate bắt đầu đã xong; có thể bắt tay thực hiện ngay.
- Chờ đầu vào: task ở cột Todo còn task tiên quyết chưa qua cột Done; cần chờ bàn giao.

Cột **Còn chờ task chưa Done** (và trường `Còn chờ` trên Project) ghi đích danh task tiên quyết chưa Done: `Bắt đầu:` là task đang chặn việc bắt đầu, `Hoàn tất:` là task phải Done trước khi task này được chuyển Done. Xem nhanh theo người bằng `python scripts/update_task_snapshot.py --report`. `--set-status SEM-XX=Done` bị từ chối khi task còn gate chưa Done, trừ khi thêm `--force`.

Project là nguồn Status hiện hành. Sau khi đổi Status nguồn, chạy `python scripts/update_task_snapshot.py --apply` để đồng bộ Input status và tài liệu; script tự động kiểm tra mở khóa các task ở cột Todo từ Chờ đầu vào sang Sẵn sàng khi task tiên quyết qua cột Done. `--check` chỉ kiểm độ khớp. Script giữ nguyên Status/Assignees/Owner/Deadline và không tạo thẻ.
<!-- input-snapshot:end -->

| Task | Người thực hiện | Status | Input status | Còn chờ task chưa Done | Hạn (UTC+7) | Công sức | Bắt đầu sau | Hoàn tất còn cần |
|---|---|---|---|---|---|---:|---|---|
'''
    for t in catalog['tasks']:
        body += f"| [{t['id']}](backlog/{t['id']}.md) — {t['title']} | {t['owner']} | {t['status']} | {t['input_status']} | {waiting_text(t, statuses, 'backlog/')} | {format_deadline(t)} | {t['effort']} | {refs(t['start_dependencies'], 'backlog/')} | {refs(t['finish_dependencies'], 'backlog/')} |\n"
    # Older snapshots used a different header; future runs use the same anchor.
    body = body.replace('| Task | Người thực hiện | Status |', '| Task | Người thực hiện duy nhất | Status |', 1)
    p.write_text(body, encoding='utf-8')
    p = ROOT / 'docs/TEAM_ASSIGNMENTS.md'
    body = p.read_text(encoding='utf-8')
    for name in catalog['members']:
        start = body.index(f'## {name}\n')
        end = body.find('\n## ', start + 4)
        if end < 0:
            end = len(body)
        part = f'## {name}\n\n| Task | Đầu việc duy nhất | Status | Input status | Còn chờ task chưa Done | Hạn (UTC+7) | Bắt đầu sau | Hoàn tất còn cần |\n|---|---|---|---|---|---|---|---|\n'
        for t in catalog['tasks']:
            if t['owner'] != name:
                continue
            part += f"| [{t['id']}](../tasks/backlog/{t['id']}.md) | {t['title']} | {t['status']} | {t['input_status']} | {waiting_text(t, statuses, '../tasks/backlog/')} | {format_deadline(t)} | {refs(t['start_dependencies'], '../tasks/backlog/')} | {refs(t['finish_dependencies'], '../tasks/backlog/')} |\n"
        body = body[:start] + part + body[end:]
    body = re.sub(r'(?s)<!-- team-snapshot:start -->.*?<!-- team-snapshot:end -->\s*', '', body)
    at = body.index('## Trí\n')
    body = body[:at] + f'<!-- team-snapshot:start -->\nStatus và Input status đối chiếu Project lúc **{stamp}**. Mở từng task để xem cụ thể file đầu vào, người bàn giao và CHECKS phải nhận. [Cách làm mới trạng thái](../tasks/README.md#trạng-thái-đối-chiếu-project).\n<!-- team-snapshot:end -->\n\n' + body[at:]
    p.write_text(body, encoding='utf-8')
    if catalog.get('deadline_at'):
        deadline_doc = '''# Deadline từng task — một người thực hiện

Tất cả mốc dưới đây dùng **giờ Việt Nam (UTC+7)**, năm **2026**. Đây là lịch mục tiêu bàn giao, không phải thời điểm task đã hoàn thành. Gói cuối SEM-55 chốt **12/11 lúc 22:00**; dự phòng sửa lỗi/nghiệm thu cuối đến **13/11 lúc 22:00**.

[Mở Project theo người](https://github.com/users/ThanhTris/projects/3/views/2) · [Task và trạng thái đầu vào](README.md).

Do lần lập giờ diễn ra gần hết ngày 29/10 và SEM-11/12/13 vẫn Todo, ba task này chuyển sang 12:00 ngày 30/10. Các ngày hạn còn lại giữ như lịch trước; thêm giờ để tách cổng bàn giao trong cùng ngày. Hạn task nguồn luôn sớm hơn task nhận đầu vào. Nếu trễ gate, owner báo blocker, không tự coi task nguồn đã xong hay bỏ gate.
'''
        for name in catalog['members']:
            deadline_doc += f'\n## {name}\n\n| Task | Việc bàn giao | Deadline UTC+7 |\n|---|---|---|\n'
            for t in sorted((t for t in catalog['tasks'] if t['owner'] == name), key=lambda t: t['due_at']):
                deadline_doc += f"| [{t['id']}](backlog/{t['id']}.md) | {t['title']} | {format_deadline(t)} |\n"
        (ROOT / 'tasks/DEADLINES.md').write_text(deadline_doc, encoding='utf-8')


def render(t, lookup):
    body = (ROOT / 'tasks/backlog' / f"{t['id']}.md").read_text(encoding='utf-8')
    def replace_link(match):
        label, dest = match.group(1), match.group(2)
        if '://' in dest or dest.startswith('#'):
            return match.group(0)
        task_match = re.fullmatch(r'(SEM-\d+)\.md', dest)
        if task_match and task_match.group(1) in lookup:
            url = f"{BOARD}?pane=issue&itemId={lookup[task_match.group(1)]['fullDatabaseId']}"
        else:
            target = (ROOT / 'tasks/backlog' / dest).resolve().relative_to(ROOT)
            url = REPO + target.as_posix()
        return f'[{label}]({url})'
    body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, body)
    return body + f'\n[Đặc tả trong repository]({REPO}tasks/backlog/{t["id"]}.md) · [Bảng theo người]({REPO}docs/TEAM_ASSIGNMENTS.md)\n'


def generated_parts(body):
    metadata = re.search(r'(?m)^- Trạng thái:.*\n- Trạng thái đầu vào:.*\n- Còn chờ:.*\n- Đối chiếu Project:.*\n', body)
    inputs = re.search(r'(?s)<!-- task-inputs:start -->.*?<!-- task-inputs:end -->', body)
    deadline = re.search(r'(?m)^- Hạn:.*$', body)
    assert metadata and inputs and deadline, 'Missing generated input/status/deadline sections.'
    return metadata.group(), inputs.group(), deadline.group()


def merge_card_snapshot(t, item, lookup):
    """Refresh generated sections while retaining owner notes and manual body edits."""
    expected_meta, expected_inputs, expected_deadline = generated_parts(render(t, lookup))
    body = item['content']['body']
    metadata = re.compile(r'(?m)^- Trạng thái:.*(?:\n- Trạng thái đầu vào:.*)?(?:\n- Còn chờ:.*)?(?:\n- Đối chiếu Project:.*)?\n')
    assert metadata.search(body), (t['id'], 'Missing status block; review task description before applying.')
    body = metadata.sub(lambda _: expected_meta, body, count=1)
    assert re.search(r'(?m)^- Hạn:.*$', body), (t['id'], 'Missing deadline line')
    body = re.sub(r'(?m)^- Hạn:.*$', lambda _: expected_deadline, body, count=1)
    inputs = re.compile(r'(?s)<!-- task-inputs:start -->.*?<!-- task-inputs:end -->')
    if inputs.search(body):
        body = inputs.sub(lambda _: expected_inputs, body, count=1)
    else:
        at = body.index('\n## Việc ')
        body = body[:at] + '\n' + expected_inputs + '\n\n' + body[at:]
    return body


def batch(ops):
    declarations, fields, variables = [], [], {}
    for i, (name, typ, value, result) in enumerate(ops):
        declarations.append(f'$v{i}:{typ}!')
        variables[f'v{i}'] = value
        fields.append(f'a{i}:{name}(input:$v{i}){{{result}}}')
    return gql('mutation(' + ','.join(declarations) + '){' + ' '.join(fields) + '}', variables)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--check', action='store_true')
    group.add_argument('--report', action='store_true',
                       help='Chỉ đọc: in theo người task làm được ngay và task đang chờ task nào chưa Done')
    parser.add_argument('--force', action='store_true',
                        help='Cho phép --set-status Done dù task còn gate chưa Done')
    parser.add_argument('--set-status', action='append', metavar='SEM-XX=STATUS',
                        help='Chuyển cột Status cho task trước khi đồng bộ (ví dụ: --set-status SEM-32=Done)')
    args = parser.parse_args()
    catalog = json.loads((ROOT / 'tasks/catalog.json').read_text(encoding='utf-8'))
    snapshot = project_snapshot()
    by, lookup = audit(catalog, snapshot)
    statuses = {tid: values(item)['Status'] for tid, item in lookup.items()}
    if args.report:
        print(report(catalog, statuses))
        return
    if args.set_status:
        if not args.apply:
            parser.error('--set-status requires --apply')
        fields = gh('project', 'field-list', '3', '--owner', 'ThanhTris', '--format', 'json', '--limit', '100')['fields']
        status_field = next(f for f in fields if f['name'] == 'Status')
        status_opts = {o['name']: o['id'] for o in status_field['options']}
        for spec in args.set_status:
            target_tid, target_st = spec.split('=')
            assert target_tid in lookup, f'Unknown task {target_tid}'
            assert target_st in status_opts, f'Unknown status {target_st}'
            if target_st == 'Done' and not args.force:
                start_wait, finish_wait = waiting_on(by[target_tid], {**statuses, target_tid: 'Todo'})
                if start_wait or finish_wait:
                    parser.error(f"{target_tid} chưa thể Done: còn chờ {', '.join(start_wait + finish_wait)} chưa Done. "
                                 'Hoàn tất task đó trước hoặc thêm --force nếu đã chấp nhận ngoại lệ.')
            statuses[target_tid] = target_st
            item_id = lookup[target_tid]['id']
            gql('mutation($input:UpdateProjectV2ItemFieldValueInput!){updateProjectV2ItemFieldValue(input:$input){projectV2Item{id}}}',
                {'input': {'projectId': PROJECT, 'itemId': item_id, 'fieldId': status_field['id'], 'value': {'singleSelectOptionId': status_opts[target_st]}}})
            print(f"Set status: {target_tid} -> {target_st}")
        snapshot = project_snapshot()
        by, lookup = audit(catalog, snapshot)
        statuses = {tid: values(item)['Status'] for tid, item in lookup.items()}
    if args.apply:
        stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        prev_inputs = {t['id']: t.get('input_status') for t in catalog['tasks']}
        update_docs(catalog, by, statuses, stamp)
        unlocked = compute_todo_unlocks(catalog['tasks'], prev_inputs, statuses)
        if unlocked:
            print(f"\n[MỞ KHÓA] Có {len(unlocked)} task ở cột Todo được mở khóa sang 'Sẵn sàng':")
            for t, done_deps in unlocked:
                print(f"  * {t['id']} — {t['title']} (Owner: {t['owner']})")
                print(f"    -> Đã thỏa mãn toàn bộ gate bắt đầu: {', '.join(done_deps)}")
        fields = gh('project', 'field-list', '3', '--owner', 'ThanhTris', '--format', 'json', '--limit', '100')['fields']
        input_field = next((f for f in fields if f['name'] == INPUT_FIELD), None)
        if input_field is None:
            gh('project', 'field-create', '3', '--owner', 'ThanhTris', '--name', INPUT_FIELD,
               '--data-type', 'SINGLE_SELECT', '--single-select-options', ','.join(READINESS), '--format', 'json')
            fields = gh('project', 'field-list', '3', '--owner', 'ThanhTris', '--format', 'json', '--limit', '100')['fields']
            input_field = next(f for f in fields if f['name'] == INPUT_FIELD)
        waiting_field = next((f for f in fields if f['name'] == WAITING_FIELD), None)
        if waiting_field is None:
            gh('project', 'field-create', '3', '--owner', 'ThanhTris', '--name', WAITING_FIELD,
               '--data-type', 'TEXT', '--format', 'json')
            fields = gh('project', 'field-list', '3', '--owner', 'ThanhTris', '--format', 'json', '--limit', '100')['fields']
            waiting_field = next(f for f in fields if f['name'] == WAITING_FIELD)
        options = {o['name']: o['id'] for o in input_field['options']}
        if set(options) != set(READINESS):
            options = sync_project_field_options(input_field['id'], input_field['options'])
        assert set(options) == set(READINESS)
        tasks = catalog['tasks']
        for offset in range(0, len(tasks), 2):
            ops = []
            for t in tasks[offset:offset + 2]:
                item = lookup[t['id']]
                ops.extend([
                    ('updateProjectV2DraftIssue', 'UpdateProjectV2DraftIssueInput',
                     {'draftIssueId': item['content']['id'], 'body': merge_card_snapshot(t, item, lookup)}, 'draftIssue{id}'),
                    ('updateProjectV2ItemFieldValue', 'UpdateProjectV2ItemFieldValueInput',
                     {'projectId': PROJECT, 'itemId': item['id'], 'fieldId': input_field['id'],
                      'value': {'singleSelectOptionId': options[t['input_status']]}}, 'projectV2Item{id}'),
                    ('updateProjectV2ItemFieldValue', 'UpdateProjectV2ItemFieldValueInput',
                     {'projectId': PROJECT, 'itemId': item['id'], 'fieldId': waiting_field['id'],
                      'value': {'text': waiting_text(t, statuses)}}, 'projectV2Item{id}')
                ])
            batch(ops)
            print('Updated inputs: ' + ', '.join(t['id'] for t in tasks[offset:offset + 2]), flush=True)
        field_ids = {f['name']: f['id'] for f in fields}
        deadline_name = DEADLINE_FIELD if DEADLINE_FIELD in field_ids else 'Deadline'
        visible = [field_ids[n] for n in ('Title', 'Owner', deadline_name, 'Status', 'Input status', WAITING_FIELD, 'Assignees', 'Depends on', 'Unblocks')]
        for view in snapshot['views']['nodes']:
            if view['number'] in (1, 2):
                gql('mutation($input:UpdateProjectV2ViewInput!){updateProjectV2View(input:$input){projectV2View{id}}}',
                    {'input': {'viewId': view['id'], 'configuration': {'visibleFieldIds': visible}}})
        counts = Counter(t['input_status'] for t in tasks)
        block = f'''<!-- input-snapshot:start -->
## Trạng thái đầu vào

Đối chiếu **{stamp}**: Đã hoàn thành **{counts.get('Đã hoàn thành', 0)}**, Đang thực hiện **{counts.get('Đang thực hiện', 0)}**, Chờ kiểm tra **{counts.get('Chờ kiểm tra', 0)}**, Cần cập nhật **{counts.get('Cần cập nhật', 0)}**, Sẵn sàng **{counts.get('Sẵn sàng', 0)}**, Chờ đầu vào **{counts.get('Chờ đầu vào', 0)}**. Status vẫn là tiến độ thực tế trên Project; Input status mô tả trạng thái tương ứng theo từng cột và tự động kiểm tra mở khóa task ở cột Todo khi task tiên quyết qua cột Done.

- Cột Todo: Sẵn sàng (đủ gate bắt đầu), Chờ đầu vào (còn task tiên quyết chưa xong).
- Cột In Progress: Đang thực hiện.
- Cột Review: Chờ kiểm tra.
- Cột Needs Update: Cần cập nhật.
- Cột Done: Đã hoàn thành.

Mỗi thẻ có bảng **Đầu vào cần nhận**: task nguồn bấm được, người bàn giao, file/artifact yêu cầu, CHECKS và Status nguồn. Chỉ dùng đầu ra sau khi nhận đúng artifact/version/CHECKS.

Sau khi đổi Status nguồn, dùng `python scripts/update_task_snapshot.py --apply` để cập nhật lại Input status và tài liệu. Khi task chuyển qua cột Done, script tự động quét và mở khóa các task ở cột Todo từ Chờ đầu vào sang Sẵn sàng. `--check` chỉ kiểm tra.
<!-- input-snapshot:end -->
'''
        readme = re.sub(r'(?s)<!-- input-snapshot:start -->.*?<!-- input-snapshot:end -->\s*', '', snapshot['readme']).rstrip() + '\n\n' + block
        gql('mutation($input:UpdateProjectV2Input!){updateProjectV2(input:$input){projectV2{id}}}',
            {'input': {'projectId': PROJECT, 'readme': readme}})
        snapshot = project_snapshot()
        by, lookup = audit(catalog, snapshot)
        assert statuses == {tid: values(item)['Status'] for tid, item in lookup.items()}, 'Status changed during sync; rerun to refresh.'
    for t in catalog['tasks']:
        tid, item = t['id'], lookup[t['id']]
        expected = input_status(t, statuses)
        assert t['status'] == statuses[tid], (tid, 'Local Status stale; run --apply')
        assert t.get('input_status') == values(item).get(INPUT_FIELD) == expected, (tid, 'Input status stale; run --apply')
        assert values(item).get(WAITING_FIELD) == waiting_text(t, statuses), (tid, 'Waiting field stale; run --apply')
        assert generated_parts(item['content']['body']) == generated_parts(render(t, lookup)), (tid, 'Input/status snapshot differs; review or refresh')
        for phase, deps in [('start', t['start_dependencies']), ('finish', t['finish_dependencies'])]:
            for dep in deps:
                assert f'pane=issue&itemId={lookup[dep]["fullDatabaseId"]}' in item['content']['body']
                for output in by[dep]['outputs']:
                    assert f'`{output}`' in item['content']['body'], (tid, dep, output)
    print(json.dumps({'verified': 45, 'statuses': dict(Counter(statuses.values())),
                      'input_status': dict(Counter(t['input_status'] for t in catalog['tasks'])),
                      'one_assignee_matches_owner_each': True, 'dependency_cycle': False}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
