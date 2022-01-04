from web3.main import Web3
from ..api_apr_fetcher import APIAPRFetcher
import json
from ..utils.utils import blockchain_urls, get_token_price_from_dexs, open_contract, blockchain_native_token_address
import warnings
from typing import Dict, List, Union
import urllib.request
from pprint import pprint

class BeefyAPRFetcher(APIAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("https://api.beefy.finance/apy/breakdown")

    def _pool_aprs_from_api_content(self, api_content) -> List[Dict[str, Union[int, float, str]]]:
        data = json.loads(api_content)
        req = urllib.request.Request("https://api.beefy.finance/vaults", headers={'User-Agent': 'Mozilla/5.0'})
        complete_data = json.loads(urllib.request.urlopen(req).read())
        req = urllib.request.Request("https://api.beefy.finance/tvl", headers={'User-Agent': 'Mozilla/5.0'})
        tvl_raw_data = json.loads(urllib.request.urlopen(req).read())
        complete_data = {
            d["id"]:d for d in complete_data
        }
        tvl_data = {}
        if tvl_raw_data != {}:
            for _, d in tvl_raw_data.items():
                for k, v in d.items():
                    tvl_data[k] = v
        d = []
        web3 = Web3(Web3.HTTPProvider(blockchain_urls["avalanche"]))
        for id, infos in data.items():
            if id in complete_data:
                name = "/".join(complete_data[id]["assets"]) + f"({complete_data[id]['platform'].lower()})"
            else:
                continue
            if complete_data[id]["chain"] != "avax":
                continue
            if complete_data[id]["name"] == "AVAX":
                token_address = blockchain_native_token_address["avalanche"]
            else:
                token_address = complete_data[id]["tokenAddress"]
            earn_contract = open_contract(
                web3, "avalanche", complete_data[id]["earnContractAddress"]
            )
            
            if id not in tvl_data:
                if len(complete_data[id]["assets"]) == 2:
                    lp_contract = open_contract(
                        web3, "avalanche", token_address
                    )
                    total_vault_supply = earn_contract.functions.balance().call() * 10**(-lp_contract.functions.decimals().call())
                    address_token_0_lp = lp_contract.functions.token0().call()
                    address_token_1_lp = lp_contract.functions.token1().call()
                    token0 = open_contract(web3, "avalanche", address_token_0_lp)
                    token1 = open_contract(web3, "avalanche", address_token_1_lp)
                    token0_decimals = token0.functions.decimals().call()
                    token1_decimals = token1.functions.decimals().call()
                    reserves_lp = lp_contract.functions.getReserves().call()
                    reserves_token_0 = reserves_lp[0] * 10**(-token0_decimals)
                    reserves_token_1 = reserves_lp[1] * 10**(-token1_decimals)
                    total_lp_supply = lp_contract.functions.totalSupply().call() * 10**(-lp_contract.functions.decimals().call())
                    price_token_0 = get_token_price_from_dexs(web3, "avalanche", address_token_0_lp)
                    price_token_1 = get_token_price_from_dexs(web3, "avalanche", address_token_1_lp)
                    price_lp_token = (reserves_token_0*price_token_0/total_lp_supply) + (reserves_token_1*price_token_1/total_lp_supply)
                elif len(complete_data[id]["assets"]) > 2:
                    total_vault_supply = earn_contract.functions.balance().call() * 10**(-earn_contract.functions.decimals().call())
                    price_lp_token = 1
                else:
                    price_lp_token = get_token_price_from_dexs(web3, "avalanche", token_address)
                    token_contract = open_contract(
                        web3, "avalanche", token_address
                    )
                    total_vault_supply = earn_contract.functions.balance().call() * 10**(-token_contract.functions.decimals().call())

                tvl = price_lp_token * total_vault_supply
            else:
                tvl = tvl_data[id]
            tradingApr = -1 if ("tradingApr" not in infos or infos["tradingApr"] is None) else infos.get("tradingApr", 0)
            vaultApr = -1 if ("vaultApr" not in infos or infos["vaultApr"] is None) else infos.get("vaultApr", 0)
            totalApy = -1 if ("totalApy" not in infos or infos["totalApy"] is None) else infos.get("totalApy", 0)
            d.append(
                {
                    "pair": name,
                    "apr": ((float(vaultApr) + float(tradingApr)) if vaultApr != -1 else float(totalApy))*100,
                    "tvl": max(tvl, -1)
                }
            )
        return d
