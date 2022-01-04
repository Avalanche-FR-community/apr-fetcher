from web3.main import Web3
from ..api_apr_fetcher import APIAPRFetcher
import json
from ..utils.utils import blockchain_urls, get_token_price_from_dexs, open_contract
import warnings
from typing import Dict, List, Union
import urllib.request

NAME_PER_ADDRESS = {
    "0x969BC610C2237B2131595C1ED0e96233Fc5e1832": "AVAX-XAVA (PANGOLIN)"
}

class YieldYakAPRFetcher(APIAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("https://staging-api.yieldyak.com/apys")

    def _pool_aprs_from_api_content(self, api_content) -> List[Dict[str, Union[int, float, str]]]:
        data = json.loads(api_content)
        complete_data = json.loads(urllib.request.urlopen("https://staging-api.yieldyak.com/farms").read())
        complete_data = {
            d["address"]:d for d in complete_data
        }
        d = []
        web3 = Web3(Web3.HTTPProvider(blockchain_urls["avalanche"]))
        for address, infos in data.items():
            name = complete_data[address]["name"] + f"({complete_data[address]['platform']})"
            tvl = -1
            if len(complete_data[address]["depositToken"]["underlying"]) == 1:
                address_token = complete_data[address]["depositToken"]["address"]
                if complete_data[address]["depositToken"]["symbol"] == "AVAX":
                    address_token = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
                price_token = get_token_price_from_dexs(web3, "avalanche", address_token)
                tvl = price_token * float(complete_data[address]["totalDeposits"])
            elif len(complete_data[address]["depositToken"]["underlying"]) == 2:
                address_token_0 = complete_data[address]["depositToken"]["underlying"][0]
                address_token_1 = complete_data[address]["depositToken"]["underlying"][1]
                price_token_0 = get_token_price_from_dexs(web3, "avalanche", address_token_0)
                price_token_1 = get_token_price_from_dexs(web3, "avalanche", address_token_1)
                try:
                    lp_contract = open_contract(
                        web3, "avalanche", complete_data[address]["depositToken"]["address"]
                    )
                    address_token_0_lp = lp_contract.functions.token0().call()
                    reserves_lp = lp_contract.functions.getReserves().call()
                    lp_token_supply = lp_contract.functions.totalSupply().call() * 10**(-lp_contract.functions.decimals().call())
                    reserves_lp[0] *= 10**(-complete_data[address]["token0"]["decimals"])
                    reserves_lp[1] *= 10**(-complete_data[address]["token1"]["decimals"])
                except:
                    reserves_lp = [float(complete_data[address]["token0"]["reserves"]), float(complete_data[address]["token1"]["reserves"])]
                    token_0_symbol = open_contract(web3, "avalanche", complete_data[address]["depositToken"]["underlying"][0]).functions.symbol().call()
                    if token_0_symbol == complete_data[address]["token0"]["symbol"]:
                        address_token_0_lp = address_token_0
                    else:
                        address_token_0_lp = address_token_1
                    lp_token_supply = float(complete_data[address]["lpToken"]["supply"])
                
                if complete_data[address]["depositToken"]["underlying"][0] == address_token_0_lp:
                    reserves_token_0 = reserves_lp[0] 
                    reserves_token_1 = reserves_lp[1]
                else:
                    reserves_token_0 = reserves_lp[1]
                    reserves_token_1 = reserves_lp[0]
                
                price_lp_token = (reserves_token_0*price_token_0/lp_token_supply) + (reserves_token_1*price_token_1/lp_token_supply)
                tvl = price_lp_token * float(complete_data[address]["totalDeposits"])
            elif len(complete_data[address]["depositToken"]["underlying"]) == 3:
                tvl = float(complete_data[address]["totalDeposits"]) if complete_data[address]["depositToken"]["stablecoin"] else -1          
            d.append(
                {
                    "pair": name,
                    "apr": float(infos["apr"]),
                    "tvl": max(tvl, -1)
                }
            )
        return d
