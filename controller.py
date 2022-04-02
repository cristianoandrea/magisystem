import threading
import datetime
import time

import commons
import datacalcio
import scraper
import segnalatore



C_SALVA = 'salva'
C_ISTANZIA = 'istanzia'
C_SCARICA = 'scarica'
C_CALCOLA = 'calcola'
C_ESCI = 'esci'
C_PARTITE = 'partite'
C_SQUADRE = 'squadre'
C_NPARTITE = 'npartite'
C_SCARICAOGGI = 'oggi'
C_CAMBIA = 'cambia'

campionati = {}
partiteOggi = []
papabili = []

inEsecuzione = True



def main():
    global campionati
    serieA = commons.Campionato(commons.NomeCampionato.SERIEA)
    campionati[serieA.getNome()] = serieA
    bundesliga = commons.Campionato(commons.NomeCampionato.BUNDESLIGA)
    campionati[bundesliga.getNome()] = bundesliga
    laLiga = commons.Campionato(commons.NomeCampionato.LALIGA)
    campionati[laLiga.getNome()] = laLiga
    ligue1 = commons.Campionato(commons.NomeCampionato.LIGUE1)
    campionati[ligue1.getNome()] = ligue1
    premier = commons.Campionato(commons.NomeCampionato.PREMIER)
    campionati[premier.getNome()] = premier


    while inEsecuzione:
        print('>>> ', end='')
        comando = input()
        if comando == C_SCARICA: download()
        elif comando == C_CALCOLA: calcola()
        elif comando == C_SCARICAOGGI: scaricaOggi()
        elif comando == C_ISTANZIA: eseguiIstanziazione()
        elif comando == C_SALVA: eseguiSalvataggio(serieA)
        elif comando == C_ESCI: termina()
        elif comando == C_CAMBIA: cambia()
        else: print('comando non valido')



def download():
    """
        Effettua il download di tutte le partite della stagione attuale per ogni campionato seguito
    """
    global campionati
    #lista di thread per poter attendere la terminazione di tutti
    attese = []
    for campionato in campionati.values():
        campionato.downloadPartite()
    """for campionato in campionati.values():
        t = threading.Thread(target=campionato.downloadPartite)
        t.start()
        attese.append(t)
    for i in range(0, len(attese)):
        t = attese[i]
        t.join()"""

def calcola():
    """
        Effettua il calcolo per il valore di a migliore per ogni campionato seguito
    """
    global campionati
    #lista di thread per poter attendere la terminazione di tutti
    attese = []
    for campionato in campionati.values():
        campionato.calcolaA(stampa=True)
    """for campionato in campionati.values():
        t = threading.Thread(target=campionato.calcolaA)
        t.start()
        attese.append(t)
    for i in range(0, len(attese)):
        t = attese[i]
        t.join()"""

def scaricaOggi():
    """
        Salva le partite che giocano oggi e manda sul canale un avviso di quali sono.
        A seguire comincia il processo che tiene sotto controllo le partite su cui giocare oggi
        e per tale motivo questa funzione presuppone che calcola() sia già stata eseguita
    """
    global partiteOggi, papabili
    partiteOggi = []
    papabili = []

    for campionato in campionati.values():
        partiteOggi += scraper.partite_di_oggi(campionato)
    
    for i in range(len(partiteOggi)):
        if commons.SuperOverTester.valutaProposta(partiteOggi[i]):
            partiteOggi[i].setStrategia(commons.Strategia.SUPEROVER)
            papabili.append(partiteOggi[i])
            print('suggerita', partiteOggi[i].nome, 'con probabilità di', partiteOggi[i].tester.probPer(partiteOggi[i]))
        else:
            partiteOggi[i].setStrategia(commons.Strategia.SUPEROVER)
            print('non suggerita', partiteOggi[i].nome, 'con probabilità di', partiteOggi[i].tester.probPer(partiteOggi[i]))
    messaggio = 'Partite papabili per oggi:\n'
    for i in range(len(papabili)):
        messaggio += papabili[i].nome
        messaggio += ' delle '
        messaggio += papabili[i].orario
        messaggio += ' con probabilità del '
        messaggio += str(papabili[i].tester.probPer(papabili[i]))
        messaggio += '\n'
    segnalatore.inviaMessaggio(messaggio)
    t = threading.Thread(target=controllo)
    #t.start()

def controllo():
    """
        Esegue il controllo per le partite passate in input su se entrare e quando, fino a che
        almeno una partita deve ancora finire o non si è usciti
    """
    global papabili
    #p = []
    i = 0
    while len(papabili) > 0 and inEsecuzione:
        if papabili[i].data < datetime.datetime.now():
            #si è già entrati nella partita
            if papabili[i].ingressoFatto:
                #TODO: aggiorna i campi di papabili[i]
                tester = papabili[i].tester
                if tester.valutaUscita(papabili[i]):
                    #TODO: mandare il messaggio di uscita
                    try:
                        papabili.remove(papabili[i])
                    except ValueError:
                        print('IMPORTANTE: la rimozione di un elemento dalla lista delle papabili è fallita, possibile ciclo infinito')
                        i += 1
                else:
                    #i non è incrementato in caso di rimozione perché papabili[i] è stato rimosso e la posizione i è ora occupata 
                    #dall'elemento successivo
                    i += 1
            #si deve ancora entrare
            else:
                tester = papabili[i].tester
                if tester.valutaIngresso(papabili[i]):
                    #TODO: mandare il messaggio di ingresso
                    papabili[i].confermaIngresso()
                i += 1
        #dato che bisogna ciclare più volte se si è arrivati alla fine della lista si riparte dall'inizio
        #si esegue anche sleep per porre il thread in attesa per un minuto, non c'è bisogno di ciclare di continuo
        if i == len(papabili):
            i = 0
            time.sleep(60)


def cambia():
    print('Nuovo limite:')
    n = float(input())
    if n > 0.79 and n < 1:
        commons.SOGLIA_SO = n
        commons.SuperOverTester.SOGLIA_SO = n




def eseguiSalvataggio(campionato):
    datacalcio.istanza_a_db(campionato.getPartite())

def eseguiIstanziazione():
    #global serieA
    partite = datacalcio.istanzia_partite()
    partite.sort(key=commons.Partita.compare)
    for partita in partite:
        sqCasa = partita.getSquadraCasa()
        sqTrasferta = partita.getSquadraTrasferta()
        sqCasa.aggiungiPartita(partita)
        sqTrasferta.aggiungiPartita(partita)
        #serieA.aggiungiPartita(partita)


def termina():
    """
        Funzione per terminare correttamente l'esecuzione del programma
    """
    global inEsecuzione
    inEsecuzione = False


main()