from fetcher.apr_fetchers.alpha_homora_v1_fetcher import AlphaHomoraAPRFetcher
from fetcher.apr_fetchers.beefy_fetcher import BeefyAPRFetcher
from fetcher.apr_fetchers.boofi_fetcher import BoofiAPRFetcher
from fetcher.apr_fetchers.swift_fetcher import SwiftAPRFetcher
from fetcher.apr_fetchers.yetiswap_fetcher import YetiswapAPRFetcher
from .yieldyak_fetcher import YieldYakAPRFetcher
from .beefy_fetcher import BeefyAPRFetcher
from .alpha_homora_v1_fetcher import AlphaHomoraAPRFetcher
from .boofi_fetcher import BoofiAPRFetcher
from .swift_fetcher import SwiftAPRFetcher
from .yetiswap_fetcher import YetiswapAPRFetcher

fetchers = {
    "yieldyak": YieldYakAPRFetcher(),
    "beefy": BeefyAPRFetcher(),
    "alpha_homora_v1": AlphaHomoraAPRFetcher(),
    "boofi": BoofiAPRFetcher(),
    "swift": SwiftAPRFetcher(), # /!\ APRs are bad (are we reading the right contract ? Swift team is not clear on this... e.g., farms having alloc_point of 0 in contract but still having APR in the UI !)
    "yetiswap": YetiswapAPRFetcher()
}
