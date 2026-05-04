import logging
from contextlib import contextmanager
from contextvars import ContextVar

current_check_id = ContextVar('current_check_id', default=None)
current_check_stage = ContextVar('current_check_stage', default=None)


class CheckContextFormatter(logging.Formatter):
    def format(self, record):
        line = super().format(record)
        cid = current_check_id.get()
        stage = current_check_stage.get()

        prefix_parts = []
        if cid is not None:
            prefix_parts.append(f'check_id={cid}')
        if stage is not None:
            prefix_parts.append(f'stage={stage}')
        if not prefix_parts:
            return line
        return f"{line} [{' '.join(prefix_parts)}]"


@contextmanager
def check_log_context(check_id):
    cid_tok = current_check_id.set(check_id)
    stage_tok = current_check_stage.set(None)
    try:
        yield
    finally:
        current_check_id.reset(cid_tok)
        current_check_stage.reset(stage_tok)
