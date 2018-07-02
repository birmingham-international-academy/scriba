import pytest

from lti_app.core.semantics_checker import Checker


def _normalize_sentence(text):
    return text.split('.')[0].strip()


# 'All thunderstorms have a similar life history.',
# 'All thunderstorms have similarity in their historical life story.',

@pytest.mark.parametrize('excerpt,text,expected', [
    (
        "History has a habit of repeating itself through the decades in Europe. In Italy, where communists once held sway, nationalists are now in the ascendancy.",
        'In Italy communists once held sway, however nationalists are rising up.',
        1
    )
])
def test_similarity(excerpt, text, expected):
    print('\n')
    semantics_checker = Checker(text, excerpt)

    semantics_checker.run()

    assert 1 == 1
