import datetime
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
import deprecation

#import ricerca_statistica


squadre = { }

partite = [ ]
partiteDaSalvare = [ ]

testers = { }

aGlobale = 0.0
#il numero di prove da fare (di fatto se ne fa una in meno per escludere a=1)
nProve = 100
#la soglia di probabilità oltre cui la partita è proposta
SOGLIA_SO = 0.8



def Pn1SO(Pn, Vn, a):
    return (1-a)*Pn + a*Vn


def cicloTest(partite, a, stampa=False):
    """
        Per a fissato esegue il ciclo di prove per tutte le partite passate in input.
        Ritorna la percentuale di guadagni ottenuti e il numero di errori fatti (sulle previsioni)
    """
    #il numero di errori fatti sulle proposte
    errori = 0
    #l'array degli errori relativi
    errRel = np.zeros(len(partite))
    #l'indice per errRel (viene aggiornato solo quando la probabilità è definita)
    prevFatte = 0
    #il numero di proposte fatte (quando viene consigliato di scommettere)
    propFatte = 0
    
    negative = 0
    positive = 0

    if stampa: print('inizio test con a =', a)
    for i in range(len(partite)):
        #recupera le squadre e le probabilità della partita
        #sqCasa = partite[i].getSquadraCasa()
        #sqTrasferta = partite[i].getSquadraTrasferta()
        sqCasa = partite[i].sqCasa
        sqTrasferta = partite[i].sqTrasferta
        pCasa = sqCasa.probPer(Strategia.SUPEROVER, partite[i])
        pTrasferta = sqTrasferta.probPer(Strategia.SUPEROVER, partite[i])
        #se la probabilità è definita si valuta una proposta
        #e ne si verifica la correttezza
        if pCasa != None and pTrasferta != None:
            #se la probabilità è sufficiente fai la proposta altrimenti no
            if (pCasa + pTrasferta)/2 > SOGLIA_SO: proposta = True
            else: proposta = False
            prevFatte += 1
            if proposta != SuperOverTester.successo(partite[i]):
                errori += 1
                #se era stata proposta la scommessa si son persi dei soldi
                if proposta:
                    negative += 1
                    propFatte += 1
            else:
                #se era stata proposta la scommessa si son guadagnati dei soldi
                if proposta:
                    positive += 1
                    propFatte += 1

            errRel[i] = errori/prevFatte

    #finito il ciclo si misurano le prestazioni e si plotta l'errore
    guadagni = 15*positive
    perdite = 55*negative
    if stampa:
        print('errori fatti:', errori, 'previsioni azzeccate:', prevFatte-errori)
        print('indice di errore all\'ultima partita:', errori/prevFatte)
        print('proposte corrette:', positive, 'scorrette:', negative)
        print('indice proposte in perdita:', negative/propFatte, 'indice proposte in guadagno', positive/propFatte)
        print('il profitto sarebbe stato del ', guadagni-perdite, '%', sep='')
        #mostraPlotErr(errRel, 'globale_'+str(aGlobale))
        print()

    return errori, guadagni-perdite


def mostraPlotErr(err, title):
    """
        Plotta e mostra il grafico dell'errore relativo err per ogni passo eseguito,
        titolando il grafico title
    """
    plt.plot(err)
    plt.title(title)
    plt.show()


def chiudi():
    #import datacalcio
    #datacalcio.istanza_a_db(partite)
    pass





class Campionato:
    def __init__(self, nome):
        if not isinstance(nome, NomeCampionato):
            raise TypeError('Errore nell\'istanziare un campionato, nome dev\'essere di tipo NomeCampionato, non '+str(type(nome)))
        self.__nome = nome
        self.__a = 0.0
        self.__squadre = {}
        self.__partite = []

    @property
    def campionato(self):
        """
            Il tipo di campionato di quest'istanza [NomeCampionato]
        """
        return self.__nome


    def getNome(self):
        return self.__nome.value

    def getPartite(self):
        return self.__partite

    def getSquadre(self):
        return self.__squadre.values()

    def getTipo(self):
        return self.__nome

    def aggiungiPartita(self, partita):
        if not isinstance(partita, Partita):
            raise TypeError('Errore nell\'aggiunta di una partita ad un campionato, partita dev\'essere di tipo Partita, non '+str(type(partita)))
        self.__partite.append(partita)
        self.aggiungiSquadra(partita.getSquadraCasa())
        self.aggiungiSquadra(partita.getSquadraTrasferta())
        #print('aggiunta la partita ', end='')
        #partita.stampa()


    def aggiungiSquadra(self, squadra):
        if not isinstance(squadra, Squadra):
            raise TypeError('Errore nell\'aggiunta di una squadra ad un campionato, squadra dev\'essere di tipo Squadra, non '+str(type(squadra)))
        try:
            self.__squadre[squadra.getNome()]
        except KeyError:
            self.__squadre[squadra.getNome()] = squadra


    def trovaSquadra(self, nomeSquadra, checkAggiunta=True):
        squadra = None
        yes = 'y'
        no = 'n'
        try:
            squadra = self.__squadre[nomeSquadra]
        except KeyError:
            if checkAggiunta:
                print('Squadra', nomeSquadra, 'non trovata. La si vuole aggiungere ora? (y/n) ')
                rep = input()
                #finchè la risposta non è chiara continua a richiederla
                while rep != yes and rep != no:
                    print('Non ho capito la risposta', end='')
                    rep = input()
                #se la risposta è no la funzione termina
                if rep == no: return None
                #ramo nuova squadra inserita
                squadra = Squadra(nomeSquadra)
                self.__squadre[nomeSquadra] = squadra
                squadre[nomeSquadra] = squadra
            else:
                squadra = Squadra(nomeSquadra)
                self.__squadre[nomeSquadra] = squadra
                squadre[nomeSquadra] = squadra
                print('Aggiunta la squadra', nomeSquadra)

        return squadra


    def probReset(self):
        """
            Resetta le probabilità calcolate per tutte le squadre del campionato
        """
        for squadra in self.__squadre.values():
            squadra.pSOReset()


    def calcolaA(self, stampa=False):
        """
            Esegue nProve cicli testando diversi valori di aGlobale per trovare
            quale valore da i risultati migliori
        """
        if stampa: print('inizio test per a globale in super over')
        self.__a = 0.0
        #il valore di cui va incrementato a ad ogni ciclo 
        inc = 1 / nProve
        #variabili per tenere traccia del miglior risultato
        aMigliore = 0.0
        erroriMigliore = len(self.__partite)
        guadagniMigliore = float('-inf')
        
        for conta in range(nProve-1):
            self.__a += inc
            self.setASquadre()
            errori, guadagni = cicloTest(self.__partite, self.__a, False)
            if guadagni > guadagniMigliore:
                aMigliore = self.__a
                erroriMigliore = errori
                guadagniMigliore = guadagni
            self.probReset()

        if stampa:
            print('fine test a globale. i risultati migliori li ha dati', aMigliore, 'con', erroriMigliore, 'errori ', end='')
            print('e un guadagno di ', guadagniMigliore,'%', sep='')
        self.__a = aMigliore
        self.setASquadre()


    def setASquadre(self):
        for squadra in self.__squadre.values():
            squadra.setA(self.__a)
        

    def downloadPartite(self):
        import scraper
        print(self.__nome.value, 'inizia il download delle partite')
        self.__partite = scraper.trovaPartite(self)
        self.calcolaA(stampa=False)
        print(self.__nome.value, 'ha finito il download delle partite')
        #for sq in self.__squadre.values():
        #    partite = sq.partite
        #    for i in range(len(partite)):
        #        print(type(partite[i]))
        #    print()





class NomeCampionato(Enum):
    SERIEA = 'Serie A'
    PREMIER = 'Premier League'
    BUNDESLIGA = 'Bundesliga'
    LIGUE1 = 'Ligue 1'
    LALIGA = 'La Liga'




class Strategia(Enum):
    SUPEROVER = 0





class Partita:
    def __init__(self, squadraCasa, squadraTrasferta, goals, data):
        if not isinstance(squadraCasa, Squadra):
            raise TypeError('Errore nell\'istanziare una partita, squadraCasa dev\'essere di tipo Squadra, non '+str(type(squadraCasa)))
        #squadra che gioca in casa [Squadra]
        self.__squadraCasa = squadraCasa
        if not isinstance(squadraTrasferta, Squadra):
            raise TypeError('Errore nell\'istanziare una partita, squadraTrasferta dev\'essere di tipo Squadra, non '+str(type(squadraTrasferta)))
        #squadra che gioca in trasferta [Squadra]
        self.__squadraTrasferta = squadraTrasferta
        if not isinstance(data, datetime.datetime):
            raise TypeError('Errore nell\'istanziare una partita, data dev\'essere di tipo datetime, non '+str(type(data)))
        #la data in cui la partita è stata giocata [datetime]
        self.__data = data
        #TODO: trova il modo di controllare il tipo di una lista di goal
        #elenco dei goal della partita [Goals list]
        self.__goals = goals
        self.__goals.sort(key=Goal.compare)
        #il nome della partita, usato come chiave [String]
        self.__nome = str(data.year)+str(data.month)+str(data.day) + squadraCasa.getNome() + '-' + squadraTrasferta.getNome() 

    @property
    def sqCasa(self):
        """
            La squadra che gioca in casa [Squadra]
        """
        return self.__squadraCasa

    @property
    def sqTrasferta(self):
        """
            La squadra che gioca in trasferta [Squadra]
        """
        return self.__squadraTrasferta

    @property
    def data(self):
        """
            La data in cui la partita è giocata [datetime]
        """
        return self.__data

    @property
    def goals(self):
        """
            La lista dei goals della partita [list di Goals]
        """
        return self.__goals


    @deprecation.deprecated(details='non usare più i getter, usa invece le proprietà')
    def getSquadraCasa(self):
        return self.__squadraCasa

    @deprecation.deprecated(details='non usare più i getter, usa invece le proprietà')
    def getSquadraTrasferta(self):
        return self.__squadraTrasferta
    
    @deprecation.deprecated(details='non usare più i getter, usa invece le proprietà')
    def getGoals(self):
        return self.__goals

    @deprecation.deprecated(details='non usare più i getter, usa invece le proprietà')
    def getNome(self):
        return self.__nome

    @deprecation.deprecated(details='non usare più i getter, usa invece le proprietà')
    def getData(self):
        return self.__data

    """def salva(self):
        record = open(PARTITE_PATH+self.__nome+'.txt', 'w')
        #record.write(self.__nome + '\n')
        record.write(self.__squadraCasa.getNome()+'\n')
        record.write(self.__squadraTrasferta.getNome()+'\n')
        record.write(self.__data.strftime('%Y/%m/%d %H:%M') + '\n')
        for goal in self.__goals:
            record.write(goal.toString()+'\n')
        record.close()

    @staticmethod
    def crea(file):
        #il -1 vuol dire 1 posizione partendo dalla fine, cioè togli l'ultimo carattere
        nomeCasa = file.readline()[:-1]
        squadraCasa = trovaSquadra(nomeCasa)
        nomeTrasferta = file.readline()[:-1]
        squadraTrasferta = trovaSquadra(nomeTrasferta)
        data = parseData(file.readline()[:-1])
        goals = []
        for line in file.readlines():
            g = Goal.unString(line)
            goals.append(g)
        p = Partita(squadraCasa, squadraTrasferta, goals, data)
        squadraCasa.aggiungiPartita(p)
        squadraTrasferta.aggiungiPartita(p)
        return p"""

    @staticmethod
    def compare(partita):
        d = partita.__data        
        return int(d.year*365.25 + d.month*30 + d.day)

    def stampa(self):
        print(self.__squadraCasa.getNome(), '-', self.__squadraTrasferta.getNome(), 'del', self.__data, 'con', len(self.__goals), 'goals')





class PartitaFutura:
    def __init__(self, squadraCasa, squadraTrasferta, dataOra, link=''):
        PartitaFutura._checkType(squadraCasa, squadraTrasferta, dataOra, link)
        self.__sqCasa = squadraCasa
        self.__sqTrasferta = squadraTrasferta
        self.__dataOra = dataOra
        self.__link = link
        self.__ingresso = False
        self.__strategia = None
        self.__minuto = 0
        self.__nGoals = 0
        self.__tester = None

    @property
    def sqCasa(self):
        """
            La squadra che giocherà in casa [Squadra]
        """
        return self.__sqCasa

    @property
    def sqTrasferta(self):
        """
            La squadra che giocherà in trasferta [Squadra]
        """
        return self.__sqTrasferta

    @property
    def ingressoFatto(self):
        """
            True se è stato fatto l'ingresso nel mercato della partita (con il metodo confermaIngresso),
            False altrimenti [bool]
        """
        return self.__ingresso

    @property
    def strategia(self):
        """
            La strategia utilizzata per questa partita
        """
        return self.__strategia

    @property
    def tester(self):
        """
            Il tester corrispondente alla strategia scelta per questa partita
        """
        return self.__tester

    @property
    def data(self):
        """
            La data di gioco della partita, comprensiva di orario [datetime]
        """
        return self.__dataOra

    @property
    def nome(self):
        """
            L'intestazione della partita nel formato "nome casa - nome trasferta" [str]
        """
        return self.__sqCasa.nome + ' - ' + self.__sqTrasferta.nome

    @property
    def orario(self):
        """
            L'orario della partita in formato stringa [str]
        """
        retVal = str(self.__dataOra.hour) + ':' + str(self.__dataOra.minute)
        if self.__dataOra.minute == 0: retVal += '0'
        return retVal



    def getData(self):
        return self.__dataOra

    def getMinuto(self):
        return self.__minuto

    def getNome(self):
        return self.__sqCasa.getNome() + '-' + self.__sqTrasferta.getNome() 

    def getNGoals(self):
        return self.__nGoals

    def getOra(self):
        return self.__dataOra.hour + ':' + self.__dataOra.minute

    def getSquadraCasa(self):
        return self.__sqCasa

    def getSquadraTrasferta(self):
        return self.__sqTrasferta

    def getSrtategia(self):
        return self.__strategia

    def getTester(self):
        return self.__tester


    def setMinuto(self, minuto):
        self.__minuto = minuto

    def setNGoals(self, numero):
        self.__nGoals = numero

    def setStrategia(self, strategia):
        if not isinstance(strategia, Strategia):
            raise TypeError('Errore nel settare la strategia di una PartitaFutura, strategia dev\'essere di tipo Strategia, non '+str(type(strategia)))
        self.__strategia = strategia
        self.__tester = testers[strategia]

    #def setTester(self, tester):
    #    self.__tester = testers[tester]


    def confermaIngresso(self):
        self.__ingresso = True

    
    def entrato(self):
        return self.__ingresso
        

    @staticmethod
    def _checkType(squadraCasa, squadraTrasferta, ora, link):
        if not isinstance(squadraCasa, Squadra):
            raise TypeError('Errore nell\'istanziare una partita futura, squadraCasa dev\'essere di tipo Squadra, non '+str(type(squadraCasa)))
        if not isinstance(squadraTrasferta, Squadra):
            raise TypeError('Errore nell\'istanziare una partita futura, squadraTrasferta dev\'essere di tipo Squadra, non '+str(type(squadraTrasferta)))
        if not isinstance(ora, datetime.datetime):
            raise TypeError('Errore nell\'istanziare una partita futura, ora dev\'essere di tipo datetime, non '+str(type(ora)))
        if not isinstance(link, str):
            raise TypeError('Errore nell\'istanziare una partita futura, link dev\'essere di tipo str, non '+str(type(link)))

    




class Goal:
    def __init__(self, squadra, minuto):
        if not isinstance(squadra, Squadra):
            raise TypeError('Errore nell\'istanziare un goal, squadra dev\'essere di tipo Squadra, non '+str(type(squadra)))
        #la squadra che ha segnato il goal [Squadra]
        self.__squadraSegnante = squadra
        if not isinstance(minuto, int):
            raise TypeError('Errore nell\'istanziare un goal, minuto dev\'essere di tipo int, non '+str(type(minuto)))
        #il minutaggio del goal [int]
        self.__minuto = minuto

    @property
    def minuto(self):
        """
            Il minuto in cui è stato segnato il goal [int]
        """
        return self.__minuto

    @property
    def sqSegnante(self):
        """
            La squadra che ha segnato il goal [Squadra]
        """
        return self.__squadraSegnante
    

    def getMinuto(self):
        return self.__minuto

    def getSquadraSegnante(self):
        return self.__squadraSegnante

    def compare(self):
        return self.__minuto

    def toString(self):
        return self.__squadraSegnante.getNome() +'-'+ str(self.__minuto)

    @staticmethod
    def unString(stringa):
        i = 0
        while i < len(stringa) and stringa[i] != '-':
            i += 1
        if i == len(stringa): return None
        squadraSegnante = squadre[stringa[:i]]
        return Goal(squadraSegnante, int(stringa[i+1:]))

    def stampa(self):
        print('goal di', self.__squadraSegnante, 'al', self.__minuto, 'esimo')





class Squadra:
    def __init__(self, nome):
        if not isinstance(nome, str):
            raise TypeError('Errore nell\'istanziare una squadra, nome dev\'essere di tipo str, non '+str(type(nome)))
        #nome della squadra [str]
        self.__nome = nome
        #lista delle partite giocate [Partita list]
        self.__partite = []
        
        #la probabilità per il super over quando gioca in casa [float]
        self.__pSOCasa = None
        #l'indice della prima partita da valutare per quelle giocate in casa [int]
        self.__valutaSOCasa = 0
        #la probabilità per il super over quando gioca in trasferta [float]
        self.__pSOTrasferta = None
        #l'indice della prima partita da valutare per quelle giocate in trasferta [int]
        self.__valutaSOTrasferta = 0
        #il valore della costante a della successione assocciato alla squadra [float]
        self.__aPrivato = None

    @property
    def nome(self):
        """
            Il nome della squadra [str]
        """
        return self.__nome

    @property
    def partite(self):
        """
            La lista delle partite giocate dalla squadra [list di Partita]
        """
        return self.__partite


    def getA(self):
        if self.__aPrivato == None: return aGlobale
        else: return self.__aPrivato

    def getNome(self):
        return self.__nome

    def getPartite(self):
        return self.__partite


    def aggiungiPartita(self, partita):
        #self.__partite.aggiungi(partita)
        self.__partite.append(partita)


    def equals(self, altraSquadra):
        """
            Valuta se questa squadra sia uguale ad altraSquadra.
            Ritorna True in caso affermativo, False altrimenti
        """
        if not isinstance(altraSquadra, Squadra): return False
        return self.__nome == altraSquadra.__nome


    def probPer(self, strategia: Strategia, partita: Partita):
        """
            Calcola la probabilità per la partita partita secondo la strategia
            strategia
        """
        #TODO: aggiungere il controllo sulle squadre in partita 
        if strategia == Strategia.SUPEROVER:
            data = partita.getData()
            if partita.getSquadraCasa().getNome() == self.__nome:
                self.__pSOCasaFino(data)
                ret = self.__pSOCasa
            else:
                self.__pSOTrasfertaFino(data)
                ret = self.__pSOTrasferta
            return ret


    def __pSOCasaFino(self, data: datetime.datetime, ancheTrasferta=False):
        #nel caso P sia indeterminata bisogna assegnarle un valore iniziale
        if self.__pSOCasa == None:
            #il valore iniziale è l'indice di valutazione della prima partita in casa
            definito = False
            while self.__valutaSOCasa < len(self.__partite) and not definito:
                #se in questa partita gioca in casa, definiamo P
                if self.__partite[self.__valutaSOCasa].getSquadraCasa().equals(self):
                    self.__pSOCasa = SuperOverTester.valuta(self.__partite[self.__valutaSOCasa])
                    definito = True
                self.__valutaSOCasa += 1

        a = self.getA()
        #scorro finché ci sono partite salvate con data precedente a quella richiesta
        while self.__valutaSOCasa < len(self.__partite) and data > self.__partite[self.__valutaSOCasa].getData():
            #se la partita è in casa la valuto
            if self.__partite[self.__valutaSOCasa].getSquadraCasa().equals(self):
                Vn = SuperOverTester.valuta(self.__partite[self.__valutaSOCasa])
                self.__pSOCasa = Pn1SO(self.__pSOCasa, Vn, a)
            #TODO: se è in trasferta la valuto solo se specificato
            elif ancheTrasferta:
                pass
            self.__valutaSOCasa += 1


    def __pSOTrasfertaFino(self, data: datetime.datetime, ancheCasa=False):
        #nel caso P sia indeterminata bisogna assegnarle un valore iniziale
        if self.__pSOTrasferta == None:
            #il valore iniziale è l'indice di valutazione della prima partita in trasferta
            definito = False
            while self.__valutaSOTrasferta < len(self.__partite) and not definito:
                if self.__partite[self.__valutaSOTrasferta].getSquadraTrasferta().equals(self):
                    self.__pSOTrasferta = SuperOverTester.valuta(self.__partite[self.__valutaSOTrasferta])
                    definito = True
                self.__valutaSOTrasferta += 1

        a = self.getA()
        #scorro finché ci sono partite salvate con data precedente a quella richiesta
        while ( self.__valutaSOTrasferta < len(self.__partite) ) and (data > self.__partite[self.__valutaSOTrasferta].getData()):
            #se la partita è in trasferta la valuto
            if self.__partite[self.__valutaSOTrasferta]:
                Vn = SuperOverTester.valuta(self.__partite[self.__valutaSOTrasferta])
                self.__pSOTrasferta = Pn1SO(self.__pSOTrasferta, Vn, a)
            #TODO: se è in trasferta la valuto solo se specificato
            elif ancheCasa:
                pass
            self.__valutaSOTrasferta += 1


    def pSOReset(self):
        self.__pSOCasa = None
        self.__valutaSOCasa = 0
        self.__pSOTrasferta = None
        self.__valutaSOTrasferta = 0


    def setA(self, a):
        self.__aPrivato = a


    def testSOPrivato(self):
        """
            Esegue nProve cicli per diversi valori di a associato all'istanza
            per trovare quale valore da i risultati migliori
        """
        print('inizio test per la squadra', self.__nome)
        #variabili per l'iterazione
        inc = 1 / nProve
        self.__aPrivato = 0.0
        #variabili di controllo sulle prestazioni
        aMigliore = 0.0
        erroriMigliore = len(self.__partite)
        guadagniMigliore = 0
        perditeMigliore = 0

        for conta in range(nProve-1):
            self.__aPrivato += inc
            """print('test con a privato =', self.__aPrivato)
            #fissato aPrivat, si scorrono tutte le partite
            for i in range(len(partite)):
                sqCasa = partite[i].getSquadraCasa()
                sqTrasferta = partite[i].getSquadraTrasferta()
                pCasa = sqCasa.probPer(Strategia.SUPEROVER, partite[i])
                pTrasferta = sqTrasferta.probPer(Strategia.SUPEROVER, partite[i])
                #se la probabilità è definita si valuta una proposta
                #e ne si verifica la correttezza
                if pCasa != None and pTrasferta != None:
                    if (pCasa + pTrasferta)/2 > SOGLIA_SO: proposta = True
                    else: proposta = False
                    if proposta != SuperOverTester.successo(partite[i]):
                        errori += 1
                    #i+1 è il numero di partite analizzate, l'errore relativo è calcolato
                    #come numero errori fratto numero valutazioni
                    errRel[prevFatte] = errori/(i+1)
                    prevFatte += 1

            errRel = errRel[:prevFatte]
            prevFatte = errRel.size()
            guadagni = 15*(prevFatte-errori)
            perdite = 55*errori
            print('\terrori fatti:', errori, 'previsioni azzeccate:', prevFatte-errori)
            print('\til profitto sarebbe stato del', guadagni-perdite, '%', sep='')
            mostraPlotErr(errRel, 'privato_'+self.__nome+'_'+str(aGlobale))"""
            errori, prevFatte = cicloTest(self.__partite, self.__aPrivato)
            if errori < erroriMigliore:
                aMigliore = self.__aPrivato
                erroriMigliore = errori
                guadagniMigliore = 15 * (prevFatte-errori)
                perditeMigliore = 55 * errori

        print('fine test a privato per', self.__nome, '. i risultati migliori li ha dati', aMigliore, 'con', erroriMigliore, 'errori ', end='')
        print('e un guadagno di ', guadagniMigliore-perditeMigliore,'%', sep='')
        self.__aPrivato = aMigliore


    def stampa(self):
        print(self.__nome)




class SuperOverTester:
    LIMITE_PRIMO_GOAL = 70
    SOGLIA_SO = 0.8
    MINUTO_INGRESSO = 15

    def __init__(self):
        pass

    def valutaIngresso(self, partita):
        return partita.getMinuto() > SuperOverTester.MINUTO_INGRESSO

    def valutaUscita(self, partita):
        return partita.getNGoals() > 1 or partita.getMinuto() > SuperOverTester.LIMITE_PRIMO_GOAL

    def probPer(self, partita):
        """
            Ritorna la probabilità che un investimento in questa partita, con strategia
            SuperOver vada a buon fine [float]
        """
        return round(SuperOverTester.prob(partita), 2)

    @staticmethod
    def valuta(partita: Partita):
        voto = 1
        goals = partita.getGoals()
        if len(goals) == 0: voto = 0
        elif goals[0].getMinuto() > SuperOverTester.LIMITE_PRIMO_GOAL:
            voto *= 0.5
        if len(goals) < 2: voto *= 0.1

        return voto

    @staticmethod
    def successo(partita: Partita):
        goals = partita.getGoals()
        minutoMin = 130
        for i in range(len(goals)):
            if goals[i].getMinuto() < minutoMin:
                minutoMin = goals[i].getMinuto()
        return (len(goals) >= 2) and (minutoMin < SuperOverTester.LIMITE_PRIMO_GOAL)


    @staticmethod
    def prob(partita):
        """
            Ritorna la probabilità che un investimento in questa partita, con strategia
            SuperOver vada a buon fine [float]
        """
        sqCasa = partita.sqCasa
        sqTrasferta = partita.sqTrasferta
        pCasa = sqCasa.probPer(Strategia.SUPEROVER, partita)
        pTrasferta = sqTrasferta.probPer(Strategia.SUPEROVER, partita)
        if pCasa != None and pTrasferta != None: return (pCasa + pTrasferta) / 2
        else: return 0


    @staticmethod
    def valutaProposta(partita):
        """
            Ritorna True se è suggerito investinre in questa partita con strategia SuperOver,
            False altrimenti
        """
        return SuperOverTester.prob(partita) > SuperOverTester.SOGLIA_SO




testers[Strategia.SUPEROVER] = SuperOverTester()

