from app.view_models.book import BookViewModel


class TradeInfo():
    def __init__(self, goods):
        self.total = 0
        self.trades = []
        self.__parse(goods)

    def __parse(self, goods):
        self.total = len(goods)
        self.trades = [self.__map_to_trade(single) for single in goods]

    def __map_to_trade(self, single):
        time = '未知'
        if single.create_time:
            time = single.create_datetime.strftime('%Y-%m-%d')
        return {
            'user_name': single.user.nickname,
            'time': time,
            'id': single.id
        }

class MyTrade():
    def __init__(self, id, book, wishes_count):
        self.id = id
        self.book = book
        self.wishes_count = wishes_count


class MyTrades():
    def __init__(self, trades_of_mine, trade_count_list):
        self.trades = []
        self.__trades_of_mine = trades_of_mine
        self.__trade_count_list = trade_count_list
        self.trades = self.__parse()

    def __parse(self):
        trades = []
        for trade in self.__trades_of_mine:
            temp_trade = self.__parse_single(trade)
            trades.append(temp_trade)
        return trades

    def __parse_single(self, trade):
        count = 0
        for trade_count in self.__trade_count_list:
            if trade.isbn == trade_count['isbn']:
                count = trade_count['count']
                break
        my_trade = MyTrade(trade.id, BookViewModel(trade.book), count)
        return my_trade


