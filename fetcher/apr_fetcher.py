from abc import ABC, abstractmethod
from typing import Dict, List, Union

class APRFetcher(ABC):
    """
        Interface for apr fetcher
    """

    @abstractmethod
    def pool_aprs(self, sorted_by_apr_desc=True) -> List[Dict[str, Union[int, float, str]]]:
        """
            Fetch pool infos of a given project
            Each pool entry has the following key:value entries:
            "pair": str, gives the name of the pair (or single asset)
            "apr": float, gives the apr of the pool (in %)
            "tvl": float, gives the total value locked (in USDT)
            "infos": dict[str, float|str], might be empty or give additional informations on the pool
            Parameters
            ----------
            sorted_by_apr_desc: bool
            Whether the list is sorted using the apr in descending order
        """
        raise NotImplementedError()
