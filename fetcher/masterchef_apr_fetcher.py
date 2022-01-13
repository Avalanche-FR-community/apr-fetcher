from abc import abstractmethod
from .apr_fetcher import APRFetcher
from typing import Dict, List, Union, Any
from .dapp_apr_fetcher import DappAPRFetcher
from .utils.utils import (
    calculate_lp_token_price,
    get_block_average_time,
    get_token_price_from_dexs,
    open_contract,
    usdt_address,
    platform_name_mapping,
    decimals_mapping,
    symbol_mapping
)


class MasterchefAPRFetcher(DappAPRFetcher):
    """
        Interface for data-fetching based APR fetcher
    """

    @abstractmethod
    def masterchef_address(self):
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_address_field(self):
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_per_block_or_per_second_field(self, per_block: bool) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _total_staked(self, pool_info):
        raise NotImplementedError()

    @abstractmethod
    def _pool_address(self, pool_info):
        raise NotImplementedError()

    @abstractmethod
    def _alloc_point(self, pool_info):
        raise NotImplementedError()

    def dapp_token_address(self, web3) -> str:
        masterchef_contract = open_contract(self._web3, self._blockchain, self.masterchef_address())
        return getattr(masterchef_contract.functions, self.dapp_token_address_field())().call()

    def dapp_pools_infos(self, web3) -> List[Dict[str, Union[str, float]]]:
        masterchef_contract = open_contract(self._web3, self._blockchain, self.masterchef_address())
        d = []
        for i in range(masterchef_contract.functions.poolLength().call()):
            pool_info = masterchef_contract.functions.poolInfo(i).call()
            d.append({
                "total_staked": self._total_staked(i, pool_info),
                "pool_address": self._pool_address(i, pool_info),
                "alloc_point": self._alloc_point(i, pool_info),
            })
        return d

    def dapp_token_per_year(self, web3) -> float:
        field_per_second = self.dapp_token_per_block_or_per_second_field(per_block=False)
        masterchef_contract = open_contract(self._web3, self._blockchain, self.masterchef_address())
        token_contract = open_contract(web3, self._blockchain, self.dapp_token_address(web3))
        decimals = token_contract.functions.decimals().call()
        if field_per_second is None or field_per_second == "":
            average_time_per_block_seconds = get_block_average_time(web3, span=100)
            block_per_seconds = 1.0 / average_time_per_block_seconds
            block_per_year = block_per_seconds * 3600 * 24 * 365
            token_per_block = getattr(masterchef_contract.functions, self.dapp_token_per_block_field(per_block=True))().call()
            annual_token_emission = block_per_year * (token_per_block/(10**decimals))
        else:
            annual_token_emission = getattr(masterchef_contract.functions, field_per_second)().call() * 10**(-decimals) * 3600 * 24 * 365
        return annual_token_emission

    def dapp_token_total_alloc(self, web3) -> int:
        total_alloc = sum([p["alloc_point"] for p in self.dapp_pools_infos(web3)])
        return total_alloc

    def dapp_token_price(self, web3) -> float:
        return get_token_price_from_dexs(web3, self._blockchain, self.dapp_token_address(web3))
