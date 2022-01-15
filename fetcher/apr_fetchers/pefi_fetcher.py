from typing import Dict, List, Tuple, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs, symbol_mapping, decimals_mapping
from ..masterchef_apr_fetcher import MasterchefAPRFetcher
from pprint import pprint

class PefiAPRFetcher(MasterchefAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))

    def masterchef_address(self) -> str:
        return "0x256040dc7b3CECF73a759634fc68aA60EA0D68CB"

    def dapp_token_address_field(self) -> str:
        return "pefi"

    def dapp_token_per_block_or_per_second_field(self, per_block: bool) -> str:
        return "" if per_block else "pefiEmissionPerSecond"

    def _total_staked(self, i, pool_info) -> float:
        pool_contract = open_contract(self._web3, self._blockchain, self._pool_address(i, pool_info))
        decimals = pool_contract.functions.decimals().call()
        return pool_info[-1] * 10**-decimals * pool_info[-2] * 10**-decimals

    def _pool_address(self, i, pool_info) -> str:
        return pool_info[0]

    def _alloc_point(self, i, pool_info) -> int:
        return pool_info[3]

    def additional_aprs(self, i: int, pool_info: Dict[str, Union[float, int, str]]) -> List[Tuple[str, float]]:
        return []
