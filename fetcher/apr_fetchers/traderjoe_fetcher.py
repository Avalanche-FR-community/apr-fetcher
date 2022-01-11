from typing import Dict, List, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs
from ..masterchef_apr_fetcher import MasterchefAPRFetcher
from pprint import pprint

class TraderjoeAPRFetcher(MasterchefAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))

    def masterchef_address(self):
        return "0x188bED1968b795d5c9022F6a0bb5931Ac4c18F00"

    def dapp_token_address_field(self):
        return "JOE"

    def dapp_token_per_block_or_per_second_field(self, per_block: bool):
        return "" if per_block else "joePerSec"

    def _total_staked(self, i, pool_info):
        pool_contract = open_contract(self._web3, self._blockchain, self._pool_address(i, pool_info))
        decimals = pool_contract.functions.decimals().call()
        return open_contract(self._web3, self._blockchain, self._pool_address(i, pool_info)).functions.balanceOf(self._web3.toChecksumAddress(self.masterchef_address())).call() * 10**(-decimals)

    def _pool_address(self, i, pool_info):
        return pool_info[0]

    def _alloc_point(self, i, pool_info):
        return pool_info[3]
