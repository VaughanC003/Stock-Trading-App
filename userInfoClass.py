class UserInfo:
    def __init__(self, data):
        self.__tickers = data

    def __str__(self):
        return str(self.__tickers)

    def get_tickers(self, ind):
        return self.__tickers[ind]

    def get_all_tickers(self):
        return self.__tickers[:]

    def append(self, tckr):
        self.__tickers.append(tckr)

    def remove_ticker(self, ticker):
        try:
            self.__tickers.remove(ticker.upper())
            print(f"{ticker} removed successfully.")
        except ValueError:
            print(f"{ticker} not found in the list.")

    def remove(self, ticker):
        self.remove_ticker(ticker)

    def __getitem__(self, index):
        return self.__tickers[index]

    def __delitem__(self, index):
        del self.__tickers[index]

    def __len__(self):
        return len(self.__tickers)