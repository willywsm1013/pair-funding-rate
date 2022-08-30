import sys
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from requests import Request, Session, Response
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
                          verbose=False) -> List[dict]:

        current = datetime.now().timestamp()
        start_time = datetime(2019, 2, 1).timestamp()
        funding_rates = []

        while start_time < current:
            end_time = start_time + 15*24*3600
            if verbose:
                print (datetime.fromtimestamp(start_time), datetime.fromtimestamp(end_time), end='\r')
            rates = self._get('funding_rates', {
                                  'future': future,
                                  'start_time': start_time,
                                  'end_time': end_time
                                })
            funding_rates.extend(rates)
            start_time = end_time
        df = pd.DataFrame(funding_rates).drop_duplicates().sort_values('time').reset_index()[['time', 'rate']]
        return df

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
    symbol = f'{sys.argv[1].upper()}-PERP'
    print (f'Download funding rate history of {symbol} !')
    collector = FundingRateCollector()
    df = collector.get_funding_rates(symbol, verbose=True)
    print()
    print (f'total data num : {len(df)}')
    df.to_csv(f'{symbol}.csv', index=True)
