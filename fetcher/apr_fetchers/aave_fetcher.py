from abc import ABC, abstractmethod
from typing import Dict, List, Union

from web3.main import Web3
from ..apr_fetcher import APRFetcher
from ..utils.utils import blockchain_urls, get_token_price_from_dexs, open_contract


class AaveAPRFetcher(APRFetcher):

    def _pool_aprs(self) -> List[Dict[str, Union[int, float, str]]]:
        blockchain = "avalanche"
        web3 = Web3(Web3.HTTPProvider(blockchain_urls[blockchain]))
        protocol_data_contract = open_contract(web3, blockchain, "0x65285E9dfab318f57051ab2b139ccCf232945451")
        RAY = 10**27
        SECONDS_PER_YEAR = 31536000
        d = []
        for name_token, address in protocol_data_contract.functions.getAllReservesTokens().call():
            token_contract = open_contract(web3, blockchain, address)
            reserve_data = protocol_data_contract.functions.getReserveData(address).call()
            liquidity_rate = reserve_data[3] / RAY
            variable_rate = reserve_data[4] / RAY
            stable_rate = reserve_data[5] / RAY
            decimals = token_contract.functions.decimals().call()
            total_liquidity = reserve_data[0] / 10**decimals
            price = get_token_price_from_dexs(web3, blockchain, address)
            dict_farm = {
                "pair": name_token+"(aave)",
                "apr": 0,
                "tvl": price * total_liquidity,
                "additional_aprs": [("WAVAX", (liquidity_rate + variable_rate + stable_rate)*100)]
            }
            d.append(dict_farm)
        return d
