from PyQt5.QtWidgets import *
from script import main

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet('MainWindow {background-image: url(script/background.jpg); }')
    Dialog = main.MainWindow()
    Dialog.setWindowTitle("AFIS")
    Dialog.showMaximized()
    sys.exit(app.exec_())