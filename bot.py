# Bot Creato da Lorenzo Carta, Tommaso Battistoni, Leonardo Rossi e Alessandro Caruso sul dataset della Ronda della Carità di Verona
# Seguiti dal docente Antonio Faccioli di 37100LAB Verona, in collaborazione con ITS Academy LAST
# Questo bot importa e analizza i dati del DB, crea grafici e istogrammi per la comunicazione con l'utente
# Il bot è stato creato con Python, utilizzando le librerie telegram, per la gestione del bot, sqlite3, per la comunicazione con il database e matplotlib per la creazione degli istogrammi

from unicodedata import category
import telegram
from telegram import *
from telegram.ext import *
from requests import *
import os
import sqlite3
import matplotlib.pyplot as plt
from datetime import *

# Inizializzazione Bot
# Inserire il token fornito da BotFather tramite Telegram
token = ""
bot = telegram.Bot(token)

# Creo un dizionario per l'ascissa dell'istogramma
months = ["Gen.",
          "Feb.",
          "Mar.",
          "Apr.",
          "Mag.",
          "Giu.",
          "Lug.",
          "Ago.",
          "Set.",
          "Ott.",
          "Nov.",
          "Dic."
          ]

# Bottoni Inline
options = [
        [InlineKeyboardButton("Media Vestiti 2021 👚", callback_data='1')],
        [InlineKeyboardButton("Media Avanzi Mensili 2021 🚽", callback_data='2')],
        [InlineKeyboardButton("Giorni di frutta nel 2021 🍌", callback_data='3')],
        [InlineKeyboardButton("Media Coperte Consegnate 2021 🛌🏻", callback_data='4')],
        [InlineKeyboardButton("Media Volontari Mensili 2021 🤗", callback_data='5')],
        [InlineKeyboardButton("Pasti Pronti Mensili 2021 🥙", callback_data='6')]

        ]

# Creo la logica del bottone sfruttando le callback delle options
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    if(query.data == '1'):
        mediaVestiti(update, context)
    elif(query.data == '2'):
        mediaAvanzi(update, context)
    elif(query.data == '3'):
        giorniFrutta(update, context)
    elif(query.data == '4'):
        mediaCoperte(update, context)
    elif(query.data == '5'):
        mediaVolontari(update, context)
    elif(query.data == '6'):
        totPasti(update, context)

# Connessione al DB
# Nota, il DB dev'essere nella stessa cartella dello script Python
def dbStart():
    db = "caritaDB.db"
    db_exists = not os.path.exists(db)
    conn = sqlite3.connect(db)
    if db_exists:
        print("Il db non esisteva, l'ho creato")
    else:
        print("Database esistente")
    cur = conn.cursor()
    return cur

# Chiudo la connessione
def dbEnd():
    db = "caritaDB.db"
    conn = sqlite3.connect(db)
    conn.close()
    
# Crea Nome File
# Questa funzione crea un nome per il file, in modo da poterlo salvare in una cartella. Il nome è generato in base all'ora/minuto/secondo del momento in cui viene creato il file
# per abbassare la probabilità di duplicati
def creaNomeFile():
    now = datetime.now()
    nomefile = str(now.strftime("%H%M%S")) + ".jpg"
    return nomefile

# Start
def start(update, context):
    chat_id = update.effective_chat.id
    print("start called from chat with id = {}".format(chat_id))
    update.message.reply_text("Benvenuto! Questo bot analizza e diffonde i consumi e gli sprechi effettuati durante le ronde della Carita di Verona")
    reply_markup = InlineKeyboardMarkup(options)
    update.message.reply_text('Scegli per favore:', reply_markup=reply_markup)

# Fine Chat
def end(update):
    chat_id = update.effective_chat.id
    update.message.reply_text("end")
    print("end called from chat with id = {}".format(chat_id))

# Qui iniziano le query per il grafico, nota, al momento della scrittura del programma non ho trovato nessuna funzione di sqlite3 per la gestione efficente delle date,
# perciò, abbiamo creato un operatore ternario per la gestione delle date sfruttando le wildcard delle query.
# ES: Se la data è "01/01/2020" allora la query sarà "%/"0" + indice/%", nel caso in cui il numero del mese superi il 9, l'operatore non aggiungerà lo zero all'indice

# Giorni di Frutta Mensili Primi Consegnati
def giorniFrutta(update, context):
    nomefile = creaNomeFile()
    cur = dbStart()
    datoq1 = []
    for i in range(1,13):
        cur.execute("SELECT count(*) from tabellaCarita WHERE data LIKE '%-" +
                    ("0"+str(i) if i < 10 else str(i)) + "-%' AND frutta == 'si'")
        datoq1.append(int(cur.fetchone()[0]))
    creaIstogrammaAnnuale(datoq1, "Giorni con Frutta nel 2021", nomefile)
    context.bot.send_photo(chat_id=update.effective_chat.id,photo=open(nomefile, 'rb'))
    dbEnd()

# Media Volontari Anno
def mediaVolontari(update, context):
    nomefile = creaNomeFile()
    cur = dbStart()
    datoq2 = []
    for i in range(1,13):
        cur.execute("SELECT avg(totVolontari) from tabellaCarita WHERE data LIKE '%-" +
                    ("0"+str(i) if i < 10 else str(i)) + "-%'")
        datoq2.append(round(float(cur.fetchone()[0])))
    creaIstogrammaAnnuale(datoq2, "Volontari Mensili nel 2021", nomefile)
    context.bot.send_photo(chat_id=update.effective_chat.id,photo=open(nomefile, 'rb'))
    dbEnd()
    
# Media Coperte Consegnate
def mediaCoperte(update, context):
    nomefile = creaNomeFile()
    cur = dbStart()
    datoq3 = []
    for i in range(1,13):
        cur.execute("SELECT avg(coperteConsegnate) from tabellaCarita WHERE data LIKE '%-" +
                    ("0"+str(i) if i < 10 else str(i)) + "-%'")
        datoq3.append(round(float(cur.fetchone()[0])))
    creaIstogrammaAnnuale(datoq3, "Media Coperte nel 2021", nomefile)
    context.bot.send_photo(chat_id=update.effective_chat.id,photo=open(nomefile, 'rb'))
    dbEnd()

# Media vestiti consegnati
def mediaVestiti(update, context):
    nomefile = creaNomeFile()
    cur = dbStart()
    datoq3 = []
    for i in range(1,13):
        cur.execute("SELECT avg(vestitiConsegnati) from tabellaCarita WHERE data LIKE '%-" +
                    ("0"+str(i) if i < 10 else str(i)) + "-%'")
        datoq3.append(round(float(cur.fetchone()[0])))
    creaIstogrammaAnnuale(datoq3, "Media Vestiti Consegnati Mensili nel 2021", nomefile)
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open(nomefile, 'rb'))
    dbEnd()

# Media Avanzi Giornalieri nell'anno
def mediaAvanzi(update, context):
    nomefile = creaNomeFile()   
    cur = dbStart()
    datoq4 = []
    for i in range(1,13):
        cur.execute("SELECT (avg(secondiAvanzati) + avg(primiAvanzati)) from tabellaCarita WHERE data LIKE '%-" +
                    ("0"+str(i) if i < 10 else str(i)) + "-%'")
        datoq4.append(round(float(cur.fetchone()[0])))
    creaIstogrammaAnnuale(datoq4, "Avanzi Mensili nel 2021", nomefile)
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open(nomefile, 'rb'))
    dbEnd()

# Totale dei pasti preparati in ogni mese
def totPasti(update, context):
    nomefile = creaNomeFile()   
    cur = dbStart()
    datoq6 = []
    for i in range(1,13):
        cur.execute("SELECT sum(totPasti) from tabellaCarita WHERE data LIKE '%-" +
                    ("0"+str(i) if i < 10 else str(i)) + "-%'")
        datoq6.append(round(float(cur.fetchone()[0])))
    creaIstogrammaAnnuale(datoq6, "Pasti Mensili nel 2021", nomefile)
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=open(nomefile, 'rb'))
    dbEnd()

# Crea Istrogramma, utilizza il dizionario dei mesi per l'ascissa dell'istogramma, prende come parametri il nome del file, il titolo dell'istogramma e il vettore dei dati
def creaIstogrammaAnnuale(data, title, filename):
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    plt.bar(months, data)
    plt.suptitle(title)
    plt.savefig(filename)
    plt.clf()
    
# Main del bot, qui è presente il poller per la gestione dei messaggi
def main():
    updater = Updater(token)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("end", end))
    updater.start_polling()
    updater.idle()

main()

