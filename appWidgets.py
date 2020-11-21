from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QCheckBox, QLineEdit, \
    QInputDialog, QLabel, QTableWidget
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QMessageBox, QCalendarWidget, QTableWidgetItem, \
    QFileDialog
from PyQt5.QtWidgets import QSpinBox
from math import sin, cos, tan, log, pi
from PyQt5 import uic
from hashlib import md5
import datetime
import sqlite3
import csv
import os

CONNECT = sqlite3.connect('data/accounts.sqlite')


class Notebook(QWidget):
    def __init__(self, login):
        super().__init__()
        self.login = login
        uic.loadUi('templates/Notebook.ui', self)
        self.setWindowTitle('Заметки')
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.openText()
        self.pushButton.clicked.connect(self.save_notes)
        self.checkBox.clicked.connect(self.readMode)

    def openText(self):
        try:
            file = open(
                'data/scraps/' + md5(self.login.encode()).hexdigest() + '.txt',
                mode='r',
                encoding='utf-8')
            self.textEdit.setText(file.read())
        except FileNotFoundError:
            pass

    def save_notes(self):
        text = self.textEdit.toPlainText()
        m = open('data/scraps/' + md5(self.login.encode()).hexdigest() + '.txt',
                 mode='w', encoding='utf-8')
        m.write(text)
        m.close()

    def readMode(self):
        self.textEdit.setEnabled(not self.sender().isChecked())


class Cells(QWidget):
    def __init__(self, login):
        super().__init__()
        self.login = login
        self.__initUI()

    def __initUI(self):
        uic.loadUi('templates/Cells.ui', self)
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.setWindowTitle('Ячейки')
        self.pushButton.clicked.connect(self.openCell)
        for i in range(2, 25):
            exec(f'self.pushButton_{str(i)}.clicked.connect(self.openCell)')
        self.pushButton_25.clicked.connect(self.loadData)
        self.spinBox.setRange(1, 24)

    def loadData(self):
        user, ident = md5(self.login.encode()).hexdigest(), self.spinBox.text()
        all_data, cur = self.checkBox.isChecked(), CONNECT.cursor()
        direction = QFileDialog.getSaveFileName(self, 'Сохранить', '')[0]
        os.mkdir(direction)
        if not all_data:
            data = \
                cur.execute('''SELECT data FROM cells WHERE user = ? AND id = ?''',
                            (user, ident)).fetchone()[0]
            with open(direction + '/data.txt', mode='w', encoding='utf8') as file:
                file.write(data)
                file.close()
        else:
            data = cur.execute(
                f'SELECT data FROM cells WHERE user = "{user}"').fetchall()
            print(data)
            for index, elem in enumerate(data):
                with open(direction + '/data' + str(index + 1) + '.txt',
                          mode='w', encoding='utf8') as file:
                    file.write(elem[0])
                    file.close()
        self.update()

    def openCell(self):
        user, ident = md5(self.login.encode()).hexdigest(), self.sender().text()
        cur = CONNECT.cursor()
        text = cur.execute('''SELECT data FROM cells WHERE id = ? AND user = ?''',
                           (ident, user)).fetchall()
        self.dataShow = DataCell(text[0][0] if text else '', self.sender().text(),
                                 self.login)
        self.dataShow.show()


class Table(QWidget):
    def __init__(self, login):
        super().__init__()
        self.login = login
        self.tableItems = []
        self.block = False  # Переменная блокировки сигнала itemChanged
        self.__initUI()

    def __initUI(self):
        uic.loadUi('templates/Table.ui', self)
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.setWindowTitle('Таблица')
        self.tabWidget.setTabText(0, 'Таблица')
        self.tabWidget.setTabText(1, 'CSV')
        self.pushButton.clicked.connect(self.saveCSV)
        self.pushButton_2.clicked.connect(self.loadCSV)
        self.pushButton_3.clicked.connect(self.unloadCSV)
        self.pushButton_4.clicked.connect(self.addRow)
        self.pushButton_5.clicked.connect(self.addColumn)
        self.pushButton_6.clicked.connect(self.delRow)
        self.pushButton_7.clicked.connect(self.delColumn)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.openCSV()
        self.openTableCSV()

    def openTableCSV(self):
        self.block = True
        try:
            if self.tableItems:
                title = self.tableItems[0]
                self.tableWidget.setColumnCount(len(title))
                self.tableWidget.setHorizontalHeaderLabels(title)
                self.tableWidget.setRowCount(0)
                for i, row in enumerate(self.tableItems[1:]):
                    self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                    for j, elem in enumerate(row):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(elem))
        except FileNotFoundError:
            pass
        self.block = False

    def openCSV(self):
        self.block = True
        try:
            with open('data/csv/' + md5(self.login.encode()).hexdigest() + '.csv',
                      encoding='utf8') as file:
                csv_code = file.read()
                self.textEdit.setText(csv_code)
                self.tableItems = [i.split(';') for i in
                                   csv_code.split('\n') if i]

        except FileNotFoundError:
            pass
        self.block = False

    def saveCSV(self):
        with open('data/csv/' + md5(self.login.encode()).hexdigest() + '.csv',
                  mode='w', encoding='utf8') as file:
            csv_code_text = self.textEdit.toPlainText()
            file.write(csv_code_text)
        self.openCSV()
        self.openTableCSV()
        self.update()

    def loadCSV(self):
        """Функция подгрузки CSV файла в таблицу"""
        file = QFileDialog.getOpenFileName(self, 'Выберите CSV Таблицу', '',
                                           '*.csv')[0]
        if file:
            with open(file, 'r', encoding='utf8') as csv_file:
                csv_code = csv_file.read()
                with open('data/csv/' + md5(
                        self.login.encode()).hexdigest() + '.csv',
                          mode='w', encoding='utf8') as csv_file2:
                    csv_file2.write(csv_code)
            self.openCSV()
            self.openTableCSV()
            self.update()

    def unloadCSV(self):
        direction = QFileDialog.getSaveFileName(self, 'Сохранить', '', '*.csv')[0]
        with open(direction, mode='w', encoding='utf8') as file:
            file.write(self.textEdit.toPlainText())

    def addRow(self):
        self.tableItems.append([' ' for i in
                                range(self.tableWidget.columnCount())])
        with open('data/csv/' + md5(self.login.encode()).hexdigest() + '.csv',
                  mode='w', encoding='utf8') as file:
            csv_code = '\n'.join([';'.join(i) for i in self.tableItems])
            file.write(csv_code)
        self.openCSV()
        self.openTableCSV()

    def addColumn(self):
        name_col, ok_pressed = QInputDialog.getText(self, 'Добавить колонку',
                                                    'Введите название колонки')
        if ok_pressed:
            try:
                self.tableItems[0].append(name_col)
            except IndexError:
                self.tableItems.append([name_col])

            for i in range(1, len(self.tableItems)):
                self.tableItems[i].append(' ')
            with open('data/csv/' + md5(self.login.encode()).hexdigest() + '.csv',
                      mode='w', encoding='utf8') as file:
                csv_code = '\n'.join([';'.join(i) for i in self.tableItems])
                file.write(csv_code)
            self.openCSV()
            self.openTableCSV()

    def delRow(self):
        print(self.tableItems)
        row = self.tableWidget.currentRow()
        if row >= 0:
            del self.tableItems[row + 1]
            with open('data/csv/' + md5(self.login.encode()).hexdigest() + '.csv',
                      mode='w', encoding='utf8') as file:
                csv_code = '\n'.join([';'.join(i) for i in self.tableItems])
                file.write(csv_code)
            self.openCSV()
            self.openTableCSV()

    def delColumn(self):
        try:
            col, ok = QInputDialog.getItem(self, 'Выберите колонку',
                                           'Выберите колонку чтобы ее удалить',
                                           self.tableItems[0])
            col_index = self.tableItems[0].index(col)
            print(col_index)
            for i in range(len(self.tableItems)):
                if len(self.tableItems[i]) - 1 == col_index:
                    strip = []
                else:
                    strip = self.tableItems[i][col_index + 1:]
                self.tableItems[i] = self.tableItems[i][:col_index] + strip
            if not self.tableItems[0]:
                self.tableWidget.clear()
                self.tableWidget.update()
                self.update()

            with open('data/csv/' + md5(self.login.encode()).hexdigest() + '.csv',
                      mode='w', encoding='utf8') as file:
                csv_code = '\n'.join([';'.join(i) for i in self.tableItems])
                file.write(csv_code)
            self.openCSV()
            self.openTableCSV()
        except IndexError:
            QMessageBox.critical(self, 'Ошибка', 'У вас пустая таблица')

    def formulaInTable(self, item):
        if item[:8].lower() == 'formula(' and item[-1] == ')':
            try:
                formula = item[8:len(item) - 1].lower()
                return str(eval(formula)), True
            except Exception as err:
                print(err)
                return 'ERROR', False
        return item, False

    def item_changed(self, item):
        if not self.block:
            i, j = item.row(), item.column()
            elem, update_need = self.formulaInTable(item.text())
            self.tableItems[i + 1][j] = elem
            with open('data/csv/' + md5(self.login.encode()).hexdigest() + '.csv',
                      mode='w', encoding='utf8') as file:
                csv_code = '\n'.join([';'.join(i) for i in self.tableItems])
                file.write(csv_code)
            self.openCSV()
            if update_need:
                self.openTableCSV()


class Calendar(QWidget):
    def __init__(self, login):
        super().__init__()
        self.login, self.today = login, '.'.join(
            str(datetime.date.today()).split('-')[::-1])
        self.__initUI()

    def __initUI(self):
        uic.loadUi('templates/Calendar.ui', self)
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.setWindowTitle('Календарь')
        self.label.setText(f'Сегодня {self.today}')
        self.calendarWidget.clicked.connect(self.openDateEvents)
        self.pushButton.clicked.connect(self.addEvent)
        self.pushButton_2.clicked.connect(self.delEvent)
        self.openDateEvents()

    def addEvent(self):
        date, cur = self.openDate(), CONNECT.cursor()
        text, ok_pressed = QInputDialog.getMultiLineText(self, 'Добавить событие',
                                                         'Введите событие:')
        if ok_pressed:
            result_request = cur.execute('''SELECT event, user, date FROM events
                                            WHERE event = ? AND user = ?
                                            AND date = ?''',
                                         (text,
                                          md5(self.login.encode()).hexdigest(),
                                          date)).fetchall()
            if not result_request:
                cur.execute(
                    '''INSERT INTO events(event, user, date) VALUES(?, ?, ?)''',
                    (text, md5(self.login.encode()).hexdigest(), date))
            else:
                QMessageBox.critical(self, 'Ошибка',
                                     'Введите не повторяющееся событие')

            CONNECT.commit()
        self.openDateEvents()

    def delEvent(self):
        index, cur = self.listWidget.currentRow(), CONNECT.cursor()
        event, user, date = cur.execute('''SELECT event, user, date FROM events
                                           WHERE user = ? AND date = ?''',
                                        (md5(self.login.encode()).hexdigest(),
                                         self.openDate())).fetchall()[index]
        cur.execute(
            '''DELETE FROM events WHERE event = ? AND user = ? AND date = ?''',
            (event, user, date))
        CONNECT.commit()
        self.openDateEvents()

    def openDate(self):
        return '.'.join(
            [str(i) for i in self.calendarWidget.selectedDate().getDate()][::-1])

    def openDateEvents(self):
        self.listWidget.clear()
        self.listWidget.addItems(self.getEvents())
        self.update()

    def getEvents(self):
        date, cur = self.openDate(), CONNECT.cursor()

        events = [event[0] for event in
                  cur.execute(
                      '''SELECT event FROM events WHERE date = ? AND user = ?''',
                      (date, md5(self.login.encode()).hexdigest())).fetchall()]
        return events


class Statistic(QWidget):
    def __init__(self, login):
        super().__init__()
        self.login = login
        self.__initUI()

    def __initUI(self):
        uic.loadUi('templates/Statistic.ui', self)
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.setWindowTitle('Статистика')
        self.tabWidget.setTabText(0, 'Личная')
        self.tabWidget.setTabText(1, 'Общая')
        self.pushButton.clicked.connect(self.addData)
        self.openStatistic()
        self.openMeStatistic()

    def addData(self):
        text, ok_press = QInputDialog.getMultiLineText(self, 'Добавить данные',
                                                       'Введите данные статистики')
        user = md5(self.login.encode()).hexdigest()
        if text and ok_press:
            with open('data/statistic/' + user + '.txt', encoding='utf8',
                      mode='w') as file:
                file.write(text + ';')
            self.verticalLayout_2.addWidget(QLabel(text))

    def openMeStatistic(self):
        user = md5(self.login.encode()).hexdigest()
        try:
            with open('data/statistic/' + user + '.txt', encoding='utf8') as file:
                elements = [i for i in file.read().split(';') if i]
                for elem in elements:
                    self.verticalLayout_2.addWidget(QLabel(elem))
        except FileNotFoundError:
            pass

    def openStatistic(self):
        user, cur = md5(self.login.encode()).hexdigest(), CONNECT.cursor()
        try:
            with open('data/formulas/' + user + '.txt', encoding='utf8') as file:
                formulas = [i for i in file.read().split(';') if i]
                self.label.setText('Количество формул: ' + str(len(formulas)))
        except FileNotFoundError:
            self.label.setText('Количество формул: 0')

        cells = len([i for i
                     in cur.execute(f"""SELECT data FROM cells
                                        WHERE user = '{user}' """).fetchall()
                     if i[0]])
        self.label_2.setText('Количество занятых ячеек: ' + str(cells))

        try:
            with open('data/scraps/' + user + '.txt') as file:
                length = str(len([i for i in file.read() if i.isalnum()]))
                self.label_3.setText(f'Количество символов в заметках: {length}')
        except FileNotFoundError:
            self.label_3.setText('Количество символов в заметках: 0')

        count_users = cur.execute('SELECT COUNT(*) FROM acc').fetchone()[0]
        self.label_4.setText(f'Количество пользователей приложения: {count_users}')


class FormulasWindow(QWidget):
    def __init__(self, login):
        super().__init__()
        self.login = login
        uic.loadUi('templates/FormulasWindow.ui', self)
        self.__initUI()
        self.createSpace()
        self.openListFormulas()

    def __initUI(self):
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.setWindowTitle('Формулы')
        self.listWidget.itemDoubleClicked.connect(self.resultFormula)
        func = lambda: self.resultFormula(self.listWidget.currentItem())
        self.pushButton_3.clicked.connect(func)
        self.pushButton.clicked.connect(self.addFormula)
        self.pushButton_2.clicked.connect(self.delFormula)

    def addFormula(self):
        formula, ok = QInputDialog.getText(self, "Введите формулу",
                                           "Введите формулу с переменной x(англ.)")
        text = self.text()
        if ok and formula:
            self.listWidget.addItem(formula)
            file = open(
                'data/formulas/' + md5(self.login.encode()).hexdigest() + '.txt',
                mode='w', encoding='utf-8')
            file.write(text + formula + ';')
            file.close()
            self.update()

    def delFormula(self):
        index = self.listWidget.currentRow()
        formulas = [i for i in self.text().split(';') if i]
        print(formulas, index)
        del formulas[index]
        with open('data/formulas/' + md5(self.login.encode()).hexdigest() + '.txt',
                  mode='w', encoding='utf-8') as file:
            file.write((';'.join(formulas) + ';').strip())
        self.listWidget.clear()
        self.openListFormulas()

    def text(self):
        file = open(
            'data/formulas/' + md5(self.login.encode()).hexdigest() + '.txt',
            mode='r',
            encoding='utf-8')
        return file.read()

    def createSpace(self):
        """
        Функция нужна для того чтобы решить проблему с открытием файла считывания
        формул.
        (При первом запуске)
        """
        try:
            file = open(
                'data/formulas/' + md5(self.login.encode()).hexdigest() + '.txt',
                mode='r', encoding='utf-8')
            file.read()
        except FileNotFoundError:
            file = open(
                'data/formulas/' + md5(self.login.encode()).hexdigest() + '.txt',
                mode='w', encoding='utf-8')
            file.write('')
            file.close()

    def openListFormulas(self):
        try:
            file = open(
                'data/formulas/' + md5(self.login.encode()).hexdigest() + '.txt',
                mode='r',
                encoding='utf-8')
            formulas = file.read().split(';')
            self.listWidget.addItems([formula for formula in formulas if formula])
        except FileNotFoundError:
            pass

    def resultFormula(self, item):
        formula = item.text()

        try:
            self.lineEdit_2.setText(
                str(eval(formula.replace('x', self.lineEdit.text()))))
        except (NameError, TypeError, ZeroDivisionError, SyntaxError):
            QMessageBox.critical(self, 'Ошибка', 'Введите верное значение x')


class DataCell(QWidget):
    """Вспомогательное окно для окна Cell"""

    def __init__(self, text, ident, login):
        super().__init__()
        print(text)
        uic.loadUi('templates/DataCell.ui', self)
        self.setWindowIcon(QIcon('templates/icon.ico'))
        self.login, self.ident = login, ident
        self.textEdit.setText(text)
        self.setWindowTitle('Ячейка ' + ident)
        self.pushButton.clicked.connect(self.saveData)

    def saveData(self):
        """Функция для сохранения записей в ячейке"""
        user = md5(self.login.encode()).hexdigest()
        text, cur = self.textEdit.toPlainText(), CONNECT.cursor()
        request = cur.execute(
            '''SELECT id, user FROM cells WHERE user = ? AND id = ?''',
            (user, self.ident)).fetchall()  # Запрос записей ячейки по данным юзера
        if request:
            cur.execute('''UPDATE cells
                           SET data = ?
                           WHERE user = ? AND id = ? ''', (text, user, self.ident))
        else:
            cur.execute('''INSERT INTO cells(id, user, data) VALUES(?, ?, ?)''',
                        (self.ident, user, text))
        CONNECT.commit()
        self.update()
