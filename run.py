from fetcher.apr_fetchers import fetchers

for fetcher_name, fetcher in fetchers.items():
    print(fetcher.pool_aprs(sorted_by_apr_desc=False))
