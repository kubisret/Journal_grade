import sqlite3


# Главный класс по работе с БД
class Data:
    def __init__(self):
        super(Data, self).__init__()
        self.con = sqlite3.connect('data_base_one.db')

    # Метод добавления в таблицу spis_record новой записи
    def addition_new_subject(self, subject, assessment, super_assessment, col_5, col_current, GPA):
        # Подключаем курсор для работы с содержимым БД
        cur = self.con.cursor()

        # id предмета, который хотим добавим
        id = cur.execute("""
            SELECT id
            FROM spis_subject
            WHERE title = ?
        """, (subject,)).fetchall()[0][0]

        # Если в таблице записей еще нет нового предмета
        try:
            cur.execute("""
                INSERT INTO spis_record 
                    (id, assessment, super_assessment, col_5, col_current, GPA)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id, assessment, super_assessment, col_5, col_current, GPA))

            self.con.commit()

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

        except sqlite3.IntegrityError:
            pass

        # Фиксируем изменения в БД
        self.con.commit()

    # Метод изменения записи в таблице spis_record
    def update_subject(self, subject, assessment, super_assessment, col_5, col_current, GPA):
        cur = self.con.cursor()

        id = cur.execute("""
            SELECT id
            FROM spis_subject
            WHERE title = ?
        """, (subject,)).fetchall()[0][0]

        cur.execute("""
            UPDATE spis_record 
            SET assessment = ?, super_assessment = ?, col_5 = ?, col_current = ?, GPA = ?
            WHERE id = ?
        """, (assessment, super_assessment, col_5, col_current, round(GPA, 2), id))

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

    # Метод удаления записи из таблицы spis_record
    def delete_subject(self, subject):
        cur = self.con.cursor()

        # Получаем id предмета, который хотим удалить
        id = cur.execute("""
            SELECT id
            FROM spis_subject
            WHERE title = ?
         """, (subject,)).fetchall()[0][0]

        # Выполняем запрос по удалению предмета
        cur.execute("""
            DELETE
            FROM spis_record 
            WHERE id = ?
        """, (id,))

        # Фиксируем изменения в БД
        self.con.commit()

    # Метод вычисления данных из таблицы spis_record для отображения на главном окне программы
    def calculation_values_on_main_window(self, sistem_assessment):
        cur = self.con.cursor()

        # Получаем содержимое таблицы spis_record
        result = cur.execute("""
                SELECT * 
                FROM spis_record 
                """).fetchall()

        # Список для добавления всех оценок
        all_assessments = []

        if sistem_assessment == 10:
            all_assessments_ = ''
            for corteg_line in result:
                all_assessments_ += corteg_line[1]

            spis_del_10 = all_assessments_.split('10')
            col_10 = len(spis_del_10) - 1
            all_assessments = list(map(lambda x: int(x), ''.join(spis_del_10)))
            for i in range(col_10):
                all_assessments.append(10)

        elif sistem_assessment == 5:
            for corteg_line in result:
                all_assessments.extend([int(ass) for ass in list(corteg_line[1])])

        # Если список оценок не пуст
        if len(all_assessments) != 0:

            # Список для добавления всех супер-оценок
            all_super_assessments = []
            for corteg_line in result:
                all_super_assessments.extend([corteg_line[2]])

            # Количество выполненных предметов
            col_sucessful = 0
            for corteg_line in result:
                if corteg_line[5] >= corteg_line[2] - 0.5:
                    col_sucessful += 1

            # Вычисления кол-ва добавленных предметов;
            # среднего балла по всем предметам;
            # супер-среднего балла по всем предметам;
            # кол-ва выполненных предметов
            col_subject = len(result)

            all_gpa = cur.execute("""
                        SELECT super_assessment
                        FROM spis_record
                    """).fetchall()

            all_aver = cur.execute("""
                SELECT GPA
                FROM spis_record
            """).fetchall()

            all_gpa = [gpa[0] for gpa in all_gpa]
            new_gpa = round(sum(all_gpa) / len(all_gpa), 2)

            all_aver = [aver[0] for aver in all_aver]
            new_aver = round(sum(all_aver) / len(all_aver), 2)

            average_point = new_aver
            super_average_point = new_gpa
            col_sucessful = col_sucessful

            # Возвращаем результат
            return col_subject, average_point, super_average_point, col_sucessful

        else:
            # Если оценок нет --> таблица QTableWidget пустая, отображаем '0.0'
            col_subject = '0'
            average_point = '0.0'
            super_average_point = '0.0'
            col_sucessful = '0'

            # Возвращаем результат выполнения метода
            return col_subject, average_point, super_average_point, col_sucessful