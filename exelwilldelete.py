import logging
import random
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


user_balances = {}
user_items = {}
user_last_claim = {}


shop_items = {
    "Luck": {"price": 20, "description": "Сразу два прокрута."},
}

DAILY_REWARD = 100


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0  
    if user_id not in user_items:
        user_items[user_id] = [] 
    if user_id not in user_last_claim:
    update.message.reply_text('Дарова мы тут кости бросаем напиши маляву /roll для прокрута, /shop что в магазине есть, или /daily чтоб получить лавэшечку.')

def roll_dice(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    win_number = 6
    win_amount = 25  
    lose_amount = 10

    if dice_roll == win_number:
        user_balances[user_id] += win_amount
        update.message.reply_text(f'Прокрут {dice_roll}! 🎲 ты выиграл ${win_amount}! твой балик ${user_balances[user_id]}.')
    else:
         user_balances[user_id] -= lose_amount
         update.message.reply_text(f'Прокрут {dice_roll}. Проиграл на ставках твой балик ${user_balances[user_id]}.')

    if "Luck" in user_items.get(user_id, []):
      
        second_dice_roll = random.randint(1, 6)
        total_roll = dice_roll + second_dice_roll
        update.message.reply_text(f'Сразу два: {second_dice_roll}. Тотально: {total_roll}')
        if total_roll == 6:
            user_balances[user_id] += win_amount
            update.message.reply_text(f'Ты выиграл ${win_amount}! Вот тебе лавэшечка${user_balances[user_id]}.')
        else:
            update.message.reply_text(f'Проиграл на ставках {total_roll}.Твой балик ${user_balances[user_id]}.')

def shop(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    reply_text = "Это шоп кракена:\n\n"
    for item, details in shop_items.items():
        price = details["price"]
        description = details["description"]
        reply_text += f"• {item}: ${price} - {description}\n"

    reply_text += "\nИспользуй /buy <item_name> и выбери его."
    update.message.reply_text(reply_text)


def buy_item(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        update.message.reply_text('Слушай специальный предмет для покупки. Используй шоп /shop чтобы видеть  предметы.')
        return

    item_name = ' '.join(context.args)
    if item_name in shop_items:
        item_price = shop_items[item_name]["price"]
        if user_balances.get(user_id, 0) >= item_price:
            user_balances[user_id] -= item_price
            user_items[user_id].append(item_name)
            update.message.reply_text(f'У тебя есть {item_name}! твой балик ${user_balances[user_id]}.')
        else:
            update.message.reply_text(f'Лавэ нету! Бомжара {item_name}. Не смотри!!! ${user_balances.get(user_id, 0)}.')
    else:
        update.message.reply_text(f'Таких поставок у нас нету.')

def daily_reward(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_time = datetime.now()

    if user_id in user_last_claim:
        last_claim_time = user_last_claim[user_id]
        if last_claim_time and current_time - last_claim_time < timedelta(days=1):
            time_remaining = timedelta(days=1) - (current_time - last_claim_time)
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            update.message.reply_text(f'Ты можешь получить только после {hours} часа {minutes} минуты.')
            return

    
    user_balances[user_id] += DAILY_REWARD
    user_last_claim[user_id] = current_time
    update.message.reply_text(f'Лавэшечка ${DAILY_REWARD}! Балик растет ${user_balances[user_id]}.')


def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    balance = user_balances.get(user_id, 0)
    update.message.reply_text(f'Твой балик давай чтоб больше было!: ${balance}.')

def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main() -> None:
  
    updater = Updater("your token")


    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("roll", roll_dice))
    dispatcher.add_handler(CommandHandler("shop", shop))
    dispatcher.add_handler(CommandHandler("buy", buy_item))
    dispatcher.add_handler(CommandHandler("daily", daily_reward))
    dispatcher.add_handler(CommandHandler("balance", balance))


    dispatcher.add_error_handler(error)


    updater.start_polling()


    updater.idle()

if __name__ == '__main__':
    main()
