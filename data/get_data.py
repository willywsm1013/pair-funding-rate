import sys
import math
import argparse
import pandas as pd

from tqdm import tqdm
from typing import List, Dict, Any, Optional
from datetime import datetime
from requests import Request, Session, Response
from functools import partial
from multiprocessing.pool import ThreadPool as Pool
"""
    FTX API client code : 
        https://github.com/ftexchange/ftx/blob/master/rest/client.py
"""

class FundingRateCollector():
    _ENDPOINT = 'https://ftx.com/api/' 
    def __init__(self):
        self._session = Session()

    def get_funding_rates(self, 
                          future:str=None, 
                          start_time:int=int(datetime(2019, 2, 1).timestamp()),
                          end_time:int=int(datetime.now().timestamp()),
                          time_step:int=15*24*3600,
                          threads:int=4) -> List[dict]:

        funding_rates = []
        pool = Pool(threads)
        fn = partial(self.get_rates, future=future, time_step=time_step)
        total = math.ceil((end_time-start_time)/time_step)
        iterator = tqdm(pool.imap(fn, range(start_time, end_time, time_step)), total=total)
        for rates, start, end in iterator:
            iterator.set_postfix(time=datetime.fromtimestamp(start))
            funding_rates.extend(rates)
        df = pd.DataFrame(funding_rates).drop_duplicates().sort_values('time').reset_index()[['time', 'rate']]
        return df

    def get_rates(self, start:int, time_step:int, future:str):
        end = start + time_step
        rates = self._get('funding_rates', {
                              'future': future,
                              'start_time': start,
                              'end_time': end
                            })
        return rates, start, end

    def _get(self, path:str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', type=str)
    parser.add_argument('--threads', type=int, default=4)

    args = parser.parse_args()
    symbol = f'{args.symbol.upper()}-PERP'
    print (f'Download funding rate history of {symbol} !')
    collector = FundingRateCollector()
    df = collector.get_funding_rates(symbol,
                                     threads=args.threads)
    print (f'total data num : {len(df)}')
    df.to_csv(f'{symbol}.csv', index=True)
