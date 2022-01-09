from fetcher.apr_fetchers.alpha_homora_v1_fetcher import AlphaHomoraAPRFetcher
from fetcher.apr_fetchers.beefy_fetcher import BeefyAPRFetcher
from fetcher.apr_fetchers.boofi_fetcher import BoofiAPRFetcher
from fetcher.apr_fetchers.stakedao_fetcher import StakeDAOAPRFetcher
from fetcher.apr_fetchers.swift_fetcher import SwiftAPRFetcher
from fetcher.apr_fetchers.yetiswap_fetcher import YetiswapAPRFetcher
from .yieldyak_fetcher import YieldYakAPRFetcher
from .beefy_fetcher import BeefyAPRFetcher
from .alpha_homora_v1_fetcher import AlphaHomoraAPRFetcher
from .boofi_fetcher import BoofiAPRFetcher
from .swift_fetcher import SwiftAPRFetcher
from .yetiswap_fetcher import YetiswapAPRFetcher
from .stakedao_fetcher import StakeDAOAPRFetcher
from .pangolinv2_fetcher import PangolinV2APRFetcher

fetchers = {
    "yieldyak": YieldYakAPRFetcher(),
    "beefy": BeefyAPRFetcher(),
    "alpha_homora_v1": AlphaHomoraAPRFetcher(),
    "boofi": BoofiAPRFetcher(),
    "swift": SwiftAPRFetcher(),
    "yetiswap": YetiswapAPRFetcher(),
    "stakedao": StakeDAOAPRFetcher(),
    "pangolin": PangolinV2APRFetcher()
}
