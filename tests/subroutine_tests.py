import pytest

from ext_argparse.argproc import unflatten_dict


def test_unflatten_dict():
    test_dict = {
        "hedgehog.lost.in.time": "peter",
        "hedgehog.lost.in.space": "paul",
        "hedgehog.not_lost.head_scratcher": "mary",
        "cool": "house",
        "hedgehog.not_lost.bodyguard": "Arnold Shwartznegger",
        "hedgehog.lost.qualities": "serendipity",
        "hedgehog.animal": True
    }

    unflattened = unflatten_dict(test_dict)

    ground_truth = {
        'hedgehog': {
            'lost': {
                'in': {
                    'time': 'peter',
                    'space': 'paul'
                },
                'qualities': 'serendipity'},
            'not_lost': {
                'head_scratcher': 'mary',
                'bodyguard': 'Arnold Shwartznegger'
            },
            'animal': True
        },
        'cool': 'house'
    }
    assert unflattened == ground_truth
