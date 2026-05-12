"""Claude Code hook — updates floating ball status file.

Event → status mapping:
  PermissionRequest  → waiting  (Claude needs user to approve a tool)
  PostToolUse        → running  (tool done, back to work)
  Stop               → completed (Claude finished responding)
  UserPromptSubmit   → running  (new user request, Claude starts working)
  SessionEnd         → exit     (Claude Code exiting, close floating ball)
"""
import json
import sys
import time
from pathlib import Path

STATUS_FILE = Path.home() / '.claude' / '.floating_ball_status.json'
STATUS_MAP = {
    'PermissionRequest': 'waiting',
    'PostToolUse':       'running',
    'Stop':              'completed',
    'UserPromptSubmit':  'running',
    'SessionEnd':        'exit',
}


def main():
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw else {}
    except Exception:
        event = {}

    event_type = event.get('hook_event_name', 'UNKNOWN')
    status = STATUS_MAP.get(event_type)

    if status:
        try:
            STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATUS_FILE.write_text(json.dumps({
                'status': status,
                'timestamp': time.time(),
            }))
        except Exception:
            pass


if __name__ == '__main__':
    main()
