
from .benqi_fetcher import BenQIAPRFetcher
from .traderjoe_fetcher import TraderjoeAPRFetcher
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
from .axial_fetcher import AxialAPRFetcher

fetchers = {
    "yieldyak": YieldYakAPRFetcher(),
    "beefy": BeefyAPRFetcher(),
    "alpha_homora_v1": AlphaHomoraAPRFetcher(),
    "boofi": BoofiAPRFetcher(),
    "swift": SwiftAPRFetcher(),
    "yetiswap": YetiswapAPRFetcher(),
    "stakedao": StakeDAOAPRFetcher(),
    "pangolin": PangolinV2APRFetcher(),
    "traderjoe": TraderjoeAPRFetcher(),
    "axial": AxialAPRFetcher(),
    "snowball": SnowballAPRFetcher(),
    "benqi": BenQIAPRFetcher()
}
