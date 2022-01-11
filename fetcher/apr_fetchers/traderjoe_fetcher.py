from typing import Dict, List, Tuple, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs, symbol_mapping
from ..masterchef_apr_fetcher import MasterchefAPRFetcher
from pprint import pprint

class TraderjoeAPRFetcher(MasterchefAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))

    def masterchef_address(self) -> str:
        return "0x188bED1968b795d5c9022F6a0bb5931Ac4c18F00"

    def dapp_token_address_field(self) -> str:
        return "JOE"

    def dapp_token_per_block_or_per_second_field(self, per_block: bool) -> str:
        return "" if per_block else "joePerSec"

    def _total_staked(self, i, pool_info) -> float:
        pool_contract = open_contract(self._web3, self._blockchain, self._pool_address(i, pool_info))
        decimals = pool_contract.functions.decimals().call()
        return open_contract(self._web3, self._blockchain, self._pool_address(i, pool_info)).functions.balanceOf(self._web3.toChecksumAddress(self.masterchef_address())).call() * 10**(-decimals)

    def _pool_address(self, i, pool_info) -> str:
        return pool_info[0]

    def _alloc_point(self, i, pool_info) -> int:
        return pool_info[3]

    def additional_aprs(self, i: int, pool_info: Dict[str, Union[float, int, str]]) -> List[Tuple[str, float]]:
        masterchef_contract = open_contract(self._web3, self._blockchain, self.masterchef_address())
        pool_info_complete = masterchef_contract.functions.poolInfo(i).call()
        rewarder = pool_info_complete[4]
        rewarder_contract = open_contract(self._web3, self._blockchain, rewarder)
        if rewarder_contract.functions.tokenPerSec().call() == 0:
            return []
        reward_token = rewarder_contract.functions.rewardToken().call()
        reward_contract = open_contract(self._web3, self._blockchain, reward_token)
        if "symbol" in dir(reward_contract.functions):
            symbol = reward_contract.functions.symbol().call()
        else:
            symbol = symbol_mapping(reward_token.lower(), reward_token.lower())
        annual_token_emission = rewarder_contract.functions.tokenPerSec().call() * 3600 * 24 * 365
        price_token = calculate_lp_token_price(self._web3, self._blockchain, reward_token)
        lp_token_price = self._pool_address(i, pool_info_complete)
        total_staked = self._total_staked(i, pool_info_complete)
        pool_emission_share = self._alloc_point(i, pool_info_complete) / self.dapp_token_total_alloc(self._web3)
        pool_reward_amount_per_year = annual_token_emission * pool_emission_share
        pool_reward_value_per_year = price_token * pool_reward_amount_per_year
        total_value_locked = max(1, total_staked * lp_token_price)
        apr = ((pool_reward_value_per_year/total_value_locked))*100
        return symbol, apr
