import os, sys
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def to_day(date:str) -> str :
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y-%m-%d')
    return date
    

def compute_data(df:pd.DataFrame, symbol:str) -> pd.DataFrame:
    df['diff'] = df[symbol] - df[f'K{symbol}'] 
    df['cumprod'] = (1+df['diff']).cumprod() - 1
    df['-cumprod'] = (1-df['diff']).cumprod() - 1
    df[f'short_{symbol}'] = (1+df[symbol]).cumprod() -1
    df[f'short_K{symbol}'] = (1+df[f'K{symbol}']).cumprod() -1
    return df

def plot_figure(df:pd.DataFrame, output_path:str) -> None:
    plt.figure(figsize = (15,8))

    # plot line
    graph = sns.lineplot(data=df, x='time', y='cumprod', label=f'Short {symbol}, Long K{symbol}')
    sns.lineplot(data=df, x='time', y='-cumprod', label=f'Long {symbol}, Short K{symbol}')
    sns.lineplot(data=df, x='time', y=f'short_{symbol}', label=f'Short {symbol}')
    sns.lineplot(data=df, x='time', y=f'short_K{symbol}', label=f'Short K{symbol}')
    
    # set title
    graph.set(title=f'{symbol} and K{symbol}')

    # set x ticks, only show start date, end date, and max return date
    xticks = [0, max_index, len(df)-1]
    xticklabels = [to_day(df['time'].iloc[x]) for x in xticks]
    graph.set(xticks=xticks, xticklabels=xticklabels)  # remove the tick labels

    # set axis label 
    graph.set(xlabel=None)
    graph.set(ylabel='return')
    graph.legend()

    # plot max return line
    plt.axvline(max_index, color='red', linestyle='dashed')
    plt.xticks(rotation=45)

    plt.savefig(output_path)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('symbol', type=str)
    parser.add_argument('--output_dir', type=str, default='figure')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    return args

if __name__ == '__main__':
    args = get_args()
    symbol = args.symbol.upper()

    # read and merge dataframe
    rate = pd.read_csv(f'data/{symbol}-PERP.csv').rename(columns={'rate':symbol})
    krate = pd.read_csv(f'data/K{symbol}-PERP.csv').rename(columns={'rate':f'K{symbol}'})
    df = rate.merge(krate, how='right', on='time')[['time', symbol, f'K{symbol}']]
    print (f'{symbol} data num : ', len(rate))
    print (f'K{symbol} data num : ', len(krate))
    print (df.head())

    # compute desired data
    df = compute_data(df, symbol)
    df['max'] = df[['cumprod', '-cumprod', f'short_{symbol}', f'short_K{symbol}']].max(axis=1)
    max_index = df['max'].idxmax(axis=0)

    # plot figure
    plot_figure(df, os.path.join(args.output_dir, f'{symbol}-K{symbol}.png'))
