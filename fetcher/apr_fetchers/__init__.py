
from fetcher.apr_fetchers.traderjoe_fetcher import TraderjoeAPRFetcher
from .snowball_fetcher import SnowballAPRFetcher
from .yieldyak_fetcher import YieldYakAPRFetcher
from .beefy_fetcher import BeefyAPRFetcher
from .alpha_homora_v1_fetcher import AlphaHomoraAPRFetcher
from .boofi_fetcher import BoofiAPRFetcher
from .swift_fetcher import SwiftAPRFetcher
from .yetiswap_fetcher import YetiswapAPRFetcher
from .stakedao_fetcher import StakeDAOAPRFetcher
from .pangolinv2_fetcher import PangolinV2APRFetcher
from .traderjoe_fetcher import TraderjoeAPRFetcher

fetchers = {
    # "yieldyak": YieldYakAPRFetcher(),
    # "beefy": BeefyAPRFetcher(),
    # "alpha_homora_v1": AlphaHomoraAPRFetcher(),
    # "boofi": BoofiAPRFetcher(),
    # "swift": SwiftAPRFetcher(),
    # "yetiswap": YetiswapAPRFetcher(),
    # "stakedao": StakeDAOAPRFetcher(),
    # "pangolin": PangolinV2APRFetcher(),
    "traderjoe": TraderjoeAPRFetcher(),
    # "snowball": SnowballAPRFetcher()
}
