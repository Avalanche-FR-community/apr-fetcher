from typing import Dict, List, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs
from ..dapp_apr_fetcher import DappAPRFetcher
from pprint import pprint

class StakeDAOAPRFetcher(DappAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))
        self._pool_gauge = open_contract(self._web3, self._blockchain, "0x0665eF3556520B21368754Fb644eD3ebF1993AD4")
        self._staking_reward = open_contract(self._web3, self._blockchain, "0x20fa7bdac9bb235c7de5232507eb963048e56b1e")
        self._token_contract = open_contract(self._web3, self._blockchain, self.dapp_token_address(self._web3))
        # open contract for each pool
        self._pools = {
            self.dapp_token_address(self._web3): self._staking_reward.functions.rewardData(self._web3.toChecksumAddress(self.dapp_token_address(self._web3))).call()
        }

    def dapp_pools_infos(self, web3) -> List[Dict[str, Union[str, float]]]:
        return [{
                "total_staked": self._pool_gauge.functions.totalSupply().call() * 10**-self._pool_gauge.functions.decimals().call(),
                "pool_address": self._staking_reward.functions.stakingToken().call(),
                "alloc_point": 1,
                }]

    def dapp_token_address(self, web3) -> str:
        return self._staking_reward.functions.rewardTokens(0).call()

    def dapp_token_per_year(self, web3) -> float:
        decimals = self._token_contract.functions.decimals().call()
        token_per_year = self._staking_reward.functions.rewardData(self._web3.toChecksumAddress(self.dapp_token_address(web3))).call()[3] * 10**(-decimals) * 3600 * 24 * 365
        return token_per_year

    def dapp_token_total_alloc(self, web3) -> List[Dict[str, Union[str, float]]]:
        return len(self._pools.keys())

    def dapp_token_price(self, web3) -> float:
        return get_token_price_from_dexs(web3, self._blockchain, self.dapp_token_address(web3))
