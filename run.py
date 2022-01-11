from fetcher.apr_fetchers import fetchers
from pprint import pprint

def run():
    d = {}
    for fetcher_name, fetcher in fetchers.items():
        d = {**d, **{fetcher_name: fetcher.pool_aprs(sorted_by_apr_desc=False)}}
    return d

if __name__ == "__main__":
    pprint(run())
