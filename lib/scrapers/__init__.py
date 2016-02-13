from tornado import gen
from collections import defaultdict

from .sample_scraper import SampleScraper


scrapers = [
    SampleScraper()
]


@gen.coroutine
def scrape(user_data):
    results = yield [s.scrape(user_data) for s in scrapers]
    data = defaultdict(list)
    for result in results:
        for key, values in result.items():
            data[key].append(values)
    return data