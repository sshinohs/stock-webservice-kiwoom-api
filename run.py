import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import json

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)

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

    def get_name_by_code(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", [code])
        return code_name

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()
    code_list = kiwoom.get_code_list_by_market('0')
    ham = {}
    for code in code_list:
        ham[code] = kiwoom.get_name_by_code(code)
        # print(kiwoom.get_name_by_code(code))
        # print(code, end=" ")
    # print(ham)
    with open('./file/ham.json', 'w') as f:
        f.write(json.dumps(ham, ensure_ascii=False))
        # json.dump(ham, f)