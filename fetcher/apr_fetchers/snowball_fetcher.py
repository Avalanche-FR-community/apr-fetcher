from typing import Dict, List, Union

from web3.main import Web3

from fetcher.apr_fetchers.pangolinv2_fetcher import PangolinV2APRFetcher
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs, decimals_mapping
from ..dapp_apr_fetcher import DappAPRFetcher
from pprint import pprint
import json

defaultABI = '[{"inputs":[{"internalType":"address","name":"_token","type":"address"},{"internalType":"address","name":"_governance","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"reward","type":"uint256"}],"name":"RewardAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"reward","type":"uint256"}],"name":"RewardPaid","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Staked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawn","type":"event"},{"inputs":[],"name":"DISTRIBUTION","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"DURATION","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"SNOWBALL","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"SNOWCONE","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TOKEN","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TREASURY","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"acceptGovernance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_distribution","type":"address"}],"name":"changeDistribution","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"depositAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"account","type":"address"}],"name":"depositFor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"derivedBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"derivedBalances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"derivedSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"earned","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"exit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getRewardForDuration","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"governance","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"kick","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"lastTimeRewardApplicable","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastUpdateTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"reward","type":"uint256"}],"name":"notifyRewardAmount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"pendingGovernance","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"periodFinish","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rewardPerToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rewardPerTokenStored","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rewardRate","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"rewards","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_governance","type":"address"}],"name":"setGovernance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"userRewardPerTokenPaid","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"withdrawAll","outputs":[],"stateMutability":"nonpayable","type":"function"}]'


class SnowballAPRFetcher(DappAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))
        self._gauges_contract = open_contract(self._web3, self._blockchain, "0x215D5eDEb6A6a3f84AE9d72962FEaCCdF815BF27")
        self._token_contract = open_contract(self._web3, self._blockchain, self.dapp_token_address(self._web3))
        # open contract for each pool
        lst_tokens = self._gauges_contract.functions.tokens().call()
        self._pools = {
            token_address: None
            for token_address in (
                lst_tokens
            )
        }
        keys = list(self._pools.keys())
        totalWeight = 0
        for p in keys:
            weight = self._gauges_contract.functions.weights(self._web3.toChecksumAddress(p)).call()
            if weight != 0 and int(self._gauges_contract.functions.deprecated(self._web3.toChecksumAddress(p)).call(), 16) == 0:
                gauge_address = self._gauges_contract.functions.gauges(self._web3.toChecksumAddress(p)).call()
                
                gauge_contract = open_contract(self._web3, self._blockchain, gauge_address)
                if gauge_contract is not None:
                    #gauge_contract = open_contract(self._web3, self._blockchain, gauge_address, providedABI=json.loads(defaultABI))
                    self._pools[p] = gauge_contract
                    totalWeight += weight
                else:
                    self._pools.pop(p)
            else:
                self._pools.pop(p)

    def dapp_pools_infos(self, web3) -> List[Dict[str, Union[str, float]]]:
        pools_infos = []
        for p, p_contract in self._pools.items():
            weight = self._gauges_contract.functions.weights(self._web3.toChecksumAddress(p)).call()
            underlying_pool_contract = open_contract(self._web3, self._blockchain, p_contract.functions.TOKEN().call())
            if underlying_pool_contract is None:
                decimals = decimals_mapping.get(p_contract.functions.TOKEN().call().lower(), 18)
            else:
                decimals = open_contract(self._web3, self._blockchain, p_contract.functions.TOKEN().call()).functions.decimals().call()
            #print(p_contract.functions.totalSupply().call() *  10**-decimals)
            pools_infos.append(
                {
                    "total_staked": p_contract.functions.totalSupply().call() *  10**-decimals,
                    "pool_address": open_contract(self._web3, self._blockchain, p).functions.TOKEN().call(),
                    "alloc_point": weight,
                }
            )
        return pools_infos

    def dapp_token_address(self, web3) -> str:
        return self._gauges_contract.functions.SNOWBALL().call()

    def dapp_token_per_year(self, web3) -> float:
        decimals = self._token_contract.functions.decimals().call()
        token_per_year = sum([p_contract.functions.rewardRate().call() for p_contract in self._pools.values()]) * 10**(-decimals) * 3600 * 24 * 365
        return token_per_year

    def dapp_token_total_alloc(self, web3) -> List[Dict[str, Union[str, float]]]:
        return sum([self._gauges_contract.functions.weights(self._web3.toChecksumAddress(p)).call() for p, _ in self._pools.items()])

    def dapp_token_price(self, web3) -> float:
        return get_token_price_from_dexs(web3, self._blockchain, self.dapp_token_address(web3))

    def adaptAPR(self, i: int, poolInfo: Dict[str, Union[float, int, str]], apr: float):
        # pangolin_fetcher = PangolinV2APRFetcher()
        return apr
