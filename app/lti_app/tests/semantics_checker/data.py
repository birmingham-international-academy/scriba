low_threshold = 0.15
medium_threshold = 0.30
high_threshold = 0.45


similarity_data = [
    (
        "History has a habit of repeating itself through the decades in Europe. In Italy, where communists once held sway, nationalists are now in the ascendancy.",
        'In Italy communists once held sway, however nationalists are rising up.',
        [],
        low_threshold,
        True
    ),
    (
        'Paraphrasing has the essential function of helping the writer to restate the thoughts of another author without replicating them in an exact manner.',
        "One important function of the paraphrase is to help a writer restate another author's ideas without copying them exactly.",
        [],
        low_threshold,
        True
    ),
    (
        'Paraphrasing has the essential function of helping the writer to restate the thoughts of another author without replicating them in an exact manner.',
        "One important function of the paraphrase is to help a writer restate another author's ideas without copying them exactly.",
        ['Helping one writer to express the ideas of another using different words is a key feature in paraphrase.'],
        low_threshold,
        True
    ),
    (
        'An essential task of the paraphrase is to aid a writer in reformulating the thoughts of another author without exact copying.',
        "One important function of the paraphrase is to help a writer restate another author's ideas without copying them exactly.",
        [],
        low_threshold,
        True
    ),
    (
        'Nationalists are repeating history by destroying communism.',
        'History repeats itself throughout the decades in Europe. For example, in Italy the nationalists have risen from a past of communism. Nationalist sentiment is a common feeling in the European Union.',
        [],
        low_threshold,
        False
    ),
    (
        'Keck (2006) mentions the important role that paraphrase plays in enabling writers to express the ideas of others in their own words.',
        'One important function of the paraphrase is to help a writer restate another author’s ideas without copying them exactly.',
        [],
        low_threshold,
        True
    )
]
