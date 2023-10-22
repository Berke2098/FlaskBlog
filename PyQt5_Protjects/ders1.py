import sys
from PyQt5 import QtWidgets


def Pencere():

    app=QtWidgets.QApplication(sys.argv)

    pencere = QtWidgets.QWidget()
    etiket= QtWidgets.QLabel(pencere)
    etiket.setText("Yazı1 Yazı2 Yazı3")
    etiket.move(200,30)
    pencere.setWindowTitle("Ders 1")
    buton= QtWidgets.QPushButton(pencere)
    buton.setText("Buton1")
    buton.move(200,70)
    pencere.show()

    sys.exit(app.exec_())

Pencere()