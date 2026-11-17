import telebot
import sqlite3
import os

# Токен берется из настроек сервера
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('notes.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)''')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я работаю с сервера 24/7.\n/list — список.\n/del [ID] — удалить.")

@bot.message_handler(commands=['list'])
def list_notes(message):
    cursor.execute("SELECT id, text FROM notes")
    rows = cursor.fetchall()
    if not rows:
        bot.reply_to(message, "Заметок пока нет.")
        return
    response = "📝 Твои заметки:\n\n"
    for row in rows:
        response += f"{row[0]}. {row[1]}\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=['del'])
def delete_note(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Укажи ID. Пример: /del 2")
        return
    try:
        note_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "⚠️ ID должен быть числом.")
        return

    cursor.execute("SELECT text FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    if row is None:
        bot.reply_to(message, f"❌ Заметка {note_id} не найдена.")
    else:
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        bot.reply_to(message, f"🗑 Удалена: «{row[0]}»")

@bot.message_handler(func=lambda message: True)
def save_note(message):
    cursor.execute("INSERT INTO notes (text) VALUES (?)", (message.text,))
    conn.commit()
    bot.reply_to(message, f"✅ Сохранено! (ID: {cursor.lastrowid})")

print("Бот запущен на сервере...")
bot.infinity_polling()
