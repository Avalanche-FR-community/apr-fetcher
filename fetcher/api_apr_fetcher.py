from abc import abstractmethod
from .apr_fetcher import APRFetcher
from typing import Dict, List, Union
import urllib.request
import json
from urllib.request import Request, urlopen

class APIAPRFetcher(APRFetcher):
    """
        Interface for API-based APR fetcher
    """

    def __init__(self, api_link):
        self._api_link = api_link

    @abstractmethod
    def _pool_aprs_from_api_content(self, api_content) -> List[Dict[str, Union[int, float, str]]]:
        raise NotImplementedError()

    
    def pool_aprs(self, sorted_by_apr_desc=True) -> List[Dict[str, Union[int, float, str]]]:
        """
            Fetch pool aprs (and tvls) of a given project
            Parameters
            ----------
            sorted_by_apr_desc: bool
            Whether the list is sorted using the apr in descending order
        """
        req = Request(self._api_link, headers={'User-Agent': 'Mozilla/5.0'})
        lst = self._pool_aprs_from_api_content(urllib.request.urlopen(req).read())
        lst = [{**d, **{"additional_aprs": []}} for d in lst if "additional_aprs" not in d]
        if sorted_by_apr_desc:
            return sorted(lst, key=lambda x: x["apr"], reverse=True)
        return lst
