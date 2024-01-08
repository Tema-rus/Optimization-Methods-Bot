import logging

from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler, \
    MessageHandler, filters

from config import TOKEN
from modules.solutions_of_methods import simplex, graphic


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

BASE, TARGET, CONSTRAINTS = range(3)

DATA = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf'Здравствуйте, {user.mention_html()}! Введите команду /help, чтобы увидеть список моих команд.'
    )
    return BASE


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(
        text=rf'Telegram ID: `{update.message.chat_id}`'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        '<b>Стандартные команды:</b>\n'
        '/start - Запустить бота\n'
        '/help - Помощь по командам (Увидеть эту подсказку)\n\n'
        '<b>Команды для работы с методами:</b>\n'
        '/methods - Выбрать метод оптимизации\n'
        '/cancel  - Выйти из контекста\n\n'
        '<b>Служебные команды:</b>\n'
        '/info - Получить информацию о введённых данных\n'
        '/get_chat_id - Получить id чата\n'
    )


async def send_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton('Методы решения ЗЛП', callback_data='1')],
        [InlineKeyboardButton('Метод северо-западного угла', callback_data='2')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите:', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()
    if query.data == '1':
        methods = [
            [InlineKeyboardButton('Симплексный метод (Максимизация)', callback_data='m1')],
            [InlineKeyboardButton('Графический метод (Максимизация)', callback_data='m2')],
            [InlineKeyboardButton('Графический метод (Минимизация)', callback_data='m3')],
        ]
        await query.edit_message_text(
            text=f'Выберите метод оптимизации:',
            reply_markup=InlineKeyboardMarkup(methods)
        )
    else:
        await query.edit_message_text(text=f'Метод северо-западного угла:')
        await context.bot.send_message(update.effective_chat.id, text=f'Здесь ничего нет :(')


async def method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user

    await query.answer()
    match query.data:
        case 'm1':
            await query.edit_message_text(text=f'Симплексный метод (Поиск наибольшего значения)')
            DATA[user.id] = {'method': simplex, 'minmax': 'max', 'target': None, 'constraints': []}
        case 'm2':
            await query.edit_message_text(text=f'Графический метод (Поиск наибольшего значения)')
            DATA[user.id] = {'method': graphic, 'minmax': 'max', 'target': None, 'constraints': []}
        case 'm3':
            await query.edit_message_text(text=f'Графический метод (Поиск наименьшего значения)')
            DATA[user.id] = {'method': graphic, 'minmax': 'min', 'target': None, 'constraints': []}

    await context.bot.send_message(
        chat_id=user.id,
        text=f'Введите коэффициенты при переменных целевой функции через пробел\n'
             f'Например, для выражения 2.3x1-x2, введите "2.3 -1"',
    )
    return TARGET


async def target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    coefficients = update.message.text.strip().split(' ')
    print(f'{coefficients = }')

    try:
        expr = coefficients_to_expression(coefficients)
    except ValueError:
        await update.message.reply_text('Некорректное выражение!')
        return TARGET

    DATA[user.id]['target'] = expr

    await update.message.reply_text(
        text=f'Полученная целевая функция: {expr}→{DATA[user.id]["minmax"]}.\n\n'
             f'Введите коэффициенты ограничений через пробел, отделяя ограничения запятыми.\n'
             f'Например, чтобы ввести ограничения "x1+3*x2≤0.5, -2*x2≤1, x1+x2≥2", '
             f'введите "1 3 <= 0.5, 0 -2 <= 1, 1 1 >= 2"'
    )
    context.user_data.clear()

    return BASE


def coefficients_to_expression(list_of_coeffs: List[str]) -> str:
    expression = ''
    for i, c in enumerate(list_of_coeffs, 1):
        c = float(c)
        if expression and c >= 0:
            expression += '+'
        expression += f'{c}*x{i}'
        print(f'{expression = }')
    return expression


def separate_constraints(expressions: str) -> List[str]:
    expressions = expressions.split(',')
    constraints_list = []
    for expression in expressions:
        expression = expression.strip().split(' ')
        *left, sign, right = expression
        constraints_list.append(f'{coefficients_to_expression(left)}{sign}{float(right)}')
    return constraints_list


async def constraints(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    DATA[user.id]['constraints'] = separate_constraints(update.message.text)
    await update.message.reply_text(
        text=f'Вы ввели следующие ограничения:\n' + ",\n".join(DATA[user.id]["constraints"])
    )

    await solve(update, context)
    await update.message.reply_text('Введите /cancel, чтобы продолжить.')


async def solve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data = DATA[user.id]
    target_function = f'{user_data["target"]}->{user_data["minmax"]}'
    constraints_list = user_data['constraints']

    if user_data['method'] == graphic:
        await update.message.reply_photo(photo=open(
            file=user_data["method"](target_function, constraints_list, user.id),
            mode='rb'
        ))
    else:
        await update.message.reply_text(user_data['method'](target_function, constraints_list, user.id))


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in DATA:
        await update.message.reply_text(text=f'Вы ещё не ввели данные. Введите команду /methods, чтобы начать.')
    else:
        user_data = DATA[user.id]
        await update.message.reply_html(
            text=f'<b>Информация:</b>\n'
                 f'id: {user.id}\n'
                 f'Последний метод решения: {user_data["method"]}\n'
                 f'Стремление к: {user_data["minmax"]}\n'
                 f'Целевая функция: {user_data["target"]}\n'
                 f'Введённые ограничения:\n' + ",\n".join(user_data["constraints"])
        )


async def check_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Текущее состояние: {context.user_data}')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        text=f'Введите команду /help, чтобы узнать список моих команд.'
    )
    return ConversationHandler.END


async def warning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text=f'Я вас не понимаю!\nВведите /help, чтобы узнать список моих команд.')


def main() -> None:
    application = Application.builder().token(TOKEN).concurrent_updates(False).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('methods', send_keyboard))
    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(CommandHandler('check_state', check_state))
    application.add_handler(CommandHandler('info', info_command))

    application.add_handler(CallbackQueryHandler(button, pattern='^[12]$'))
    application.add_handler(CallbackQueryHandler(method, pattern='^m[1-3]$'))

    target_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, target)],
        states={
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, constraints)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    constraints_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, constraints)],
        states={
            CONSTRAINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, constraints)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    base_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
        states={
            BASE: [MessageHandler(filters.TEXT & ~filters.COMMAND, warning)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(target_handler)
    application.add_handler(constraints_handler)
    application.add_handler(base_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
