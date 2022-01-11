from abc import abstractmethod
from .apr_fetcher import APRFetcher
from typing import Dict, List, Tuple, Union, Any
import urllib.request
import json
from .utils.utils import (
    calculate_lp_token_price,
    calculate_special_token_price,
    get_token_price_from_dexs,
    open_contract,
    usdt_address,
    platform_name_mapping,
    decimals_mapping,
    symbol_mapping
)


class DappAPRFetcher(APRFetcher):
    """
        Interface for data-fetching based APR fetcher
    """

    def __init__(self, blockchain, web3):
        self._web3 = web3
        self._blockchain = blockchain

    @abstractmethod
    def dapp_pools_infos(self, web3) -> List[Dict[str, Union[str, float]]]:
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_address(self, web3) -> str:
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_per_year(self, web3) -> float:
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_total_alloc(self, web3) -> List[Dict[str, Union[str, float]]]:
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_price(self, web3) -> float:
        raise NotImplementedError()

    def additional_aprs(self, i: int, pool_info: Dict[str, Union[float, int, str]]) -> List[Tuple[str, float]]:
        return []

    def pool_aprs(self, sorted_by_apr_desc=True) -> List[Dict[str, Union[int, float, str]]]:
        """
            TBW
        """
        price_token = self.dapp_token_price(self._web3)
        annual_token_emission = self.dapp_token_per_year(self._web3)
        farms = []
        dapp_pools_infos = self.dapp_pools_infos(self._web3)
        total_alloc = self.dapp_token_total_alloc(self._web3)
        # Compute price of the dapp token
        for i, pool_info in enumerate(dapp_pools_infos):
            total_staked = pool_info["total_staked"]
            pool_address = pool_info["pool_address"]
            alloc_point = pool_info["alloc_point"]
            if alloc_point == 0:
                continue
            # Compute infos about pool (emission share and reward amount per year)
            pool_emission_share = alloc_point / total_alloc
            pool_reward_amount_per_year = annual_token_emission * pool_emission_share
            # Get price and decimals of a single-asset or LP token
            pool_contract = open_contract(self._web3, self._blockchain, pool_address)
            if "token0" not in dir(pool_contract.functions):
                if "symbol" in dir(pool_contract.functions):
                    token0_symbol = pool_contract.functions.symbol().call()
                    token1_symbol = pool_contract.functions.symbol().call()
                else:
                    token0_symbol = symbol_mapping.get(pool_address, pool_address)
                    token1_symbol = symbol_mapping.get(pool_address, pool_address)
                LPToken_price = get_token_price_from_dexs(self._web3, self._blockchain, pool_address) if pool_address.lower() != usdt_address[self._blockchain].lower() else 1
                if LPToken_price == -1:
                    LPToken_price = calculate_special_token_price(self._web3, self._blockchain, pool_address)
                platform = ""
            else:
                token0_address = pool_contract.functions.token0().call()
                token1_address = pool_contract.functions.token1().call()
                try:
                    token0 = open_contract(self._web3, self._blockchain, token0_address)
                    if "symbol" in dir(token0.functions):
                        token0_symbol = token0.functions.symbol().call()
                    else:
                        token0_symbol = symbol_mapping.get(token0_address.lower(), token0_address.lower())
                except:
                    token0_symbol = symbol_mapping.get(token0_address.lower(), token0_address.lower())

                try:
                    token1 = open_contract(self._web3, self._blockchain, token1_address)
                    if "symbol" in dir(token1.functions):
                        token1_symbol = token1.functions.symbol().call()
                    else:
                        token1_symbol = symbol_mapping.get(token1_address.lower(), token1_address.lower())
                except:
                    token1_symbol = symbol_mapping.get(token1_address.lower(), token1_address.lower())
                LPToken_price = calculate_lp_token_price(self._web3, self._blockchain, pool_address, opened_contract=pool_contract)
                platform = platform_name_mapping.get(pool_contract.functions.symbol().call(), pool_contract.functions.symbol().call())
            # Finally, compute farm APR
            pool_reward_value_per_year = price_token * pool_reward_amount_per_year
            total_value_locked = max(1, total_staked * LPToken_price)
            apr = ((pool_reward_value_per_year/total_value_locked))*100
            token_symbol_tuple = (token0_symbol+"/"+token1_symbol if token0_symbol != token1_symbol else token0_symbol) + (f"({platform})" if platform != "" else "")
            dict_farm = {
                "pair": token_symbol_tuple,
                "apr": apr,
                "tvl": total_value_locked,
                "additional_aprs": [{"pair": reward_token, "apr": apr} for reward_token, apr in self.additional_aprs(i, pool_info)]
            }
            farms.append(dict_farm)
        if sorted_by_apr_desc:
            return sorted(farms, key=lambda x: x["apr"], reverse=True)
        return farms
