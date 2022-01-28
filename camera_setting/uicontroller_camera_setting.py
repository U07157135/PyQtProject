from Ui_CameraSetting import Ui_CameraSetting
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtWidgets import QDialog,QApplication
from PyQt5.QtGui import QFont


class CameraSetting(Ui_CameraSetting):
    def __init__(self,dialog):
        super().__init__()
        self.setupUi(dialog)
        self.change_ui_uvc_cam()
        self.event_connector()
        
    def event_connector(self):
        self.combobox_camera.currentIndexChanged.connect(self.combobox_update_ui)

    def combobox_update_ui(self):
        index = self.combobox_camera.currentIndex()
        if index == 0:
            self.change_ui_uvc_cam()
        elif index == 1:
            self.change_ui_ip_cam()
        else:
            self.change_ui_other_cam()

    def change_ui_uvc_cam(self):
        self.label_resolution_h.show()
        self.lineedit_resolution_h.show()
        self.label_resolution_w.show()
        self.lineedit_resolution_w.show()

        self.label_usb_port.show()
        self.combobox_camera_usb_port.show()
        self.btn_scan.show()

        self.label_streamurl.hide()
        self.textedit_streamurl.hide()

    def change_ui_ip_cam(self):
        self.label_resolution_h.hide()
        self.lineedit_resolution_h.hide()
        self.label_resolution_w.hide()
        self.lineedit_resolution_w.hide()

        self.label_usb_port.hide()
        self.combobox_camera_usb_port.hide()
        self.btn_scan.hide()

        self.label_streamurl.show()
        self.textedit_streamurl.show()

    def change_ui_other_cam(self):
        self.label_resolution_h.show()
        self.lineedit_resolution_h.show()
        self.label_resolution_w.show()
        self.lineedit_resolution_w.show()

        self.label_usb_port.hide()
        self.combobox_camera_usb_port.hide()
        self.btn_scan.hide()

        self.label_streamurl.hide()
        self.textedit_streamurl.hide()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = QDialog()
    ui = CameraSetting(dialog)
    dialog.show()
    sys.exit(app.exec_())