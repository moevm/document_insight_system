from contextlib import contextmanager
from contextvars import ContextVar

current_check_id = ContextVar('current_check_id', default=None)
current_check_stage = ContextVar('current_check_stage', default=None)


@contextmanager
def check_log_context(check_id):
    cid_tok = current_check_id.set(check_id)
    stage_tok = current_check_stage.set(None)
    try:
        yield
    finally:
        current_check_id.reset(cid_tok)
        current_check_stage.reset(stage_tok)
