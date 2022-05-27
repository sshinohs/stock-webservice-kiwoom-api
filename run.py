import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import json
import time
import pandas as pd

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date_val = self._comm_get_data(trcode, "", rqname, i, "일자")
            open_val = self._comm_get_data(trcode, "", rqname, i, "시가")
            high_val = self._comm_get_data(trcode, "", rqname, i, "고가")
            low_val = self._comm_get_data(trcode, "", rqname, i, "저가")
            close_val = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume_val = self._comm_get_data(trcode, "", rqname, i, "거래량")
            # print(date_val, open_val, high_val, low_val, close_val, volume_val)

            self.ohlcv['date'].append(date_val)
            self.ohlcv['open'].append(int(open_val))
            self.ohlcv['high'].append(int(high_val))
            self.ohlcv['low'].append(int(low_val))
            self.ohlcv['close'].append(int(close_val))
            self.ohlcv['volume'].append(int(volume_val))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

    item_code = "005930"
    recent_date = "20220527"

    # opt 10081 TR 요청
    kiwoom.set_input_value("종목코드", item_code)
    kiwoom.set_input_value("기준일자", recent_date)
    kiwoom.set_input_value("수정주가구분", 1)
    kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

    while kiwoom.remained_data == True:
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.set_input_value("종목코드", item_code)
        kiwoom.set_input_value("기준일자", recent_date)
        kiwoom.set_input_value("수정주가구분", 1)
        kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

    print('why')
    df = pd.DataFrame(kiwoom.ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df.to_json('삼성전자.json', orient='records')

    print('the end')


    # code_list = kiwoom.get_code_list_by_market('0')
    # ham = {}
    # for code in code_list:
    #     ham[code] = kiwoom.get_master_code_name(code)
    # with open('./file/ham.json', 'w') as f:
    #     f.write(json.dumps(ham, ensure_ascii=False))