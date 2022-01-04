from web3.main import Web3
from ..api_apr_fetcher import APIAPRFetcher
import json
from ..utils.utils import blockchain_urls, get_token_price_from_dexs, open_contract, blockchain_native_token_address
import warnings
from typing import Dict, List, Union
import urllib.request
from pprint import pprint
from pprint import pprint

class AlphaHomoraAPRFetcher(APIAPRFetcher):
    """
        Interface for apr fetcher
    """

    def __init__(self):
        super().__init__("https://api-homora.alphafinance.io/pools")

    def _pool_aprs_from_api_content(self, api_content) -> List[Dict[str, Union[int, float, str]]]:
        data = json.loads(api_content)
        d = []
        for infos in data["pools"]:
            name = infos["name"].split(" ")
            name = name[1] + f"({name[0].lower()})"
            print(infos)
            apr = float(infos["apr"])
            tvl = float(infos["totalStakedUSD"])
            d.append(
                {
                    "pair": name,
                    "apr": apr,
                    "tvl": max(tvl, -1)
                }
            )
        return d
