import requests


URL = 'http://localhost:8081/v2/check'


def check(text):
    r = requests.post(URL, data={
        'text': text,
        'language': 'en-GB',
        'disabledCategories': 'TYPOS'
    })

    return r.json().get('matches', [])
