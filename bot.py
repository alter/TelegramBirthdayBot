import csv
import logging
import datetime
import pytz
import os
from pathlib import Path
from telegram import Update
from telegram.ext import (
   Application, 
   CommandHandler,
   ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BirthdayBot:
   def __init__(self, token: str, chat_id: str, csv_path: str):
       self.token = token
       self.chat_id = chat_id
       self.csv_path = Path(csv_path)
       self.birthdays = {}
       self.last_modified = 0

   def load_birthdays(self):
       if not self.csv_path.exists():
           logger.error(f"CSV not found: {self.csv_path}")
           return
       
       current_modified = self.csv_path.stat().st_mtime
       if current_modified <= self.last_modified:
           return
           
       self.last_modified = current_modified
       self.birthdays.clear()
       
       with open(self.csv_path, 'r', encoding='utf-8') as file:
           reader = csv.reader(file)
           for row in reader:
               if not (2 <= len(row) <= 3):
                   continue
               try:
                   name = row[0].strip()
                   date = datetime.datetime.strptime(f"{row[1].strip()}-2024", '%d-%m-%Y')
                   username = row[2].strip() if len(row) > 2 and row[2].strip() else None
                   date_str = date.strftime('%d-%m')
                   if date_str not in self.birthdays:
                       self.birthdays[date_str] = []
                   self.birthdays[date_str].append((name, username, date))
               except (ValueError, IndexError):
                   continue
       logger.info("Birthdays loaded successfully")

   def get_todays_birthdays(self):
       today = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d-%m')
       return self.birthdays.get(today, [])

   async def check_birthdays(self, context: ContextTypes.DEFAULT_TYPE):
       self.load_birthdays()
       birthdays = self.get_todays_birthdays()
       if birthdays:
           await self.send_birthday_messages(context, birthdays)

   async def send_birthday_messages(self, context, birthdays):
       messages = []
       for name, username, _ in birthdays:
           message = f"Сегодня день рождения у: {name}"
           if username:
               message += f" ({username})"
           messages.append(message)
       await context.bot.send_message(
           chat_id=self.chat_id,
           text="\n".join(messages)
       )

   async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       await update.message.reply_text('Бот запущен!')

   async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       help_text = """
Доступные команды:
/help - показать это сообщение
/today - показать дни рождения сегодня
/birthdays - показать все дни рождения"""
       await update.message.reply_text(help_text)

   async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       self.load_birthdays()
       birthdays = self.get_todays_birthdays()
       if not birthdays:
           await update.message.reply_text("Сегодня нет дней рождения")
           return
       await update.message.reply_text("\n".join(
           f"{name} ({username})" if username else name 
           for name, username, _ in birthdays
       ))

   async def birthdays_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       self.load_birthdays()
       current_month = datetime.datetime.now().month
       sorted_birthdays = []
       
       for date_str, persons in self.birthdays.items():
           for person in persons:
               sorted_birthdays.append((person[2], person[0], person[1]))
       
       sorted_birthdays.sort(key=lambda x: (
           (x[0].month - current_month) % 12,
           x[0].day
       ))

       result = []
       current_month = None
       for date, name, username in sorted_birthdays:
           if date.month != current_month:
               current_month = date.month
               result.append(f"\n{date.strftime('%B')}:")
           result.append(f"{date.day}: {name}" + (f" ({username})" if username else ""))

       await update.message.reply_text("\n".join(result) if result else "Нет дней рождения")

def main():
   from dotenv import load_dotenv
   load_dotenv()

   token = os.getenv('TELEGRAM_BOT_TOKEN')
   chat_id = os.getenv('TELEGRAM_CHAT_ID')
   csv_path = os.getenv('CSV_PATH', '/app/birthdays.csv')

   bot = BirthdayBot(token, chat_id, csv_path)
   app = Application.builder().token(token).build()
   
   app.add_handler(CommandHandler("start", bot.start))
   app.add_handler(CommandHandler("help", bot.help_command))
   app.add_handler(CommandHandler("today", bot.today_command))
   app.add_handler(CommandHandler("birthdays", bot.birthdays_command))

   job_queue = app.job_queue
   job_queue.run_daily(
       bot.check_birthdays,
       time=datetime.time(hour=8, minute=0), 
       days=(0,1,2,3,4,5,6)
   )
   
   # Check birthdays on startup
   job_queue.run_once(bot.check_birthdays, 1)

   app.run_polling()

if __name__ == '__main__':
   main()
