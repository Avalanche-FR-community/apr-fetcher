from typing import Dict, List, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs
from ..masterchef_apr_fetcher import MasterchefAPRFetcher
from pprint import pprint

class PangolinV2APRFetcher(MasterchefAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))

    def masterchef_address(self):
        return "0x1f806f7c8ded893fd3cae279191ad7aa3798e928"

    def dapp_token_address_field(self):
        return "REWARD"

    def dapp_token_per_block_or_per_second_field(self, per_block: bool):
        return "" if per_block else "rewardPerSecond"

    def _total_staked(self, i, pool_info):
        pool_contract = open_contract(self._web3, self._blockchain, self._pool_address(i, pool_info))
        decimals = pool_contract.functions.decimals().call()
        return open_contract(self._web3, self._blockchain, self._pool_address(i, pool_info)).functions.balanceOf(self._web3.toChecksumAddress(self.masterchef_address())).call() * 10**(-decimals)

    def _pool_address(self, i, pool_info):
        masterchef_contract = open_contract(self._web3, self._blockchain, self.masterchef_address())
        return masterchef_contract.functions.lpToken(i).call()

    def _alloc_point(self, i, pool_info):
        return pool_info[2]
