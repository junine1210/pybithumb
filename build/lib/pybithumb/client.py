from pybithumb.core import *
import math

class Bithumb:
    def __init__(self, conkey, seckey):
        self.api = PrivateApi(conkey, seckey)

    @staticmethod
    def _convert_unit(unit):
        try:
            unit = math.floor(unit * 10000) / 10000
            return unit
        except:
            return 0

    @staticmethod
    def get_tickers():
        """
        빗썸이 지원하는 암호화폐의 리스트
        :return:
        """
        resp = None
        try:
            resp = PublicApi.ticker("ALL")
            data = resp['data']
            tickers = [k for k, v in data.items() if isinstance(v, dict)]
            return tickers
        except Exception:
            return resp

    @staticmethod
    def get_ohlc(currency):
        """
        최근 24시간 내 암호 화폐의 OHLC의 튜플
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : 코인과 (시가, 고가, 저가, 종가) 가 딕셔너리로 저장
          {
            'BTC' : (7020000.0, 7093000.0, 6810000.0, 6971000.0)
            'ETH' : ( 720000.0,  703000.0,  681000.0,  697000.0)
          }
        """
        resp = None
        try:
            resp = PublicApi.ticker(currency)['data']
            if currency is "ALL":
                del resp['date']
                data = {}
                for key in resp:
                        data[key] = (resp[key]['opening_price'], resp[key]['max_price'], resp[key]['min_price'], resp[key]['closing_price'])
                return data

            return {
                currency: (float(resp['opening_price']), float(resp['max_price']), float(resp['min_price']),
                           float(resp['closing_price']))
            }
        except Exception:
            return resp

    @staticmethod
    def get_market_detail(currency):
        """
        거래소 마지막 거래 정보 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : (24시간저가, 24시간고가, 24시간평균거래금액, 24시간거래량)
        """
        resp = None
        try:
            resp = PublicApi.ticker(currency)
            low = resp['data']['min_price']
            high = resp['data']['max_price']
            avg = resp['data']['average_price']
            volume = resp['data']['units_traded']
            return float(low), float(high), float(avg), float(volume)
        except Exception:
            return resp

    @staticmethod
    def get_current_price(currency):
        """
        최종 체결 가격 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : price
        """
        resp = None
        try:
            resp = PublicApi.ticker(currency)
            if currency is not "ALL":
                return float(resp['data']['closing_price'])
            else:
                del resp["data"]['date']
                return resp["data"]
        except Exception:
            return resp

    @staticmethod
    def get_orderbook(currency, limit=5):
        """
        매수/매도 호가 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : 매수/매도 호가
        """
        resp = None
        try:
            limit = min(limit, 20)
            resp = PublicApi.orderbook(currency, limit)
            data = resp['data']
            for idx in range(len(data['bids'])) :
                data['bids'][idx]['quantity'] = float(data['bids'][idx]['quantity'])
                data['asks'][idx]['quantity'] = float(data['asks'][idx]['quantity'])
                data['bids'][idx]['price'] = float(data['bids'][idx]['price'])
                data['asks'][idx]['price'] = float(data['asks'][idx]['price'])
            return data
        except Exception:
            return resp

    def get_trading_fee(self):
        """
        거래 수수료 조회
        :return: 수수료
        """
        resp = None
        try:
            resp = self.api.account()
            return float(resp['data']['trade_fee'])
        except Exception:
            return resp

    def get_balance(self, currency):
        """
        거래소 회원의 잔고 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : (보유코인, 사용중코인, 보유원화, 사용중원화)
        """
        resp = None
        try:
            resp = self.api.balance(currency=currency)
            specifier = currency.lower()
            return (float(resp['data']["available_" + specifier]), float(resp['data']["in_use_" + specifier]),
                    float(resp['data']["available_krw"]), float(resp['data']["in_use_krw"]))
        except Exception:
            return resp

    def get_wallet_address(self, currency):
        resp = None
        try:
            resp = self.api.wallet_address(currency=currency)
            if resp['data']['wallet_address'] != '':
                addr = resp['data']['wallet_address']
                if '&' not in addr:
                    return addr
                else:
                    return addr[:addr.find('&')] + ' / ' + addr[addr.find('=')+1:]
            else:
                return 'https://www.bithumb.com/coin_inout/deposit/' + currency
        except Exception:
            return resp

    def buy_limit_order(self, currency, price, unit):
        """
        매수 주문
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param price   : 주문 가격
        :param unit    : 주문 수량
        :return        : (주문Type, currency, 주문ID)
        """
        resp = None
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.place(type="bid", price=price, units=unit, order_currency=currency)
            return "bid", currency, resp['order_id']
        except Exception:
            return resp

    def sell_limit_order(self, currency, price, unit):
        """
        매도 주문
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param price   : 주문 가격
        :param unit    : 주문 수량
        :return        : (주문Type, currency, 주문ID)
        """
        resp = None
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.place(type="ask", price=price, units=unit, order_currency=currency)
            return "ask", currency, resp['order_id']
        except Exception:
            return resp

    def get_outstanding_order(self, order_desc):
        """
        거래 미체결 수량 조회
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 거래 미체결 수량
        """
        resp = None
        try:
            resp = self.api.orders(type=order_desc[0], order_currency=order_desc[1], order_id=order_desc[2])
            if resp['status'] == '5600':
                return None
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            return resp['data'][0]['units_remaining']
        except Exception:
            return resp

    def get_orders(self, currency):
        resp = None
        try:
            resp = self.api.orders(order_currency=currency)
            if resp['status'] == '5600':
                return {'data':[]}
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            return resp
        except Exception:
            return resp

    def get_order_completed(self, currency, type, order_id):
        """
        거래 완료 정보 조회
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 거래정보
        """
        resp = None
        try:
            resp = self.api.order_detail(type=type, order_currency=currency, order_id=order_id)
            if resp['status'] == '5600':
                return None
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            return resp['data'][0]
        except Exception:
            return resp

    def cancel_order(self, currency, type, order_id):
        resp = None
        try:
            resp = self.api.cancel(type=type, order_currency=currency, order_id=order_id)
            return resp['status'] == '0000'
        except Exception:
            return resp

    def buy_market_order(self, currency, unit):
        """
        시장가 매수
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param unit    : 주문수량
        :return        : 성공 orderID / 실패 메시지
        """
        resp = None
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.market_buy(order_currency=currency, units=unit)
            return resp['order_id']
        except Exception:
            return resp

    def sell_market_order(self, currency, unit):
        """
        시장가 매도
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param unit    : 주문수량
        :return        : 성공 orderID / 실패 메시지
        """
        resp = None
        try:
            unit = Bithumb._convert_unit(unit)
            resp = self.api.market_sell(order_currency=currency, units=unit)
            return resp['order_id']
        except Exception:
            return resp

    def get_withdraw(self, currency, address, unit, destination=None):
        resp = None
        try:
            unit = Bithumb._convert_unit(unit)

            if destination == None:
                resp = self.api.withdraw(currency=currency, address=address, units=unit)
            else:
                resp = self.api.withdraw(currency=currency, address=address, units=unit, destination=destination)

            return resp
        except Exception:
            return resp


if __name__ == "__main__":
    # print(Bithumb.get_tickers())
    # print(Bithumb.get_current_price("BTC"))
    # print(Bithumb.get_current_price("ALL"))

    bithumb = Bithumb()

    addr = bithumb.get_wallet_address('BTC')
    print(addr)
