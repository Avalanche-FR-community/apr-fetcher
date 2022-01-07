from typing import Dict, List, Union

from web3.main import Web3
from ..utils.utils import calculate_lp_token_price, open_contract, blockchain_urls, get_token_price_from_dexs
from ..dapp_apr_fetcher import DappAPRFetcher
from pprint import pprint

class BoofiAPRFetcher(DappAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("avalanche", Web3(Web3.HTTPProvider(blockchain_urls["avalanche"])))
        self._cauldron_contract = open_contract(self._web3, self._blockchain, "0xb178bd23876dd9f8aa60e7fdb0a2209fe2d7a9ab")
        self._token_contract = open_contract(self._web3, self._blockchain, self.dapp_token_address(self._web3))
        # open contract for each pool
        self._pools = {
            token_address: self._cauldron_contract.functions.tokenParameters(
                self._web3.toChecksumAddress(token_address)
            ).call()
            for token_address in (
                self._cauldron_contract.functions.tokenList().call()
            )
        }

    def dapp_pools_infos(self, web3) -> List[Dict[str, Union[str, float]]]:
        return [
            {
                "total_staked": p[7] * 10**(-open_contract(self._web3, self._blockchain, token_address).functions.decimals().call()),
                "pool_address": token_address,
                "alloc_point": p[7] * p[8]*calculate_lp_token_price(self._web3, self._blockchain, token_address),
            } for token_address, p in self._pools.items()
        ]

    def dapp_token_address(self, web3) -> str:
        return self._cauldron_contract.functions.ZBOOFI().call()

    def dapp_token_per_year(self, web3) -> float:
        decimals = self._token_contract.functions.decimals().call()
        return self._cauldron_contract.functions.zboofiPerSecond().call() * 10**(-decimals) * 3600 * 24 * 365

    def dapp_token_total_alloc(self, web3) -> List[Dict[str, Union[str, float]]]:
        return sum([p[7]*p[8]*calculate_lp_token_price(self._web3, self._blockchain, token_address) for token_address, p in self._pools.items()])

    def dapp_token_price(self, web3) -> float:
        boofi_token_address = self._cauldron_contract.functions.BOOFI().call()
        decimals = self._token_contract.functions.decimals().call()
        current_exchange_rate = self._token_contract.functions.currentExchangeRate().call()*10**(-decimals)
        boofi_price = get_token_price_from_dexs(web3, self._blockchain, boofi_token_address)
        return boofi_price*current_exchange_rate
