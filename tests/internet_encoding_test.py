# -*- coding: utf-8 -*-
import pytest


# Define some interesting unicode inputs
class UNICODE(object):
    ascii = u'A'  # The most basic of unicode.
    latin1 = ascii + u'ü'  # U-umlaut. This is defined in latin1 but not ascii.
    win1252 = latin1 + u'€'  # Euro sign. This is defined in windows-1252, but not latin1.
    bmp = win1252 + u'Ł'  # Polish crossed-L. This requires at least a two-byte encoding.
    utf8 = bmp + u'🐵'  # Monkey-face emoji. This requires at least a three-byte encoding.


@pytest.fixture(scope='module')
def setup():
    import yelp_encodings.internet
    yelp_encodings.internet.register()
pytestmark = pytest.mark.usefixtures("setup")


def test_256bytes():
    all_bytes = ''.join(chr(i) for i in range(256))
    assert 256 == len(all_bytes)

    decoded = all_bytes.decode('internet')
    assert 256 == len(decoded)

    decode_map = dict(zip(all_bytes, decoded))
    assert decode_map['\x80'] == u'\x80'
    assert decode_map['\x81'] == u'\x81'  # The unknown glyph.

    # Raw non-utf8 bytes should decode the same as windows-1252-replace.
    expected = all_bytes.decode('latin1')
    assert expected == decoded

    assert decoded.encode('utf8') == decoded.encode('internet')
    assert decoded == decoded.encode('internet').decode('internet')  # Idempotency.


def test_256bytes_replace():
    all_bytes = ''.join(chr(i) for i in range(256))
    assert 256 == len(all_bytes)

    decoded = all_bytes.decode('internet', 'replace')
    assert 256 == len(decoded)

    decode_map = dict(zip(all_bytes, decoded))
    assert decode_map['\x80'] == u'�'
    assert decode_map['\x81'] == u'�'  # The unknown glyph.

    # Raw non-utf8 bytes should decode the same as windows-1252-replace.
    expected = all_bytes.decode('utf-8', 'replace')
    assert expected == decoded

    assert decoded.encode('utf8') == decoded.encode('internet')
    assert decoded == decoded.encode('internet').decode('internet')  # Idempotency.


def test_win1252bytes():
    win1252_bytes = ''.join(sorted(set(chr(i) for i in range(256)) - set('\x81\x8d\x8f\x90\x9d')))
    assert 251 == len(win1252_bytes)

    decoded = win1252_bytes.decode('internet')
    assert 251 == len(decoded)

    decode_map = dict(zip(win1252_bytes, decoded))
    assert decode_map['\x80'] == u'€'

    # Raw non-utf8 bytes should decode the same as windows-1252-replace.
    expected = win1252_bytes.decode('windows-1252')
    assert expected == decoded

    assert decoded.encode('utf8') == decoded.encode('internet')
    assert decoded == decoded.encode('internet').decode('internet')  # Idempotency.


def test_is_like_utf8():
    encoded = UNICODE.utf8.encode('internet')

    assert UNICODE.utf8.encode('utf8') == encoded
    assert UNICODE.utf8 == encoded.decode('utf8')
    assert UNICODE.utf8 == encoded.decode('internet')


def test_is_like_windows1252():
    encoded = UNICODE.utf8.encode('windows-1252', 'ignore')

    assert UNICODE.win1252.encode('windows-1252') == encoded
    assert UNICODE.win1252 == encoded.decode('internet')


def test_unicode():
    assert UNICODE.utf8.decode('internet') == UNICODE.utf8


def test_incremental_encode():
    from codecs import iterencode
    encoded = iterencode(
        (c for c in UNICODE.utf8),
        'internet'
    )
    encoded = ''.join(encoded)
    assert encoded == UNICODE.utf8.encode('UTF-8')


if __name__ == '__main__':
    import sys
    sys.argv.insert(0, 'py.test')
    exit(pytest.main())
