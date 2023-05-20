import calendar
from datetime import datetime, timedelta

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

calendar_callback = CallbackData('simple_calendar', 'action', 'year', 'month', 'day')


class SimpleCalendar:
    MONTHS = [
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',
    ]

    async def start_calendar(self,
                             year: int = datetime.now().year,
                             month: int = datetime.now().month) -> InlineKeyboardMarkup:
        """Создает клавиатуру с указанным годом и месяцем

        :param year: год, для использования в календаре, если None, то используется текущий год
        :param month: месяц, для использования в календаре, если None, то используется текущий месяц
        :return: InlineKeyboardMarkup объект с календарем
        """
        inline_kb = InlineKeyboardMarkup(row_width=7)
        ignore_callback = calendar_callback.new('IGNORE', year, month, 0)

        """Первая строка - месяц и год"""
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            '<<',
            callback_data=calendar_callback.new('PREV-YEAR', year, month, 1)
        ))
        str_date = str(self.MONTHS[month - 1])
        inline_kb.insert(InlineKeyboardButton(
            f'{str_date} {str(year)}',
            callback_data=ignore_callback
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=calendar_callback.new('NEXT-YEAR', year, month, 1)
        ))

        """Вторая строка - дни недели"""
        inline_kb.row()

        week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

        for day in week_days:
            inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        """Основные строки - дни месяца"""
        month_calendar = calendar.monthcalendar(year, month)

        """
        [0, 0, 1, 2, 3, 4, 5]    -> 0 0 1 2 3 4 5
        [6, 7, 8, 9, 10, 11, 12] -> 6 7 8 9 10 11 12
        """
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if day == 0:
                    inline_kb.insert(InlineKeyboardButton(
                        ' ',
                        callback_data=ignore_callback
                    ))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day),
                    callback_data=calendar_callback.new('DAY', year, month, day)
                ))

        """Последняя строка - кнопки предыдущего и следующего месяца"""
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            '<',
            callback_data=calendar_callback.new('PREV-MONTH', year, month, day)
        ))

        inline_kb.insert(InlineKeyboardButton('', callback_data=ignore_callback))

        inline_kb.insert(InlineKeyboardButton(
            '>',
            callback_data=calendar_callback.new('NEXT-MONTH', year, month, day)
        ))
        return inline_kb

    async def process_selection(self, query: CallbackQuery, data: CallbackData):
        """Обработка callback_query. Этот метод создает новый календарь при нажатии на кнопки "вперед" или назад.
        Этот метод нужно вызывать внутри CallbackQueryHandler

        :param query: callback_query, как это предусмотрено в CallbackQueryHandler
        :param data: callback_data это словарь созданный с помощью calendar_callback
        :return: Кортеж с датой, если дата была выбрана
        """

        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)

        """Обработка пустых кнопок"""
        if data['action'] == 'IGNORE':
            await query.answer(cache_time=60)

        """Обработка нажатия на день"""
        if data['action'] == 'DAY':
            await query.message.delete_reply_markup()
            year = int(data['year'])
            month = int(data['month'])
            day = int(data['day'])
            return_data = True, datetime(year, month, day)

        """Обработка нажатия на кнопку СЛЕДУЮЩЕГО года"""
        if data['action'] == 'NEXT-YEAR':
            next_date = datetime(int(data['year']) + 1, int(data['month']), 1)
            year = int(next_date.year)
            month = int(next_date.month)
            await query.message.edit_reply_markup(await self.start_calendar(year, month))

        """Обработка нажатия на кнопку ПРЕДЫДУЩЕГО года"""
        if data['action'] == 'PREV-YEAR':
            prev_date = datetime(int(data['year']) - 1, int(data['month']), 1)
            year = int(prev_date.year)
            month = int(prev_date.month)
            await query.message.edit_reply_markup(await self.start_calendar(year, month))

        """Обработка нажатия на кнопку СЛЕДУЮЩЕГО месяца"""
        if data['action'] == 'NEXT-MONTH':
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(next_date.year, next_date.month))

        """Обработка нажатия на кнопку ПРЕДЫДУЩЕГО месяца"""
        if data['action'] == 'PREV-MONTH':
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(prev_date.year, prev_date.month))

        return return_data
