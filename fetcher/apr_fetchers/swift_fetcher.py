from typing import Dict, List, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs
from ..masterchef_apr_fetcher import MasterchefAPRFetcher
from pprint import pprint

class SwiftAPRFetcher(MasterchefAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))

    def masterchef_address(self):
        return "0x9A03B68b86C06f4cf29530a0780D68FBe01E9aC6"

    def dapp_token_address_field(self):
        return "swiftToken"

    def dapp_token_per_block_field(self):
        return "swiftPerBlock"

    def _total_staked(self, pool_info):
        pool_contract = open_contract(self._web3, self._blockchain, self._pool_address(pool_info))
        token_contract = open_contract(self._web3, self._blockchain, self.dapp_token_address(self._web3))
        decimals = pool_contract.functions.decimals().call()
        return open_contract(self._web3, self._blockchain, self._pool_address(pool_info)).functions.balanceOf(token_contract.functions.owner().call()).call() * 10**(-decimals)

    def _pool_address(self, pool_info):
        return pool_info[0]

    def _alloc_point(self, pool_info):
        return pool_info[1]
