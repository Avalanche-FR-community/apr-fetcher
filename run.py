from fetcher.apr_fetchers import fetchers
from pprint import pprint

for fetcher_name, fetcher in fetchers.items():
    pprint(fetcher.pool_aprs(sorted_by_apr_desc=False))
