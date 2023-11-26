import csv
import sqlite3

from PyQt5.QtWidgets import QDialog, QMessageBox

from project.ui_py.ui_dialog_window_file import UiDialog
from connection import Data
import resource


# Класс по работе с диалоговым окном приложения
class Window(QDialog, UiDialog):
    # Передаем в инициализатор ссылку на объект главного окна для взаимодействия с ним через диалоговое окно
    def __init__(self, main_window):
        super(Window, self).__init__(main_window)
        # Подключаем дизайн
        self.setupUi(self)
        self.setFixedSize(self.size())

        # Создаем экземляр главного окна (далее будем вызывать метод отображения информации на главном окне)
        self.main_window = main_window

        # Подключаем БД и создаем экземпляр класса по работе с БД
        self.con = sqlite3.connect('data_base_one.db')
        self.connection = Data()

    # Метод добавления в QCombobox для выбора предмета всех возможных предметов из таблицы spis_subject
    def add_title_subj_in_combobox(self):
        # Подключаем курсор для работы с содержимым БД
        cur = self.con.cursor()
        # Получаем список кортежей, содержимое которых будем добавлять в QCombobox в диалоговом окне
        title_subject = cur.execute("""
            SELECT title
            FROM spis_subject
        """).fetchall()

        # Добавим данные в список, который передадим параметром в строенный метод добавления значений QCombobox
        sp_title_subject = []
        for _ in title_subject:
            sp_title_subject.append(_[0])
        # Добавим значения
        self.comboBox.addItems(sp_title_subject)

    # Алгоритм по вычеслению необходимого количества '5' и/или 'желаемых оценок'
    def algoritm_process(self, super_ass, str_ass):
        # POV: процесс алгоритма интуитивно понятен и не нуждается в пояснении
        super_ass, str_ass = super_ass, [str_ass]

        # Получаем число - систему оценки из метода главного класса.
        # Номинал системы оценки также является лучшей оценкой
        sistem_assessment = self.main_window.return_sistem_assessment()

        col_5 = 0
        col_cur = 0
        for str_grade in str_ass:

            if sistem_assessment == 10:
                spis_del_10 = str_grade.strip().split('10')
                col_10 = len(spis_del_10) - 1
                list_int_grade = list(map(lambda x: int(x), ''.join(spis_del_10)))

                for i in range(col_10):
                    list_int_grade.append(10)
            else:
                list_int_grade = list(map(lambda x: int(x), list(str_grade.strip())))

            sum_grade = sum(list_int_grade)
            col_grade = len(list_int_grade)
            gpa = sum_grade / col_grade
            flag = True
            while flag:
                if gpa >= super_ass - 0.5:
                    flag = False
                    break
                else:
                    if (sum_grade + sistem_assessment) / (col_grade + 1) >= super_ass - 0.5:
                        if super_ass != sistem_assessment:
                            if (sum_grade + super_ass) / (col_grade + 1) >= super_ass - 0.5:
                                sum_grade += super_ass
                                col_grade += 1
                                col_cur += 1
                                break

                    sum_grade += sistem_assessment
                    col_grade += 1
                    col_5 += 1
                    gpa = sum_grade / col_grade
        return col_5, col_cur

    # Проверка на корректность ввода оценок
    def check_corrected_assessment(self, assessment):
        # Получаем число - систему оценки из метода главного класса
        sistem_assessment = self.main_window.return_sistem_assessment()

        result_check = ''
        if len(assessment) != 0:
            for ass in assessment:
                try:
                    int(ass)
                    if self.main_window.return_sistem_assessment() == 10:
                        if '0' in ''.join(assessment.split('10')):
                            return 'input_zero'
                        if int(ass) <= sistem_assessment:
                            result_check = 'ok'
                    else:
                        if 1 <= int(ass) <= sistem_assessment:
                            # Если оценки введены корректно без лишних символов
                            result_check = 'ok'
                        else:
                            return 'input_zero'
                except ValueError:
                    # Если есть лишние символы
                    return 'value_error'

        # Если ничего не ввели
        else:
            result_check = 'len_error'

        if result_check == 'ok':
            return 'ok'
        elif result_check == 'len_error':
            return 'len_error'

    # Метод отображения данных в диалоговом окне при добавлении предмета
    def open_add_dialog_window(self, sistem_assessment: int):
        self.label.setText('Добавление предмета')
        self.setWindowTitle('Добавление предмета')

        # Вызывам метод добавления в QCombobox всех возможных предметов
        self.add_title_subj_in_combobox()

        # Задаем некоторые параметры для полей и кнопок в диалоговом окне
        self.comboBox.setEnabled(True)  # Разрешаем выбор предмета
        self.lineEdit.setText('')  # В момент добавления нового предмета поле оценок пустое

        if sistem_assessment == 5:
            self.comboBox_2.addItems(['3', '4', '5'])
        elif sistem_assessment == 10:
            self.comboBox_2.addItems(['4', '5', '6', '7', '8', '9', '10'])

        # При нажатии на кнопку вызываем метод добавления нового предмета
        self.pushButton_set.clicked.connect(self.add_new_subject)

    # Метод отображения данных в диалоговом окне при редактировании предмета
    def open_up_dialog_window(self, subject, assessment, super_assessment, sistem_assessment):
        self.label.setText('Редактирование предмета')
        self.setWindowTitle('Редактирование предмета')

        # Вызывам метод добавления в QCombobox всех возможных предметов (но их невозможно выбрать)
        self.add_title_subj_in_combobox()

        # Создаем некоторые параметры для полей и кнопок в диалоговом окне.
        # Подстановка в форму уже существующих значений из таблицы с блокировкой выбора предмета
        self.comboBox.setCurrentText(subject)
        self.comboBox.setEnabled(False)
        self.lineEdit.setText(assessment)

        if sistem_assessment == 5:
            self.comboBox_2.addItems(['3', '4', '5'])
        elif sistem_assessment == 10:
            self.comboBox_2.addItems(['4', '5', '6', '7', '8', '9', '10'])

        self.comboBox_2.setCurrentText(super_assessment)

        # При нажатии на кнопку вызываем метод редактирования предмета
        self.pushButton_set.clicked.connect(self.update_subject)

    # Метод добавления предмета (через вызов метода добавления в классе по работе с БД)
    def add_new_subject(self):
        cur = self.con.cursor()

        # Получаем предмет, оценки, супер-оценку с формы
        subject = self.comboBox.currentText()
        assessment = ''.join(self.lineEdit.text().split())
        super_assessment = self.comboBox_2.currentText()

        # Если проверка оценок успешна
        if self.check_corrected_assessment(assessment) == 'ok':
            # Получаем систему оценки
            sistem_assessment = self.main_window.return_sistem_assessment()

            # Результат выполнения метода по вычислению нужных оценок
            result_process = self.algoritm_process(int(super_assessment), ''.join(list(assessment)))

            # Если система оценок 10, находим 'gpa' для него
            if sistem_assessment == 10:
                spis_del_10 = assessment.strip().split('10')
                col_10 = len(spis_del_10) - 1
                list_int_grade = list(map(lambda x: int(x), ''.join(spis_del_10)))

                for i in range(col_10):
                    list_int_grade.append(10)

                gpa = round(sum(list_int_grade) / len(list_int_grade), 2)

            # Если система оценок 5, находим 'gpa' для него
            else:
                gpa = round(sum([int(ass) for ass in assessment]) / len(assessment), 2)

            # Получаем из БД результат по выбранному предмету
            rows = cur.execute("""
                SELECT *
                FROM spis_record
                WHERE id = (
                    SELECT id
                    FROM spis_subject
                    WHERE title = ?
                )
                """, (subject,)).fetchall()

            # Если длина результата = 0, то предмет еще не добавлен и мы реализуем добавление
            if len(rows) == 0:
                # Обращаемся к экземпляру класса по работе с БД и вызываем метод добавления нового предмета
                self.connection.addition_new_subject(subject, assessment, super_assessment,
                                                     result_process[0], result_process[1], gpa)

                # Отображаем изменения в главном окне через его экземпляр
                self.main_window.preview_data()

                # Оповещаем если добавили запись в БД
                alert = QMessageBox(self)
                alert.setText('Предмет упешно добавлен!')
                alert.setIcon(QMessageBox.Information)
                alert.setStandardButtons(QMessageBox.Ok)
                alert.exec()

                # При успешном действии закрываем окно
                self.close()

            else:
                # Оповещаем если запись уже есть в БД
                alert = QMessageBox(self)
                alert.setText('Предмет уже был добавлен!')
                alert.setIcon(QMessageBox.Warning)
                alert.setStandardButtons(QMessageBox.Ok)
                alert.exec()

        # Если оценки введены некорректно
        elif self.check_corrected_assessment(assessment) == 'value_error':
            alert = QMessageBox(self)
            alert.setText('Неверно введены оценки!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

        # Если ничего не ввели в поле ввода
        elif self.check_corrected_assessment(assessment) == 'len_error':
            alert = QMessageBox(self)
            alert.setText('Введите оценки!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

        # Если ввели ноль некорректно
        elif self.check_corrected_assessment(assessment) == 'input_zero':
            alert = QMessageBox(self)
            alert.setText('Некорректный ввод оценок!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

    # Метод редактирования предмета (через вызов метода редактирования в классе по работе с БД)
    def update_subject(self):
        # Получаем подтянутые на форму предмет, оценки, супер-оценку
        subject = self.comboBox.currentText()
        assessment = ''.join(self.lineEdit.text().split())
        super_assessment = self.comboBox_2.currentText()

        # Если проверка оценок успешна
        if self.check_corrected_assessment(assessment) == 'ok':
            # Получаем систему оценки
            sistem_assessment = self.main_window.return_sistem_assessment()

            # Результат выполнения метода по вычислению нужных оценок
            result_process = self.algoritm_process(int(super_assessment), ''.join(list(assessment)))

            # Если система оценок 10, находим 'gpa' для него
            if sistem_assessment == 10:
                spis_del_10 = assessment.strip().split('10')
                col_10 = len(spis_del_10) - 1
                list_int_grade = list(map(lambda x: int(x), ''.join(spis_del_10)))

                for i in range(col_10):
                    list_int_grade.append(10)

                gpa = round(sum(list_int_grade) / len(list_int_grade), 2)

            # Если система оценок 5, находим 'gpa' для него
            else:
                gpa = round(sum([int(ass) for ass in assessment]) / len(assessment), 2)

            # Обращаемся к экземпляру класса по работе с БД и вызываем метод редактирования предмета
            self.connection.update_subject(subject, assessment, super_assessment,
                                           result_process[0], result_process[1], gpa)

            # Отображаем изменения в главном окне через его экземпляр
            self.main_window.preview_data()

            # Оповещаем если добавили запись в БД
            alert = QMessageBox(self)
            alert.setText('Оценки успешно изменены!')
            alert.setIcon(QMessageBox.Information)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

            # При успешном действии закрываем окно
            self.close()

        # Если оценки введены некорректно
        elif self.check_corrected_assessment(assessment) == 'value_error':
            alert = QMessageBox(self)
            alert.setText('Неверно введены оценки!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

        # Если ничего не ввели в поле ввода
        elif self.check_corrected_assessment(assessment) == 'len_error':
            alert = QMessageBox(self)
            alert.setText('Введите оценки!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

        # Если ввели ноль некорректно
        elif self.check_corrected_assessment(assessment) == 'input_zero':
            alert = QMessageBox(self)
            alert.setText('Некорректный ввод оценок!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()

    # Метод импортирования данных из файла в таблицу
    def download_file_csv(self, file_path):
        cur = self.con.cursor()

        # Получаем названия всех предметов
        set_subj_for_combobox = cur.execute("""
            SELECT title 
            FROM spis_subject
        """).fetchall()
        set_subj_for_combobox = [cor[0] for cor in set_subj_for_combobox]

        # Список всех уже добавленных названий предметов
        set_subj_for_record = cur.execute("""
            SELECT title
            FROM spis_subject
            WHERE id IN (
                SELECT id
                FROM spis_record
            )
        """).fetchall()
        set_subj_for_record = [cor[0] for cor in set_subj_for_record]
        self.con.commit()

        all_rows = []  # неотсортированный списток данных
        all_rows_sort = []

        with open(file_path, 'r', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                all_rows.append(row)

            # Выполняем все необходимые проверки при чтении данных из файла
            for row in all_rows[1:]:
                if row[0] in set_subj_for_combobox and row[0] not in set_subj_for_record:
                    if self.check_corrected_assessment(''.join(row[1].split())) == 'ok':
                        if self.main_window.return_sistem_assessment() == 10:
                            if 1 <= int(row[2]) <= self.main_window.return_sistem_assessment():
                                all_rows_sort.append(row)
                        elif self.main_window.return_sistem_assessment() == 5:
                            if 1 <= int(row[2]) <= self.main_window.return_sistem_assessment():
                                all_rows_sort.append(row)

        # Если корректных записей в файле не нашлось
        if len(all_rows_sort) == 0:
            alert = QMessageBox()
            alert.setText('Файл содержит некорректные или уже добавленные записи!')
            alert.setIcon(QMessageBox.Warning)
            alert.setStandardButtons(QMessageBox.Ok)
            alert.exec()
            return

        # Если в файле есть корректыне записи для добавления
        for row in all_rows_sort:
            # Получаем каждые данные строки
            subject = row[0]
            assessment = ''.join(row[1].split())
            super_assessment = row[2]
            col_5, col_current = self.algoritm_process(int(row[2]), ''.join(list(''.join(row[1].split()))))

            # Если система оценивания = '10', находим средний балл для нее
            if self.main_window.return_sistem_assessment() == 10:
                spis_del_10 = assessment.strip().split('10')
                col_10 = len(spis_del_10) - 1
                list_int_grade = list(map(lambda x: int(x), ''.join(spis_del_10)))

                for i in range(col_10):
                    list_int_grade.append(10)

                gpa = round(sum(list_int_grade) / len(list_int_grade), 2)

            # Если система оценивания = '5', находим средний балл для нее
            else:
                gpa = round(sum([int(ass) for ass in assessment]) / len(assessment), 2)

            self.connection.addition_new_subject(subject, assessment, super_assessment, col_5, col_current, gpa)

            self.main_window.preview_data()

        alert = QMessageBox()
        alert.setText('Файл успешно импортирован!')
        alert.setIcon(QMessageBox.Information)
        alert.setStandardButtons(QMessageBox.Ok)
        alert.exec()