import yfinance as yf
import matplotlib.pyplot as plt
import yahoo_fin.stock_info as si
import pandas as pd
from userInfoClass import UserInfo
import numpy as np
from scipy.stats import linregress
from datetime import datetime, timedelta
import mplfinance as mpf


def get_financial_ratios(ticker_list):
    try:
        for ticker_symbol in ticker_list:
            print(f"Fetching data for {ticker_symbol}...")
            stock = yf.Ticker(ticker_symbol)
            info = stock.info

            price = info.get('regularMarketPrice')
            eps = info.get('trailingEps')
            pe_ratio = info.get('trailingPE')
            ps_ratio = info.get('priceToSalesTrailing12Months')
            peg_ratio = pe_ratio / eps

            print(f"Ticker: {ticker_symbol}")
            if price is not None:
                print(f"Current Price: ${price}")
            else:
                print("Current Price data not available.")

            if eps is not None:
                print(f"Trailing EPS: ${eps}")
            else:
                print("EPS data not available.")

            if pe_ratio is not None:
                print(f"P/E Ratio: {pe_ratio}")
            else:
                print("P/E Ratio data not available.")

            if ps_ratio is not None:
                print(f"P/S Ratio: {ps_ratio}")
            else:
                print("P/S Ratio data not available.")

            if pe_ratio is not None and ps_ratio is not None:
                if pe_ratio < 15 and ps_ratio < 2:
                    insight = "Potential BUY: undervalued across several metrics."
                elif pe_ratio > 30:
                    insight = "Potential SELL: overvalued based on growth and earnings."
                else:
                    insight = "HOLD: mixed signals. Further research recommended."
            else:
                insight = "Insufficient data to generate buy/sell insight."

            print(f"Insight: {insight}\n")
        main(ticker_list)

    except Exception as e:
        print(f"An error occurred: {e}")


def view_index(tickers):
    sp_list = si.tickers_sp500()
    dow_list = si.tickers_dow()
    while True:
        index_inpt = input("Would you like to see a list of S&P 500 or Dow Jones Index? (SP/DJ/Both): ").strip().upper()

        if index_inpt == 'SP':
            print("Printing S&P 500 tickers... ")
            for tckr in range(0, len(sp_list), 10):
                print(', '.join(sp_list[tckr:tckr + 10]))
        elif index_inpt == 'DJ':
            print("Printing Dow Jones tickers...")
            for tckr in range(0, len(dow_list), 10):
                print(', '.join(dow_list[tckr:tckr + 10]))

        main(tickers)


def search_tickers(searchable_tickers, usr_tickers):
    while True:
        search_name = input("Enter the name of the company you're looking for: ").strip()
        if not search_name:
            print("Company name cannot be empty.")
            continue

        results = searchable_tickers[searchable_tickers['Name'].str.contains(search_name, case=False, na=False)]

        if results.empty:
            print("No matches found.")
        else:
            print("\nMatches found:")
            print(results[['Symbol', 'Name']].head(10).to_string(index=False))

            selected = input("Enter the ticker symbol to add (or press Enter to skip): ").strip().upper()
            if selected and selected in results['Symbol'].values:
                usr_tickers.append(selected)
                print(f"Added: {selected}")
            else:
                print("No ticker added.")

        main(usr_tickers)

        again = input("Search for another company? (Y/N): ").strip().upper()
        if again != 'Y':
            break



def delete_ticker_menu(usr_tickers):
    while True:
        print("\nCurrent Tickers:", usr_tickers)
        ticker = input("Enter the ticker you want to remove: ").strip().upper()
        usr_tickers.remove(ticker)

        # if len(usr_tickers) == 0:
        #     print("All tickers removed.")
        #     main(usr_tickers)

        again = input("Remove another? (Y/N): ").strip().upper()
        if again != 'Y':
            main(usr_tickers)


def get_candlestick_graph(tickers_list):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    for ticker_symbol in tickers_list:
        try:
            data = yf.download(ticker_symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            data = data.tail(120)

            if data.empty:
                print(f"No data found for {ticker_symbol}")
                continue

            if isinstance(data.columns, pd.MultiIndex):
                data = data.xs(ticker_symbol, axis=1, level=1)

            required_cols = ["Open", "High", "Low", "Close"]

            data_clean = data.dropna(subset=required_cols)
            for col in required_cols:
                data_clean[col] = pd.to_numeric(data_clean[col], errors='coerce')

            data_clean.index = pd.to_datetime(data_clean.index)

            mpf.plot(data_clean, type='candle', style='charles', title=ticker_symbol, volume=True)

        except Exception as e:
            print(f"Error plotting {ticker_symbol}: {e}")



def usr_graphs(usr_tickers):
    try:
        while True:
            start_year = input("Enter a start year (YYYY): ").strip()
            end_year = input("Enter an end year (YYYY or type 'current'): ").strip().lower()
            if start_year.isdigit() and (end_year.isdigit() or end_year == 'current'):
                if end_year == 'current':
                    end_date = datetime.today().strftime('%Y-%m-%d')
                    end_year_int = datetime.today().year
                else:
                    end_date = f"{end_year}-12-31"
                    end_year_int = int(end_year)
                if int(start_year) < end_year_int:
                    break
            print("Invalid input. Make sure start year is before end year.")

        print("What would you like to visualize?")
        print("1 - High\n2 - Low\n3 - Open\n4 - Close\n5 - High-Low Difference\n6 - Close-Open Difference\n7 - Percent Change\n8 - Candlestick Graph")

        input_options = {
            '1': 'High',
            '2': 'Low',
            '3': 'Open',
            '4': 'Close',
            '5': 'High-low difference',
            '6': 'Close-open difference',
            '7': 'Percent change',
            '8': 'Candlestick'
        }

        while True:
            selection = input("Enter the number of your choice (1-8): ").strip()
            if selection in input_options:
                data_input = input_options[selection]
                break
            print("Invalid input. Please enter a number from 1 to 8.")

        tickers_list = [usr_tickers.get_tickers(i) for i in range(len(usr_tickers))]

        if data_input == 'Candlestick':
            get_candlestick_graph(usr_tickers)
            main(usr_tickers)

        while True:
            mode = input("How would you like to group the data?\n"
                         "1 - Graph values by a specific month across years\n"
                         "2 - Graph average values for every month from start year to end year\n"
                         "Enter 1 or 2: ").strip()
            if mode in ['1', '2']:
                break
            print("Invalid selection. Please enter 1 or 2.")

        if mode == '1':
            while True:
                month = input("Enter a month (1-12): ").strip()
                if month.isdigit() and 1 <= int(month) <= 12:
                    usr_month = int(month)
                    break
                print("Invalid month. Please enter a number between 1 and 12.")

        all_data = []

        if len(usr_tickers) == 1:
            ticker_string = usr_tickers.get_tickers(0)
            tickers_list = [ticker_string]
        else:
            tickers_list = [usr_tickers.get_tickers(i) for i in range(len(usr_tickers))]
            ticker_string = tickers_list

        for year in range(int(start_year), end_year_int + 1):
            if year == end_year_int and end_year == 'current':
                data = yf.download(ticker_string, start=f'{year}-01-01', end=end_date)
            else:
                data = yf.download(ticker_string, start=f'{year}-01-01', end=f'{year}-12-31')

            if data.empty:
                print(f"Warning: No data found for {ticker_string} in {year}. Skipping.")
                continue

            data.index = pd.to_datetime(data.index)

            for ticker in tickers_list:
                try:
                    if isinstance(data.columns, pd.MultiIndex):
                        high = data['High', ticker]
                        low = data['Low', ticker]
                        open_ = data['Open', ticker]
                        close = data['Close', ticker]
                    else:
                        high = data['High']
                        low = data['Low']
                        open_ = data['Open']
                        close = data['Close']

                    if data_input == 'High-low difference':
                        daily_values = high - low
                        label = "High-Low Diff"
                    elif data_input == 'Close-open difference':
                        daily_values = close - open_
                        label = "Close-Open Diff"
                    elif data_input == 'Percent change':
                        daily_values = ((close - open_) / open_) * 100
                        label = "Percent Change"
                    else:
                        daily_values = eval(data_input.lower())
                        label = f'{data_input} Value'

                    if mode == '1':
                        filtered = daily_values[daily_values.index.month == usr_month]
                        avg_value = filtered.mean()
                        if not pd.isna(avg_value):
                            all_data.append((year, ticker, avg_value))
                    else:
                        monthly_avg = daily_values.groupby(daily_values.index.month).mean()
                        for month_num, avg_val in monthly_avg.items():
                            if not pd.isna(avg_val):
                                all_data.append((f"{year}-{month_num:02d}", ticker, avg_val))
                except KeyError:
                    print(f"Data not found for {ticker} in {year}. Skipping.")
                    continue

        if not all_data:
            raise ValueError("No valid data available for the specified time range and selection.")

        df = pd.DataFrame(all_data, columns=['Year', 'Ticker', label])

        for ticker in df['Ticker'].unique():
            ticker_data = df[df['Ticker'] == ticker]
            x = np.arange(len(ticker_data))
            y = ticker_data[label].values
            slope, _, _, _, _ = linregress(x, y)
            trend_message = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
            print(f"Trend for {ticker}: {trend_message} trend based on {label}.")

        df.set_index(['Year', 'Ticker'], inplace=True)
        df[label] = pd.to_numeric(df[label], errors='coerce')
        df.unstack('Ticker')[label].plot(marker='o', linestyle='-')
        plt.xlabel('Year' if mode == '1' else 'Year-Month')
        plt.ylabel(label, fontsize=14)
        plt.title(f"{label} for {', '.join(tickers_list)} ")
        plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
        plt.xticks(rotation=45)
        plt.legend(title="Ticker")
        plt.tight_layout()
        plt.show()

        main(usr_tickers)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def usr_inputs(usr_tickers):
    while True:
        usr_ticker = input("Enter a stock ticker: ").strip().upper()
        if usr_ticker:
            usr_tickers.append(usr_ticker)
        else:
            print("Ticker cannot be empty.")
            continue

        while True:
            ask = input("Enter more? (Y/N): ").strip().upper()
            if ask in ['Y', 'N']:
                break
            print("Invalid input. Enter 'Y' or 'N'.")
        if ask == 'N':
            break

    back_inp = input('Would you like to go on to analysis (Y/N)' ).strip().upper()

    if back_inp == 'Y':
        usr_graphs(usr_tickers)
    else:
        main(usr_tickers)




def main(user_info):
    try:
        usr_tickers = UserInfo(user_info)
        searchable_tickers = pd.read_csv('nasdaq_screener_1745356200527.csv')
        print('---------------------------')
        print(usr_tickers)
        print('Type number for action: ')
        print('1. Add Ticker\n'
              '2. Delete Ticker\n'
              '3. Search Ticker\n'
              '4. View S&P 500 or DOW-J list\n'
              '5. Visualize tickers\n'
              '6. Get Current price and financial ratios of tickers\n ')
        print('---------------------------')

        # example = yf.download("AAPL",start=f'2020-01-01', end=f'2025-03-31')
        # fp = open("example.csv", "w")
        # example.to_csv(fp)
        num = input('What would you like? ')
        if num == str(1):
            usr_inputs(usr_tickers)
        elif num == str(2):
            delete_ticker_menu(usr_tickers)
        elif num == str(3):
            search_tickers(searchable_tickers, usr_tickers)
        elif num == str(4):
            view_index(usr_tickers)
        elif num == str(5):
            usr_graphs(usr_tickers)
        else:
            get_financial_ratios(usr_tickers)




    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    default = []
    main(default)
