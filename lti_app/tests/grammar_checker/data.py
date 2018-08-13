sentence_fragments = [
    (
        'A story with deep thoughts and emotions.',
        ['A story with deep thoughts and emotions.']
    ),
    (
        'Whereas he went to the garden.',
        ['Whereas he went to the garden.']
    ),
    (
        'The cat.',
        ['The cat.']
    ),
    (
        'Whichever assignment.',
        ['Whichever assignment.']
    ),
    (
        'The university offers good courses. Such as electrical, chemical, and industrial engineering.',
        ['Such as electrical, chemical, and industrial engineering.']
    )
]

comma_splices = [
    (
        'Jim usually gets on with everybody, he is an understanding person.',
        ['Jim usually gets on with everybody, he is an understanding person.']
    ),
    (
        'Jim usually gets on with everybody; he is an understanding person.',
        []
    ),
    (
        'The students performed well, they are very motivated.',
        ['The students performed well, they are very motivated.']
    )
]

noun_verb_disagreements = [
    (
        'He are good.',
        ['He are good']
    ),
    (
        'They is very nice. In fact the cat are great.',
        ['They is very nice', 'the cat are great']
    ),
    (
        'I goes to the garden.',
        ['I goes to the garden']
    ),
    (
        'I go to the pitch. However they go to the market.',
        []
    ),
    (
        'Jordan, Michael, and John run and plays. They are good kids.',
        ['Jordan, Michael, and John run and plays']
    ),
    (
        'Jordan and John report that they acquired a plagiarism detection system which gives good results.',
        []
    ),
    (
        'The plagiarism detection system are efficient.',
        ['The plagiarism detection system are efficient']
    )
]
