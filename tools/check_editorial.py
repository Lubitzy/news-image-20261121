"""Validate a revision's editorial data before rendering.

Source dates and short claims are reviewed against reporting by the agent;
these checks enforce declared provenance but do not prove truth by themselves.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def check(stories):
    assert 12 <= len(stories) <= 18, 'Use a curated, bounded story set.'
    assert len({s['id'] for s in stories}) == len(stories), 'Duplicate story IDs.'
    for story in stories:
        for field in ['id', 'region', 'geography', 'key', 'title', 'deck', 'brief', 'sources', 'evidence']:
            assert story.get(field), f'Missing {field}: {story.get("id")}'
        assert story['event_date'] == '2026-11-21', 'Wrong date.'
        assert story.get('verified') is True, 'Unreviewed source.'
        assert isinstance(story['evidence'], list) and story['evidence']
        for source in story['evidence']:
            assert source.get('url') and source.get('supports') and source.get('publication_date')
            host = (urlparse(source['url']).hostname or '').lower()
            assert host and 'make.fun' not in host, 'Competitor feed is not news evidence.'
        assert len(story['title']) <= 42, 'Headline not concise.'
        assert len(story['deck']) <= 140, 'Deck too verbose.'
        assert len(story['brief']) <= 104, 'Brief too verbose.'
    regions=sorted({s['geography'] for s in stories})
    assert len(regions) >= 6, 'Insufficient declared geographic breadth.'
    return {'status':'pass', 'stories':len(stories), 'geographic_groups':regions,
            'source_records':sum(len(s['evidence']) for s in stories),
            'limitation':'Structural validation; facts require source review.'}


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stories', type=Path)
    args=ap.parse_args()
    data=json.loads(args.stories.read_text(encoding='utf-8'))
    print(json.dumps(check(data),indent=2))
