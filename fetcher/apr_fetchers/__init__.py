from fetcher.apr_fetchers.alpha_homora_v1_fetcher import AlphaHomoraAPRFetcher
from fetcher.apr_fetchers.beefy_fetcher import BeefyAPRFetcher
from .yieldyak_fetcher import YieldYakAPRFetcher
from .beefy_fetcher import BeefyAPRFetcher
from .alpha_homora_v1_fetcher import AlphaHomoraAPRFetcher

fetchers = {
    #"yieldyak": YieldYakAPRFetcher(),
    #"beefy": BeefyAPRFetcher(),
    "alpha_homora_v1": AlphaHomoraAPRFetcher()
}
