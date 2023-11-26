import csv
import os
import sqlite3
import sys

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog, QAbstractItemView

from connection import Data
from project.ui_py.ui_main_file import Ascor
from window import Window
import resource


# Класс по работе с главным окном приложения
class MainApplication(QMainWindow, Ascor):
    def __init__(self):
        super(MainApplication, self).__init__()
        # Подключаем дизайн
        self.setupUi(self)
        self.setWindowTitle('Ascor')
        self.setFixedSize(self.size())

        # Подключаем БД и создаем экземпляр класса по работе с БД
        self.con = sqlite3.connect('data_base_one.db')
        cur = self.con.cursor()
        self.connection = Data()
        self.setAcceptDrops(True)

        # Определяем переменные для взаимодействия из базового и второстепенного классов
        self.sistem_assessment = cur.execute("""
            SELECT value
            FROM value_system
        """).fetchall()[0][0]

        # Вызываем метод отображения содержимого таблицы
        self.preview_data()

        # Обрабатываем нажатия каждой кнопки, расположенной на главном окне
        self.pushButton_add.clicked.connect(self.open_add_dialog_window)
        self.pushButton_up.clicked.connect(self.open_up_dialog_window)
        self.pushButton_del.clicked.connect(self.delete_subject)
        self.pushButton_down_file.clicked.connect(self.open_file_csv)
        self.pushButton_create_file.clicked.connect(self.create_file_csv)
        self.pushButton_down_form.clicked.connect(self.download_form_csv)
        self.pushButton_info.clicked.connect(self.show_about_programm)
        self.pushButton_clear.clicked.connect(self.clear_table)

        # Привязка нажатия на ячейку QTableWidget к методу отображения прогресса
        self.progressBar.setValue(0)
        self.tableWidget.itemClicked.connect(self.progress_check)

    # Метод подсветки выполненных предметов
    def set_color_row(self):
        cur = self.con.cursor()

        # Получаем средние баллы по всем предметам
        set_aver_point = cur.execute("""
            SELECT super_assessment, GPA
            FROM spis_record
        """).fetchall()

        # Получаем индексы выполненных строк
        sp_sucess_aver = []
        for index_row in range(len(set_aver_point)):
            if set_aver_point[index_row][0] - 0.5 <= set_aver_point[index_row][1]:
                sp_sucess_aver.append(index_row)

        # Проходимся по количеству этих индексов и подсвечиваем каждый во всех столбцах (подсветка целой строки)
        for i in range(len(sp_sucess_aver)):
            for col in range(self.tableWidget.columnCount()):
                self.tableWidget.item(sp_sucess_aver[i], col).setBackground(QColor(79, 79, 79))

    # Метод для отслеживания изменения индекса среднего балла
    def check_last_value_gpa(self):
        cur = self.con.cursor()

        # Получаем прошлый и текущий средние баллы
        spis_corteg_gpa = cur.execute("""
            SELECT lst_val, last_value
            FROM last_value_gpa
        """).fetchall()

        # Возвращаем статус изменения индекса среднего балла в зависимости от прошлого среднего балла
        if spis_corteg_gpa[0][0] > spis_corteg_gpa[0][1]:
            return 'red'
        elif spis_corteg_gpa[0][0] < spis_corteg_gpa[0][1]:
            return 'green'
        elif spis_corteg_gpa[0][0] == spis_corteg_gpa[0][1]:
            return 'normal'

    # Проверка на наличие элементов в таблице записей
    def check_elem_for_table(self):
        cur = self.con.cursor()
        result = cur.execute("""
                    SELECT *
                    FROM spis_record
                """).fetchall()
        if len(result) != 0:
            return 1
        return 0

    def preview_data(self):
        cur = self.con.cursor()

        if self.sistem_assessment == 5:
            self.comboBox_system.setCurrentIndex(0)
        elif self.sistem_assessment == 10:
            self.comboBox_system.setCurrentIndex(1)

        rows = cur.execute("""
                    SELECT *
                    FROM spis_record
                """).fetchall()

        # Блокируем выбор системы оценок при заполненной таблице
        if len(rows) != 0:
            self.comboBox_system.setEnabled(False)
        else:
            self.comboBox_system.setEnabled(True)

        # Получаем список кортежей, содержимое которых будем отображать в QTableWidget в главном окне
        result_records = cur.execute("""
                        SELECT 
                            spis_subject.title,
                            spis_record.assessment, 
                            spis_record.super_assessment,
                            spis_record.col_5, 
                            spis_record.col_current,
                            spis_record.GPA
                        FROM
                            spis_subject
                        INNER JOIN
                            spis_record ON spis_subject.id = spis_record.id
                        """).fetchall()

        name_title = ['Предмет', 'Ваши оценки', 'Желаемая', 'Отличных', 'Желаемых', 'Средний балл']
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(name_title)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1)

        # Построчно наполняем таблицу QTableWidget
        for i, row in enumerate(result_records):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

        # Получаем результат выполнения метода подсчета информации
        result_basic_info = self.connection.calculation_values_on_main_window(self.sistem_assessment)

        # Получаем количетво предметов, средний балл по всем оценкам, средний балл по супер-оценкам, кол-во выполненных
        col_subject = result_basic_info[0]
        average_point = result_basic_info[1]
        super_average_point = result_basic_info[2]
        col_sucessful = result_basic_info[3]

        # Отображаем на главном окне
        self.label_col.setText(str(col_subject))
        self.label_sr_ball.setText(str(average_point))
        self.label_strem.setText(str(super_average_point))
        self.label_suc.setText(str(col_sucessful))

        # Подключаем метод подсветки выполненных предметов
        self.set_color_row()

        if self.check_last_value_gpa() == 'red':
            self.label_sr_ball.setStyleSheet("color: red")
        elif self.check_last_value_gpa() == 'green':
            self.label_sr_ball.setStyleSheet("color: green")
        elif self.check_last_value_gpa() == 'normal':
            self.label_sr_ball.setStyleSheet("color: rgb(16, 109, 196)")

        # Если таблица пуста, обнулим значения среднего балла в бд
        rows = cur.execute("""
                            SELECT *
                            FROM spis_record
                        """).fetchall()
        if len(rows) == 0:
            cur.execute("""
                 UPDATE last_value_gpa 
                 SET lst_val = ?, last_value = ?
            """, (0.0, 0.0))
            self.label_sr_ball.setStyleSheet("color: none")
        self.con.commit()

    # Метод прогресса зависимости текущего среднего балла от желаемой оценки
    def progress_check(self, item):
        cur = self.con.cursor()
        column = item.column()
        subject = item.text()

        # Обрабатываем только если нажали на столбец с предметами
        if column == 0:
            rows = cur.execute("""
                SELECT *
                FROM spis_record
                WHERE id = (
                    SELECT id
                    FROM spis_subject
                    WHERE title = ?
                )
                """, (subject,)).fetchall()

            # Подсчет доли текущего среднего балла от супер оценки - 0.5 (результат в пользу ученика)
            average_point = float(rows[0][5])
            super_average_point = float(rows[0][2]) - 0.5
            percent = round(average_point / super_average_point * 100)

            # Заполнение прогрессбара значачением
            if percent > 100:
                self.progressBar.setValue(100)
            else:
                self.progressBar.setValue(percent)

        else:
            pass

    # Метод возвращения системы оценок
    def return_sistem_assessment(self) -> int:
        return self.sistem_assessment

    # Вызов метода добавления в диалоговом окне
    def open_add_dialog_window(self):
        cur = self.con.cursor()

        # Получаем текст QCombobox, в зависимости от него передаем переменной 'system' значение системы оценивания
        current_value = self.comboBox_system.currentText()
        if current_value[0] == '5':
            self.sistem_assessment = 5
        elif current_value[0:2] == '10':
            self.sistem_assessment = 10

        cur.execute("""
            UPDATE value_system 
            SET value = ?
        """, (self.sistem_assessment,))
        self.con.commit()

        # При нажатии на кнопку добавления создаем экземпляр диалогового окна и взаимодействуем с методом добавления
        self.window = Window(self)
        self.window.setModal(True)
        self.window.open_add_dialog_window(self.sistem_assessment)
        self.window.show()
        self.window.exec()

        # Обнуляем значение прогресс бар, чтобы не хранить значение по предмету после выполнения другого действия
        self.progressBar.setValue(0)

    # Вызов метода редактирования в диалоговом окне
    def open_up_dialog_window(self):
        cur = self.con.cursor()
        rows = cur.execute("""
            SELECT *
            FROM spis_record
        """).fetchall()

        # Если таблица не пустая, собираем информацию из QTableWidget
        if len(rows) != 0:
            try:
                # Собираем нужную информацию из QTableWidget
                index = self.tableWidget.selectedIndexes()
                subject = self.tableWidget.model().data(index[0])
                assessment = self.tableWidget.model().data(index[1])
                super_assessment = self.tableWidget.model().data(index[2])

                # При нажатии на кнопку создаем экземпляр диалогового окна и взаимодействуем с методом редактирования
                self.window = Window(self)
                self.window.setModal(True)
                self.window.open_up_dialog_window(subject, assessment, super_assessment, self.sistem_assessment)
                self.window.show()
                self.window.exec()

                # Обнуляем значение прогресс бар
                self.progressBar.setValue(0)

            except IndexError:
                # Оповещаем, если при редактировании не выбрали строку с предметом
                alert = QMessageBox(self)
                alert.setText('Для редактирования выберите строку с предметом!')
                alert.setIcon(QMessageBox.Warning)
                alert.setStandardButtons(QMessageBox.Ok)
                alert.exec()
        else:
            # Оповещаем, если таблица пустая
            alert = QMessageBox(self)
            alert.setText('Предметы не добавлены!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

    # Метод удаления записи из таблицы
    def delete_subject(self):
        cur = self.con.cursor()
        rows = cur.execute("""
                    SELECT *
                    FROM spis_record
                """).fetchall()

        if len(rows) != 0:
            try:
                # Получаем название предмета
                index = self.tableWidget.selectedIndexes()
                subject = self.tableWidget.model().data(index[0])
                try:
                    # Проверка, что нажали именно на ячейку предмета или выбрали строку
                    float(subject)

                    # Оповещаем если при редактировании не выбрали предмет
                    alert = QMessageBox(self)
                    alert.setText('Для удаления выберите предмет!')
                    alert.setIcon(QMessageBox.Warning)
                    alert.setStandardButtons(QMessageBox.Ok)
                    alert.exec()

                except ValueError:
                    # Создаем окошко подтверждения действия
                    confirm = QMessageBox.question(self,
                                                   self.windowTitle(),
                                                   '''Вы действительно хотите удалить запись? 
                                                   Это повлияет на отображаемую информацию!''',
                                                   QMessageBox.Yes | QMessageBox.No)

                    if confirm == QMessageBox.Yes:
                        # При подтвержении методом удаления у экземпляра 'self.connect' удаляем предмет
                        self.connection.delete_subject(subject)

                        # Блок подстановки нового значения среднего балла
                        all_gpa = cur.execute("""
                            SELECT GPA
                            FROM spis_record
                        """).fetchall()
                        if len(all_gpa) != 0:
                            all_gpa = [gpa[0] for gpa in all_gpa]
                            new_gpa = round(sum(all_gpa) / len(all_gpa), 2)

                            last_value = cur.execute("""
                                SELECT last_value
                                FROM last_value_gpa
                            """).fetchall()[0][0]

                            cur.execute("""
                                UPDATE last_value_gpa
                                SET lst_val = ?, last_value = ?
                            """, (last_value, new_gpa))
                            self.con.commit()

                        self.preview_data()

                        # Оповещаем если успешно удалили предмет
                        alert = QMessageBox(self)
                        alert.setText('Предмет успешно удален!')
                        alert.setIcon(QMessageBox.Information)
                        alert.setStandardButtons(QMessageBox.Ok)
                        alert.exec()

                # Обнуляем значение прогресс бар
                self.progressBar.setValue(0)

            # В противном случае вызываем исключение с вызовоз QMessageBox
            except IndexError:
                # Оповещаем если при редактировании не выбрали предмет
                alert = QMessageBox(self)
                alert.setText('Для удаления выберите предмет!')
                alert.setIcon(QMessageBox.Warning)
                alert.setStandardButtons(QMessageBox.Ok)
                alert.exec()
        else:
            # Оповещаем если таблица пустая
            alert = QMessageBox(self)
            alert.setText('Предметы не добавлены!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

    # Метод полной очистки таблицы записей
    def clear_table(self):
        cur = self.con.cursor()

        records = cur.execute("""
            SELECT id
            FROM spis_record
        """).fetchall()

        if len(records) != 0:
            # Создаем окошко подтверждения действия
            confirm = QMessageBox.question(self,
                self.windowTitle(),
                '''Вы действительно хотите очистить таблцу полностью?''',
            QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                # При подтверждении удаляем все
                cur.execute("""
                    DELETE
                    FROM spis_record 
                """).fetchall()
                self.con.commit()

                self.preview_data()

                alert = QMessageBox(self)
                alert.setText('Таблица успешно очищена!')
                alert.setIcon(QMessageBox.Information)
                alert.setStandardButtons(QMessageBox.Ok)
                alert.exec()

        else:
            alert = QMessageBox(self)
            alert.setText('Таблица пуста!')
            alert.setIcon(QMessageBox.Information)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

    # Метод загрузки csv-файла с помощью кнопки
    def open_file_csv(self):
        with sqlite3.connect('data_base_one.db') as con:
            cur = con.cursor()

            # Получаем текст QCombobox, зависимости от него передаем переменной 'system' значение системы оценивания
            current_value = self.comboBox_system.currentText()
            if current_value[0] == '5':
                self.sistem_assessment = 5
            elif current_value[0:2] == '10':
                self.sistem_assessment = 10

            cur.execute("""
                UPDATE value_system 
                SET value = ?
            """, (self.sistem_assessment,))

            con.commit()

        # Перенесем основу метода в метод диалогового окна, т.к. методы проверки данных в нем
        self.window = Window(self)
        file_dialog = QFileDialog()
        file_path = file_dialog.getOpenFileName(self, 'Выбрать файл', '', 'Файл-csv (*.csv)')[0]

        if file_path:
            # Вызываем метод диалогового окна добавления файла
            self.window.download_file_csv(file_path)
        else:
            pass

    # Пара методов для перетягивание файла
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                # Получаем путь к выбранному файлу
                file_path = url.toLocalFile()
                if file_path[-4:] == '.csv':
                    # Перенесем основу метода в метод диалогового окна
                    self.window = Window(self)
                    if file_path:
                        self.window.download_file_csv(file_path)
                    else:
                        pass
                else:
                    alert = QMessageBox()
                    alert.setText('Неверное расширение файла! Возможна загрузка только файлов расширением .csv!')
                    alert.setIcon(QMessageBox.Warning)
                    alert.setStandardButtons(QMessageBox.Ok)
                    alert.exec()

    # Метод создания csv-файла на основе данных таблицы
    def create_file_csv(self):
        cur = self.con.cursor()
        title_cort = ['Название предмета', 'Текущие оценки', 'Хотим получить',
                      'Получить отличных', 'Получить желаемых', 'Средний балл']
        # Получаем список кортежей, содержимое которых будем отображать в QTableWidget в главном окне
        result_records = cur.execute("""
            SELECT 
                spis_subject.title,
                spis_record.assessment, 
                spis_record.super_assessment,
                spis_record.col_5, 
                spis_record.col_current,
                spis_record.GPA
            FROM
                spis_subject
            INNER JOIN
                spis_record ON spis_subject.id = spis_record.id
       """).fetchall()

        self.con.commit()

        if len(result_records) != 0:
            # Создаем опцию, которай позволяет выбирать только папку, а не конкретный файл
            options = QFileDialog.Options()
            options |= QFileDialog.ShowDirsOnly
            set_directory_dialog = QFileDialog.getExistingDirectory(self, 'Выбрать место сохранения', options=options)
            file_name = 'file_ascor.csv'

            #  Если выбрали место сохранения, зпаписываем файл в него
            if set_directory_dialog:
                with open(os.path.join(set_directory_dialog, file_name), 'w', newline='', encoding="utf8") as csvfile:
                    writer = csv.writer(
                        csvfile, delimiter=',', quotechar='"')
                    writer.writerow(title_cort)
                    for row in result_records:
                        writer.writerow(list(row))

                alert = QMessageBox()
                alert.setText("Файл 'file_ascor.csv' успешно создан!")
                alert.setIcon(QMessageBox.Information)
                alert.setStandardButtons(QMessageBox.Ok)
                alert.exec()
            else:
                pass
        else:
            alert = QMessageBox()
            alert.setText('Таблица пустая. Внесите записи для сохранения!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

    # Метод создания csv-файла-формы с заголовками для заполнения
    def download_form_csv(self):
        # Создаем опцию, которай позволяет выбирать только папку, а не конкретный файл.
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        set_directory_dialog = QFileDialog.getExistingDirectory(self, 'Выбрать место сохранения', options=options)
        file_name = 'form_ascor.csv'

        #  Если выбрали место сохранения, зпаписываем файл в него
        if set_directory_dialog:
            with open(os.path.join(set_directory_dialog, file_name), 'w', newline='', encoding="utf8") as csvfile:
                writer = csv.writer(
                    csvfile, delimiter=',', quotechar='"')
                title_as_form = ['Название предмета', 'Текущие оценки', 'Хотим получить',
                                 'Получить отличных', 'Получить желаемых', 'Средний балл']
                writer.writerow(title_as_form)

            alert = QMessageBox()
            alert.setText("Файл формы для заполнения 'form_ascor.csv' успешно создан!")
            alert.setIcon(QMessageBox.Information)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()
        else:
            pass

    # Метод 'О программе'
    def show_about_programm(self):
        QMessageBox.about(self, "О программе",
                          "Полное название: Ascor application\nПолная версия: 0.1.0\nРазработчик: @kubic")


# Если весь код запускается с самого файла с данным кодом
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApplication()
    ex.show()
    sys.exit(app.exec())
