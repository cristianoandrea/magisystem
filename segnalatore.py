import threading
import telebot
import os
import random

dirPath = os.path.dirname(os.path.realpath(__file__))

#costanti per il bot
TOKEN = '1723137580:AAFYpcTKMesS-f7rrqMy00WvmJ0fgK1z5eM'
ID_GRUPPO = -1001192984315
ID_CANALE = -1001490967676
#costanti per le cartelle
GIF_DIR_PATH = dirPath + '/gif'
PORNO_DIR_PATH = GIF_DIR_PATH + '/porno'
HENTAI_DIR_PATH = GIF_DIR_PATH + '/hentai'
#liste di messaggi del bot
godopoli = [ ]
tristopoli = [ ]


bot = telebot.TeleBot(TOKEN)


def segnalatoreInit():
    godopoliInit()
    tristopoliInit()

def godopoliInit():
    #godopoli.append('')
    godopoli.append('godopoli')
    godopoli.append('SI SBORRA')
    godopoli.append('ez godopoli')
    godopoli.append('agile win')
    godopoli.append('ez win')
    godopoli.append('agilopoli')
    godopoli.append('gg go next')
    godopoli.append('next tutorial')

def tristopoliInit():
    #tristopoli.append('')
    tristopoli.append('F')
    tristopoli.append('a regà me spiace')
    tristopoli.append('nun se po perde così ner 2019')


def inviaMessaggio(testo):
    """
        Invia il messaggio testo sul canale salvato
    """
    try:
        bot.send_message(ID_CANALE, testo)
    except Exception:
        print('Segnalatore: impposibile inviare un messaggio')


def segnalaCashout():
    """
        Manda il messaggio che segnala di fare cashout sulla partita
    """
    pass


def poll():
    """
        Cominciare l'esecuzione del bot per la ricezione e l'invio
        di messaggi
    """
    thread = threading.Thread(target=bot.polling)
    thread.start()


def stop():
    """
        Termina l'esecuzione del bot
    """
    bot.stop_polling()

    
def randGifPorno():
    """
        Ritorna, aperto in byte e lettura, il file di una gif porno
    """
    listaGif = os.listdir(PORNO_DIR_PATH)
    idx = random.randint(0, len(listaGif)-1)
    f = open(PORNO_DIR_PATH+listaGif[idx], 'rb')
    return f


def randGifHentai():
    """
        Ritorna, aperto in byte e lettura, il file di una gif hentai
    """
    listaGif = os.listdir(HENTAI_DIR_PATH)
    idx = random.randint(0, len(listaGif)-1)
    f = open(HENTAI_DIR_PATH+listaGif[idx], 'rb')
    return f


def randGodopoli():
    """
        Ritorna un messaggio str da comunicare in caso di evento andato bene
    """
    idx = random.randint(0, len(godopoli)-1)
    return godopoli[idx]


def randTristopoli():
    """
        Ritorna un messaggio str da comunicare in caso di evento andato male
    """
    idx = random.randint(0, len(tristopoli)-1)
    return tristopoli[idx]




#@bot.message_handler(commands=[''])


#print('inizio')
#bot.polling()
bot.send_message(ID_CANALE, 'lello gay')
#print('fatto')
