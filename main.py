import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def to_day(date:str) -> str :
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y-%m-%d')
    return date
    
if __name__ == '__main__':
    symbol = sys.argv[1].upper()

    rate = pd.read_csv(f'data/{symbol}-PERP.csv').rename(columns={'rate':symbol})
    krate = pd.read_csv(f'data/K{symbol}-PERP.csv').rename(columns={'rate':f'K{symbol}'})
    print (f'{symbol} data num : ', len(rate))
    print (f'K{symbol} data num : ', len(krate))

    df = rate.merge(krate, how='right', on='time')
    df['diff'] = df[symbol] - df[f'K{symbol}'] 
    print (df.head())
    df['cumprod'] = (1+df['diff']).cumprod() - 1
    df['-cumprod'] = (1-df['diff']).cumprod() - 1
    df[f'short_{symbol}'] = (1+df[symbol]).cumprod() -1
    df[f'short_K{symbol}'] = (1+df[f'K{symbol}']).cumprod() -1
    df['max'] = df[['cumprod', '-cumprod', f'short_{symbol}', f'short_K{symbol}']].max(axis=1)
    max_index = df['max'].idxmax(axis=0)

    graph = sns.lineplot(data=df, x='time', y='cumprod', label=f'Short {symbol}, Long K{symbol}')
    sns.lineplot(data=df, x='time', y='-cumprod', label=f'Long {symbol}, Short K{symbol}')
    sns.lineplot(data=df, x='time', y=f'short_{symbol}', label=f'short_{symbol}')
    sns.lineplot(data=df, x='time', y=f'short_K{symbol}', label=f'short_K{symbol}')
    
    graph.set(title=f'{symbol} and K{symbol}')
    xticks = [0, max_index, len(df)-1]
    xticklabels = [to_day(df['time'].iloc[x]) for x in xticks]
    graph.set(xticks=xticks, xticklabels=xticklabels)  # remove the tick labels
    graph.legend()
    plt.axvline(max_index, color='red', linestyle='dashed')
    plt.show()

