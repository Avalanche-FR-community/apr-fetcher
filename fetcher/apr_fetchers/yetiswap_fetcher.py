from typing import Dict, List, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs
from ..dapp_apr_fetcher import DappAPRFetcher
from pprint import pprint

class YetiswapAPRFetcher(DappAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))
        self._liqpoolmanager_contract = open_contract(self._web3, self._blockchain, "0x8D1334c3c3F9ba54Ab6d03a3941FB16aB0258180")
        self._token_contract = open_contract(self._web3, self._blockchain, self.dapp_token_address(self._web3))
        # open contract for each pool
        self._pools = {
            self._liqpoolmanager_contract.functions.getPool(
                i
            ).call(): None
            for i in (
                range(self._liqpoolmanager_contract.functions.numPools().call())
            )
        }
        keys = list(self._pools.keys())
        for p in keys:
            try:
                self._pools[p] = open_contract(self._web3, self._blockchain, p)
                self._pools[p].functions.stakingToken().call()
            except:
                del self._pools[p]

    def dapp_pools_infos(self, web3) -> List[Dict[str, Union[str, float]]]:
        return [
            {
                "total_staked": p_contract.functions.totalSupply().call() * 10**-open_contract(self._web3, self._blockchain, self.dapp_token_address(web3)).functions.decimals().call(),
                "pool_address": p_contract.functions.stakingToken().call(),
                "alloc_point": self._liqpoolmanager_contract.functions.rewardAmount(self._web3.toChecksumAddress(p)).call(),
            } for p, p_contract in self._pools.items()
        ]

    def dapp_token_address(self, web3) -> str:
        return self._liqpoolmanager_contract.functions.yts().call()

    def dapp_token_per_year(self, web3) -> float:
        decimals = self._token_contract.functions.decimals().call()
        token_per_year = sum([p_contract.functions.rewardRate().call() for p_contract in self._pools.values()]) * 10**(-decimals) * 3600 * 24 * 365
        return token_per_year

    def dapp_token_total_alloc(self, web3) -> List[Dict[str, Union[str, float]]]:
        return sum([self._liqpoolmanager_contract.functions.rewardAmount(self._web3.toChecksumAddress(p)).call() for p, p_contract in self._pools.items()])

    def dapp_token_price(self, web3) -> float:
        return get_token_price_from_dexs(web3, self._blockchain, self.dapp_token_address(web3))
