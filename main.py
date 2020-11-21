import sys
import sqlite3

from PyQt5.QtGui import QIcon

import appWidgets

from hashlib import md5
from appWidgets import CONNECT
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QPushButton, QLineEdit
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5 import uic


class Auth(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('templates/AuthUI.ui', self)
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.pushButton.clicked.connect(self.confirm)
        self.pushButton_2.clicked.connect(self.registration)

    def confirm(self):
        cur = CONNECT.cursor()
        login, password = self.lineEdit.text(), self.lineEdit_2.text()
        data = cur.execute('''SELECT login, password FROM acc
                                  WHERE login = ? AND password = ?''',
                           (login, md5(password.encode()).hexdigest())).fetchone()
        if data:
            self.label.setText('Добро пожаловать в Vitaliano App')
            self.app = App(login)
            self.app.show()
            self.setVisible(False)
        else:
            self.label.setText('Введите верные данные!')

    def registration(self):
        cur = CONNECT.cursor()
        login, password = self.lineEdit.text(), self.lineEdit_2.text()
        request = cur.execute(
            f'SELECT login, password FROM acc WHERE login = "{login}"').fetchone()
        if not request:
            cur.execute('''INSERT INTO acc(login, password) VALUES(?, ?)''',
                        (login, md5(password.encode()).hexdigest()))
            CONNECT.commit()
            self.label.setText(f'Регистрация пользователя {login} прошла успешно!')
        else:
            self.label.setText('Выберите свободный логин!')


class App(QMainWindow):
    def __init__(self, login):
        super().__init__()
        self.login = login
        self.__initUI()

    def __initUI(self):
        uic.loadUi('templates/App.ui', self)
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.setWindowTitle('Vitaliano App')
        self.label.setText(f'login: {self.login}')
        self.pushButton.clicked.connect(sys.exit)
        self.pushButton_2.clicked.connect(self.table)
        self.pushButton_7.clicked.connect(self.changeAccount)
        self.pushButton_5.clicked.connect(self.notebook)
        self.pushButton_8.clicked.connect(self.formulas)
        self.pushButton_9.clicked.connect(self.calendar)
        self.pushButton_10.clicked.connect(self.cell)
        self.pushButton_11.clicked.connect(self.statistic)

    def table(self):
        self.tableWindow = appWidgets.Table(self.login)
        self.tableWindow.show()

    def changeAccount(self):
        ex.setVisible(True)
        self.close()

    def formulas(self):
        self.formWindow = appWidgets.FormulasWindow(self.login)
        self.formWindow.show()

    def notebook(self):
        self.note = appWidgets.Notebook(self.login)
        self.note.show()

    def cell(self):
        self.cellWindow = appWidgets.Cells(self.login)
        self.cellWindow.show()

    def calendar(self):
        self.calendarWindow = appWidgets.Calendar(self.login)
        self.calendarWindow.show()

    def statistic(self):
        self.statWindow = appWidgets.Statistic(self.login)
        self.statWindow.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Auth()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
