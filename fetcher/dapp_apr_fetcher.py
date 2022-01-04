from abc import abstractmethod
from .apr_fetcher import APRFetcher
from typing import Dict, List, Union, Any
import urllib.request
import json
from .utils.utils import get_block_average_time, get_token_price_from_dexs, open_contract, usdt_address

class DappAPRFetcher(APRFetcher):
    """
        Interface for data-fetching based APR fetcher
    """

    def __init__(self, blockchain, web3):
        self._web3 = web3
        self._blockchain = blockchain

    @abstractmethod
    def pools_infos(self, web3) -> List[Dict[str, Union[str, float]]]:
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_address(self, web3) -> str:
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_per_block(self, web3) -> float:
        raise NotImplementedError()

    @abstractmethod
    def dapp_token_total_alloc(self, web3) -> List[Dict[str, Union[str, float]]]:
        raise NotImplementedError()
    
    def pool_aprs(self, sorted_by_apr_desc=True) -> List[Dict[str, Union[int, float, str]]]:
        """
            TBW
        """
        average_time_per_block_seconds = get_block_average_time(self._web3, span=200)
        block_per_seconds = 1.0 / average_time_per_block_seconds
        block_per_year = block_per_seconds * 3600 * 24 * 365
        token_per_block = self.dapp_token_per_block(self._web3)
        token_address = self.dapp_token_address()
        token_contract = open_contract(self._web3, self._blockchain, token_address)
        decimals = token_contract.functions.decimals().call()
        annual_token_emission = block_per_year * (token_per_block/(10**decimals))
        farms = []
        for pool_info in self._pools_infos(self._web3):
            total_staked = pool_info["total_staked"]
            pool_address = pool_info["pool_address"]
            alloc_point = pool_info["alloc_point"]
            # Compute infos about pool (emission share and reward amount per year)
            pool_emission_share = alloc_point / self.dapp_token_total_alloc(self._web3)
            pool_reward_amount_per_year = annual_token_emission * pool_emission_share
            # Compute price of the dapp token
            price_token = get_token_price_from_dexs(self._web3, self._blockchain, token_address)
            
            # Get price and decimals of a single-asset or LP token
            pool_contract = open_contract(self._web3, self._blockchain, pool_address)
            if "token0" not in dir(pool_contract.functions):
                token0Symbol = pool_contract.functions.symbol().call()
                token1Symbol = pool_contract.functions.symbol().call()
                LPToken_price = get_token_price_from_dexs(self._web3, self._blockchain, pool_address) if pool_address.lower() != usdt_address[self._blockchain].lower() else 1
                LPToken_decimals = pool_contract.functions.decimals().call()
            else:
                token0Address = pool_contract.functions.token0().call()
                token1Address = pool_contract.functions.token1().call()
                token0 = open_contract(self._web3, self._blockchain, token0Address)
                token1 = open_contract(self._web3, self._blockchain, token1Address)
                token_0_price = get_token_price_from_dexs(self._web3, self._blockchain, token0Address) if token0Address.lower() != usdt_address[self._blockchain].lower() else 1
                token_1_price = get_token_price_from_dexs(self._web3, self._blockchain, token1Address) if token1Address.lower() != usdt_address[self._blockchain].lower() else 1
                token0Decimals = token0.functions.decimals().call()
                token1Decimals = token1.functions.decimals().call()
                token0Symbol = token0.functions.symbol().call()
                token1Symbol = token1.functions.symbol().call()
                reserves = pool_contract.functions.getReserves().call()
                reserveToken0 = reserves[0]*10**-(token0Decimals)
                reserveToken1 = reserves[1]*10**-(token1Decimals)
                totalSupply = pool_contract.functions.totalSupply().call()*10**-pool_contract.functions.decimals().call()
                componentLPToken0 = reserveToken0 / totalSupply
                componentLPToken1 = reserveToken1 / totalSupply
                LPToken_price = componentLPToken0 * token_0_price + componentLPToken1 * token_1_price
                LPToken_decimals = pool_contract.functions.decimals().call()
            # Finally, compute farm APR   
            pool_reward_value_per_year = price_token * pool_reward_amount_per_year
            total_value_locked = (total_staked*10**-LPToken_decimals) * LPToken_price
            apr = pool_reward_value_per_year*100/total_value_locked
            token_symbol_tuple = token0Symbol+"/"+token1Symbol if token0Symbol != token1Symbol else token0Symbol
            dict_farm = {
                "pair": token_symbol_tuple,
                "apr": apr,
                "tvl": total_value_locked
            }
            farms.append(dict_farm)
        if sorted_by_apr_desc:
            return sorted(farms, key=lambda x: x["apr"], reverse=True)
        return farms
        
