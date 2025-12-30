# tests/test_input.py
from src.input import KeyReader

def test_keyreader_context_manager():
    with KeyReader() as kr:
        assert kr is not None
def test_keyreader_read_key():
    with KeyReader() as kr:
        key = kr.read_key()
        # Since this is non-blocking, we can't assert a specific key,
        # but we can assert that it returns either None or a string.
        assert key is None or isinstance(key, str)