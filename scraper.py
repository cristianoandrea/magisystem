import datetime
from logging import NullHandler
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from collections import defaultdict
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import threading

import commons

nomeSQ_classname= "vereinprofil_tooltip.tooltipstered"
data_classname= "zentriert.no-border"
minGoalCasa_classname="zentriert.no-border-links"
minGoalTrasferta_classname= "zentriert.no-border-rechts"

def trovaData():
    driver = webdriver.Chrome()



def parsaMese(parola):
    mesi = {}
    mesi['gennaio'] = 1
    mesi['febbraio'] = 2
    mesi['marzo'] = 3
    mesi['aprile'] = 4
    mesi['maggio'] = 5
    mesi['giugno'] = 6
    mesi['luglio'] = 7
    mesi['agosto'] = 8
    mesi['settembre'] = 9
    mesi['ottobre'] = 10
    mesi['novembre'] = 11
    mesi['dicembre'] = 12
    return mesi[parola.lower()]


def parserMese(parola):
    mesi = {}
    mesi['gen'] = 1
    mesi['feb'] = 2
    mesi['mar'] = 3
    mesi['apr'] = 4
    mesi['mag'] = 5
    mesi['giu'] = 6
    mesi['lug'] = 7
    mesi['ago'] = 8
    mesi['set'] = 9
    mesi['ott'] = 10
    mesi['nov'] = 11
    mesi['dic'] = 12
    return mesi[parola.lower()]

#22 GENNAIO 2021, ORE 20:45
def converti_data (data_string):
    primoSpazio = data_string.index(" ")
    giorno = int(data_string[0: primoSpazio])
    secondoSpazio = data_string.index(" ", primoSpazio+1)
    mese = parsaMese(data_string[primoSpazio+1:secondoSpazio])
    virgola = data_string.index(",")
    anno = int(data_string[secondoSpazio+1: virgola])
    #inizioOra = data_string.index(" ", start=virgola+2)+1
    #duePunti = data_string.index(":")
    #ora = int(data_string[inizioOra: duePunti])
    #minuto = int(data_string[duePunti:])
    #return datetime.datetime(anno, mese, giorno, ora, minuto)
    return datetime.datetime(anno, mese, giorno)

#venerdì, 12/feb/2021  - 20:45'
def converti_data_transkfermarkt (data_string):
    primaBarra= data_string.index("/")
    giorno=int(data_string[primaBarra-2: primaBarra])
    secondaBarra=primaBarra+4
    mese=parserMese(data_string[primaBarra+1: secondaBarra])
    anno=int(data_string[secondaBarra+1 : secondaBarra+5])
    #return datetime.datetime(anno, mese, giorno)
    trattino= data_string.index("-")
    ora= int(data_string[trattino+2: trattino+4])
    minuti= int(data_string[trattino+5:len(data_string)])
    return datetime.datetime(anno, mese, giorno, ora, minuti)


#FIXME: probabilmente sta funzione è solo da togliere
"""def scraper_giornata(i):

    num=str(i)
    driver = webdriver.Chrome()
    url="https://www.tuttomercatoweb.com/partite/serie_a/2019-2020/572/2394/"+num
    driver.get(url)

    #per essere sicuro che finestra cookie compaia e sia cliccabile
    driver.implicitly_wait(10)
    #l'xpath corrisponde al pulsante accetta nel popup
    time.sleep(1)
    accetta_cookie = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]'))
            ).click()
    #accetta_cookie= driver.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]').click()

    dispari="match.dispari"
    pari="match.pari"
    match= driver.find_elements_by_class_name(dispari)
    match1=driver.find_elements_by_class_name(pari)
    i=0
    match = match + match1
    #per evitare quei due cicli ridicoli ho messo in un unico array tutte le partite
    #for i in range(len(match1)):
    #    match.append(match1[i])

    listaPartite = []

    for evento in match:

        try: 
            #recupera le squadre dell'evento
            teams= evento.find_elements_by_class_name("squadraBig")
            #sqCasa = commons.trovaSquadra(teams[0].text)
            sqCasa = commons.trovaSquadra(teams[0].text, checkAggiunta=False)
            sqTrasferta = commons.trovaSquadra(teams[1].text, checkAggiunta=False)
            
            #lista dei goal da usare nel costruttore
            goals = []
            #recupera la lista dei goal della squadra in casa
            goalCasa=evento.find_element_by_class_name("right.small")
            marcatoriCasa= goalCasa.text.splitlines()
            goalCasa_list=list(marcatoriCasa)
            #itera su ogni goal in casa e lo inserisce in goals
            for i in range(len(goalCasa_list)):
                minuto = int(goalCasa_list[i][0:goalCasa_list[i].index("'")])
                goals.append(commons.Goal(sqCasa, minuto))

            #recupera la lista dei goal della squadra in trasferta
            goalTrasferta= evento.find_element_by_class_name("left.small")
            marcatoriTrasferta=goalTrasferta.text.splitlines()
            goalTrasferta=list(marcatoriTrasferta)

            for i in range(len(goalTrasferta)):
                minuto = int(goalTrasferta[i][0:goalTrasferta[i].index("'")])
                goals.append(commons.Goal(sqTrasferta, minuto))


            #da qui inizio le robe per ottenere la data, cliccando sulla partita ed aprendo la tab
            
            #qui creo un array contenente tutte le tab prima di aprire la nuova
            old_tabs=driver.window_handles
            #clicco sulla partita specifica
            evento.find_element_by_class_name("report").click()
            #elenco aggiornato di tab
            new_tabs=driver.window_handles
            for tab in new_tabs:
                #voglio andare alla tab nuova, che quindi non fa parte di old tabs
                if tab in old_tabs:
                    pass
                else:
                    new_tab=tab
            driver.switch_to.window(new_tab)

            #nella nuova tab ottengo quindi la classe specifica
            element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tcc-small.mleft"))
                )

            #la data viene salvata qui come stringa
            dataStringa=element.text
            #preso il testo chiudo la tab
            driver.close()
            #e torno a quella con l'elenco delle partite
            driver.switch_to.window(old_tabs[0])

            #da qui inizia la conversione della stringa in datetime
            data = converti_data(dataStringa)

            nuovaPartita = commons.Partita(sqCasa, sqTrasferta, goals, data)
            listaPartite.append(nuovaPartita)
            sqCasa.aggiungiPartita(nuovaPartita)
            sqTrasferta.aggiungiPartita(nuovaPartita)
        except Exception as e:
            time.sleep(1)


    driver.close()
    return listaPartite"""


#FIXME: probabilmente sta funzione è solo da togliere
"""def scraper_transfermarkt(i):

    num=str(i)
    driver = webdriver.Chrome()
    url="https://www.transfermarkt.it/serie-a/spieltag/wettbewerb/IT1/plus/?saison_id=2020&spieltag="+num
    driver.get(url)

    listaPartite = []
    match=[]
    
    for j in range(2,12):
        partita= driver.find_element_by_xpath("/html/body/div[2]/div[11]/div[1]/div["+ str(j)+ "]")
        match.append(partita)

    for evento in match:
        
        teams=  evento.find_elements_by_class_name(nomeSQ_classname)
        
        sqCasa = commons.trovaSquadra(teams[0].text, checkAggiunta=False)
        sqTrasferta = commons.trovaSquadra(teams[6].text, checkAggiunta=False)

        goals=[]
        
        goalCasa=evento.find_elements_by_class_name(minGoalCasa_classname)
        #rimuovo buona parte delle stringhe vuote
        for i in range(0,len(goalCasa)):
            #if (goalCasa[i].text != '' and ' ')
             if "'" in goalCasa[i].text:
                #goalCasa_str.append(goalCasa[i].text)
                marco=goalCasa[i].text
                if '+' in marco:
                    minuto= int (marco[0:marco.index("+")])
                else:
                    minuto = int(marco[0:marco.index("'")])
                goals.append(commons.Goal(sqCasa, minuto))



        goalTrasferta= evento.find_elements_by_class_name(minGoalTrasferta_classname)
        for i in range(0,len(goalTrasferta)):
            #if (goalCasa[i].text != '' and ' ')
             if "'" in goalTrasferta[i].text:
                #goalCasa_str.append(goalCasa[i].text)
                marco=goalTrasferta[i].text
                if '+' in marco:
                    minuto= int (marco[0:marco.index("+")])
                else:
                    minuto = int(marco[0:marco.index("'")])
                goals.append(commons.Goal(sqTrasferta, minuto))

        
        data_string=evento.find_element_by_class_name(data_classname).text
        data=converti_data_transkfermarkt (data_string)
        nuovaPartita = commons.Partita(sqCasa, sqTrasferta, goals, data)
        listaPartite.append(nuovaPartita)
        sqCasa.aggiungiPartita(nuovaPartita)
        sqTrasferta.aggiungiPartita(nuovaPartita)

    driver.close()
    return listaPartite"""
    

def ottieni_campionato_transfermarkt(competizione):

    ultima_giornata=ottieni_ultima_giocata(competizione)
    #print('ultima giornata per', competizione.campionato.value, '=', ultima_giornata)
    #per trovare partite in transfermarkt usiamo l'xpath, in campionati a 20 squadre cerchiamo in un range 2-12 nei div del sito
    #il parametro viene modificato solo per il campionati non a 20 squadre
    range_partite=12
    driver = webdriver.Chrome()
    if competizione.campionato==commons.NomeCampionato.SERIEA:
        #serie-a
        url="https://www.transfermarkt.it/serie-a/spieltag/wettbewerb/IT1/plus/?saison_id=2020&spieltag="

    elif competizione.campionato==commons.NomeCampionato.PREMIER:
        #premier-league
        url="https://www.transfermarkt.it/premier-league/spieltag/wettbewerb/GB1/plus/?saison_id=2020&spieltag="
    
    elif competizione.campionato==commons.NomeCampionato.BUNDESLIGA:
        #bundesliga
        url="https://www.transfermarkt.it/bundesliga/spieltag/wettbewerb/L1/plus/?saison_id=2020&spieltag="
        range_partite=11

    elif competizione.campionato==commons.NomeCampionato.LIGUE1:
        #ligue-1
        url="https://www.transfermarkt.it/ligue-1/spieltag/wettbewerb/FR1/plus/?saison_id=2020&spieltag="
    
    elif competizione.campionato==commons.NomeCampionato.LALIGA:
        #la-liga
        url="https://www.transfermarkt.it/la-liga/spieltag/wettbewerb/ES1/plus/?saison_id=2020&spieltag="

    listaGiornate=[]

    for i in range(1, ultima_giornata):
        num=str(i)
        driver.get(url+num)
        match=[]
        listaPartite=[]
        for i in range(2,range_partite): #TODO: che so sti cosi
            partita= driver.find_element_by_xpath("/html/body/div[2]/div[11]/div[1]/div["+ str(i)+ "]")
            match.append(partita)
        
        for evento in match:

            teams=  evento.find_elements_by_class_name(nomeSQ_classname)
        
            sqCasa = competizione.trovaSquadra(teams[0].text, checkAggiunta=False)
            sqTrasferta = competizione.trovaSquadra(teams[6].text, checkAggiunta=False)

            goals=[]
            
            goalCasa=evento.find_elements_by_class_name(minGoalCasa_classname)
            for i in range(0,len(goalCasa)):
                #if (goalCasa[i].text != '' and ' ')
                if "'" in goalCasa[i].text:
                    #goalCasa_str.append(goalCasa[i].text)
                    marco=goalCasa[i].text
                    if '+' in marco:
                        minuto= int (marco[0:marco.index("+")])
                    else:
                        minuto = int(marco[0:marco.index("'")])
                    goals.append(commons.Goal(sqCasa, minuto))



            goalTrasferta= evento.find_elements_by_class_name(minGoalTrasferta_classname)
            for i in range(0,len(goalTrasferta)):
                #if (goalCasa[i].text != '' and ' ')
                if "'" in goalTrasferta[i].text:
                    #goalCasa_str.append(goalCasa[i].text)
                    marco=goalTrasferta[i].text
                    if '+' in marco:
                        minuto= int (marco[0:marco.index("+")])
                    else:
                        minuto = int(marco[0:marco.index("'")])
                    goals.append(commons.Goal(sqTrasferta, minuto))

            
            data_string=evento.find_element_by_class_name(data_classname).text
            data=converti_data_transkfermarkt (data_string)
            nuovaPartita = commons.Partita(sqCasa, sqTrasferta, goals, data)
            listaPartite.append(nuovaPartita)
            sqCasa.aggiungiPartita(nuovaPartita)
            sqTrasferta.aggiungiPartita(nuovaPartita)

        
        #listaGiornate.append(listaPartite)
        listaGiornate += listaPartite
    
    driver.close()
    return listaGiornate


def trovaPartite(competizione):
    try:
        listaGiornate=[]
        listaGiornate= ottieni_campionato_transfermarkt(competizione)
        return listaGiornate
    except: 
        print('Impossibile scaricare il campionato', competizione.campionato.value ,'. F')

def scaricaCampionati(campionati):
    attese = []
    for campionato in campionati.values():
        t = threading.Thread(target=campionato.downloadPartite)
        attese.append(t)
        t.start()
    for i in range(0, len(attese)):
        t = attese[i]
        t.join()




def parsaOra(data):
    ora= int(data[0:2])
    minuti= int(data[3:5])
    adesso = datetime.datetime.now()
    return datetime.datetime(adesso.year, adesso.month, adesso.day, ora, minuti)

def partite_di_oggi(competizione):
    """
        Ritorna la lista delle partite che giocano nella giornata attuale nel campionato competizione
        in caso termini correttamente, None altrimenti
    """
    try:
        print('Download partite di', competizione.campionato.value)
        oggi=datetime.date.today()
        driver = webdriver.Chrome()
        url = ''
        range_partite=12

        if competizione.campionato==commons.NomeCampionato.SERIEA:
            #serie-a
            url="https://www.transfermarkt.it/serie-a/spieltag/wettbewerb/IT1/plus/"

        elif competizione.campionato==commons.NomeCampionato.PREMIER:
            #premier-league
            #url="https://www.transfermarkt.it/premier-league/spieltag/wettbewerb/GB1/plus/"
            url="https://www.transfermarkt.it/premier-league/spieltag/wettbewerb/GB1/plus/?saison_id=2020&spieltag=33"
        
        elif competizione.campionato==commons.NomeCampionato.BUNDESLIGA:
            #bundesliga
            url="https://www.transfermarkt.it/bundesliga/spieltag/wettbewerb/L1/plus/"
            range_partite=11

        elif competizione.campionato==commons.NomeCampionato.LIGUE1:
            #ligue-1
            url="https://www.transfermarkt.it/ligue-1/spieltag/wettbewerb/FR1/plus/"
        
        elif competizione.campionato==commons.NomeCampionato.LALIGA:
            #la-liga
            url="https://www.transfermarkt.it/la-liga/spieltag/wettbewerb/ES1/plus/"
            #url="https://www.transfermarkt.it/la-liga/spieltag/wettbewerb/ES1/plus/?saison_id=2020&spieltag=33"


        listaOggi=[]

        driver.get(url)        
        for i in range(2,range_partite): #TODO: che so sti cosi
            partita= driver.find_element_by_xpath("/html/body/div[2]/div[11]/div[1]/div["+ str(i)+ "]")

            data_string=partita.find_element_by_class_name(data_classname).text
            data=converti_data_transkfermarkt (data_string)
            
            if data.month == oggi.month:
                #guardo il giorno 
                if data.day == oggi.day:
                    #kawabonga
                    #controlla il resto della partita e aggiungila alla listaOggi
                    teams=  partita.find_elements_by_class_name(nomeSQ_classname)
            
                    sqCasa = competizione.trovaSquadra(teams[0].text, checkAggiunta=False)
                    sqTrasferta = competizione.trovaSquadra(teams[6].text, checkAggiunta=False)
                    nuovaPartita = commons.PartitaFutura(sqCasa, sqTrasferta, data)
                    listaOggi.append(nuovaPartita)
                    sqCasa.aggiungiPartita(nuovaPartita)
                    sqTrasferta.aggiungiPartita(nuovaPartita)
            
        driver.close()
        return listaOggi
    except :
        print('Impossibile scaricare le partite di oggi. F')
        return None



def ottieni_ultima_giocata(competizione):

    driver = webdriver.Chrome()
    if competizione.getTipo()==commons.NomeCampionato.SERIEA:
        #serie-a
        url="https://www.transfermarkt.it/serie-a/spieltag/wettbewerb/IT1/plus/"

    elif competizione.getTipo()==commons.NomeCampionato.PREMIER:
        #premier-league
        url="https://www.transfermarkt.it/premier-league/spieltag/wettbewerb/GB1/plus/"
    
    elif competizione.getTipo()==commons.NomeCampionato.BUNDESLIGA:
        #bundesliga
        url="https://www.transfermarkt.it/bundesliga/spieltag/wettbewerb/L1/plus/"

    elif competizione.getTipo()==commons.NomeCampionato.LIGUE1:
        #ligue-1
        url="https://www.transfermarkt.it/ligue-1/spieltag/wettbewerb/FR1/plus/"
    
    elif competizione.getTipo()==commons.NomeCampionato.LALIGA:
        #la-liga
        url="https://www.transfermarkt.it/la-liga/spieltag/wettbewerb/ES1/plus/"

    driver.get(url)
    #dovrebbe aprire la pagina relativa all'ultima giocata, ora guardo il numero
    giornata_corrente=driver.find_element_by_class_name("table-header").text
    giornata=int(giornata_corrente[3:5])
    #giornata-=1
    driver.close()
    return giornata


def cerca_partite_oggi ():
    """
        DEPRECATA: al momento si usa partite_di_oggi(competizione)
    """
    listaOggi=[]
    listaOggi+= partite_di_oggi(commons.NomeCampionato.BUNDESLIGA)
    listaOggi+= partite_di_oggi(commons.NomeCampionato.SERIEA)
    listaOggi+= partite_di_oggi(commons.NomeCampionato.LIGUE1)
    listaOggi+= partite_di_oggi(commons.NomeCampionato.LALIGA)
    listaOggi+= partite_di_oggi(commons.NomeCampionato.PREMIER)

    return listaOggi


