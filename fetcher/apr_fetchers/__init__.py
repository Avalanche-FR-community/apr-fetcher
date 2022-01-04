from fetcher.apr_fetchers.beefy_fetcher import BeefyAPRFetcher
from .yieldyak_fetcher import YieldYakAPRFetcher
from .beefy_fetcher import BeefyAPRFetcher

fetchers = {
    "yieldyak": YieldYakAPRFetcher(),
    "beefy": BeefyAPRFetcher()
}
