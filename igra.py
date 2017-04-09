#################
## LOGIKA IGRE ##
#################

##from norm_logika import *
##from pop_logika import *
##from five_logika import *
import random

IGRALEC_R = 1 # Igralec, ki ima rdeče krogce
IGRALEC_Y = 2 # Igralec, ki ima rumene krogce
PRAZNO = 0 # Prazno polje
NEODLOCENO = "neodločeno" # Igra se je končala z neodločenim izzidom
NI_KONEC = "ni konec" # Igre še ni konec
NEVELJAVNO = 99 # Ta stolpec ni veljaven

def nasprotnik(igralec):
    """Vrni nasprotnika od igralca."""
    if igralec == IGRALEC_R:
        return IGRALEC_Y
    elif igralec == IGRALEC_Y:
        return IGRALEC_R
    else:
        # Do sem ne smemo priti, če pridemo, je napaka v programu.
        # V ta namen ima Python ukaz assert, s katerim lahko preverimo,
        # ali dani pogoj velja. V našem primeru, ko vemo, da do sem
        # sploh ne bi smeli priti, napišemo za pogoj False, tako da
        # bo program crknil, če bo prišel do assert.
        # To je zelo uporabno za odpravljanje napak.
        # Assert uporabimo takrat, ko bi program lahko deloval naprej kljub
        # napaki (če bo itak takoj crknil, potem assert ni potreben).
        assert False, "neveljaven nasprotnik"

class Igra():
    # Tabela vseh možnih zmagovalnih kombinacij 4 v vrsto
    stirke = []
    for i in range(7):
        for j in range(3): # Navpične
            stirke.append([(i,j), (i,j+1), (i,j+2), (i,j+3)])
        if i < 4: # 4 = 7 - 3, 3 mesta še naprej za 4ko
            for j in range(6): # 6 vrstic
                stirke.append([(i,j), (i+1,j), (i+2, j), (i+3, j)]) # Vodoravne
                if j < 3: # Diagonalne desno gor
                    stirke.append([(i,j), (i+1,j+1), (i+2,j+2), (i+3,j+3)])
                if j > 2: # Diagonalne desno dol
                    stirke.append([(i,j), (i+1,j-1), (i+2,j-2), (i+3,j-3)])

    
    def __init__(self, tip=None):
        # Ustvarimo seznam trenutne pozicije
        self.polozaj = [[PRAZNO]*6 for i in range(7)]

        # Prvi na potezi je naključni igralec.
        x=random.choice([1,2])
        if x%2==0:
            self.na_potezi = IGRALEC_R
        if x%2==1:
            self.na_potezi = IGRALEC_Y

        # Shranjujmo si zgodovino, da lahko uporabimo 'undo'
        self.zgodovina = []

        # Števec, ki nam pove, katero potezo si ogledujemo
        # Z njim lahko gremo v 'preteklost'
        self.stevec = 0

        # To je začasna rešitev, dokler ne najdem boljše
        # Je zadnje stanje, če želiš `Redo`-jati do konca
        self.zadnja = ([[PRAZNO]*6 for i in range(7)], self.na_potezi)

    def kopija(self):
        '''Vrni kopijo te igre, brez zgodovine.'''
        # Potrebujemo, da se ne rišejo poteze, ko računalnik razmišlja
        k = Igra()
        k.polozaj = [self.polozaj[i][:] for i in range(7)]
        k.na_potezi = self.na_potezi
        return k

    def povleci_potezo(self, p):
        '''Povleci potezo p, če je veljavna, sicer ne naredi nič.
            Veljavna igra -> vrne stanje_igre() po potezi, sicer None.'''
        #(i,j) = p # Igrana poteza
        poteze = self.veljavne_poteze()
        je_popout = False

        # Preverimo, če je poteza veljavna
        if p < 0:
            k = -(p+1) # Kateri stolpec to dejansko je
            if p in poteze:
                # Imamo popout potezo
                if len(self.zgodovina) > self.stevec:
                    self.zgodovina = self.zgodovina[:self.stevec]
                self.shrani_polozaj()
                # Odstranimo spodnji žeton
                del self.polozaj[k][0]
                self.polozaj[k].append(0)
                j = 0
                je_popout = True
            elif -p in poteze:
                if len(self.zgodovina) > self.stevec:
                    self.zgodovina = self.zgodovina[:self.stevec]
                self.shrani_polozaj()
                j = self.vrstica(k)
                self.polozaj[k][j] = self.na_potezi
            else:
                # Poteza ni veljavna
                return None
        elif p in poteze:
            # Poteza je veljavna
            if len(self.zgodovina) > self.stevec:
                self.zgodovina = self.zgodovina[:self.stevec]
            self.shrani_polozaj()
            j = self.vrstica(p-1)
            self.polozaj[p-1][j] = self.na_potezi
        else:
            # Poteza ni veljavna
            return None
        (zmagovalec, stirka) = self.stanje_igre()
        if zmagovalec == NI_KONEC:
            # Igra se nadaljuje, na potezi je nasprotnik
            self.na_potezi = nasprotnik(self.na_potezi)
        else:
            # Igra se je zaključila
            self.na_potezi = None
        self.zadnja = ([self.polozaj[i][:] for i in range(7)], self.na_potezi)
        return (zmagovalec, stirka, (k,j) if p<0 else (p-1,j), je_popout)

    def razveljavi(self):
        '''Razveljavi potezo in se vrne v prejšnje stanje.'''
        if self.stevec > 0:
            (self.polozaj, self.na_potezi) = self.zgodovina[self.stevec-1]
            self.stevec -= 1
            return (self.polozaj, self.na_potezi)
        else:
            return None

    def shrani_polozaj(self):
        '''Shrani trenutni položaj igre, da se lahko vanj vrnemo
            s klicem metode 'razveljavi'.'''
        p = [self.polozaj[i][:] for i in range(7)]
        self.zgodovina.append((p, self.na_potezi))
        self.stevec += 1

    def stanje_igre(self):
        '''Vrne nam trenutno stanje igre. Možnosti so:
            - (IGRALEC_R, stirka), če je igre konec in je zmagal IGRALEC_R z dano zmagovalno štirko,
            - (IGRALEC_Y, stirka), če je igre konec in je zmagal IGRALEC_Y z dano zmagovalno štirko,
            - (NEODLOCENO, None), če je igre konec in je neodločeno,
            - (NI_KONEC, None), če je igra še vedno v teku.'''
        # Najprej preverimo, če obstaja kakšna zmagovalna štirka
        for s in Igra.stirke:
            ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
            barva = self.polozaj[i1][j1]
            if (barva != PRAZNO) and (barva == self.polozaj[i2][j2] == self.polozaj[i3][j3] == self.polozaj[i4][j4]):
                # s je naša zmagovalna štirka
                return (barva, s)
        # Če zmagovalca ni, moramo preveriti, če je igre konec
        poteze = self.veljavne_poteze()
        if len(poteze) > 0:
            # Obstaja še vsaj 1 veljavna poteza
            return (NI_KONEC, None)
        else:
            # Če pridemo do sem, so vsa polja zasedena in ni več veljavnih potez
            # Pravtako tudi zmagovalca ni, torej je rezultat neodločen
            return (NEODLOCENO, None)

##    def stevilo_dosegljivih_stirk(self):
##        '''Vrne koliko zmagovalnih štirk še lahko posamezen igralec doseže.'''
##        # Takih potez bo za posameznega igralca največ len(Igra.stirke) = 69
##        stevilo = [0, 0] # Prvo imamo stevilo rdecih nato rumenih
##        
##        for s in Igra.stirke:
##            ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
##            barve = list(set([self.polozaj[i1][j1], self.polozaj[i2][j2],
##                     self.polozaj[i3][j4], self.polozaj[i4][j4]]))
##            if len(barve) == 1:
##                if barve[0] == IGRALEC_R:
##                    stevilo[0] += 1
##                elif barve[0] == IGRALEC_Y:
##                    stevilo[1] += 1
##                else:
##                    stevilo[0] += 1
##                    stevilo[1] += 1
##            elif len(barve) == 2:
##                if PRAZNO in barve:
##                    b = list(set(barve) - set([PRAZNO]))[0]
##                    if b == IGRALEC_R:
##                        stevilo[0] += 1
##                    else:
##                        stevilo[1] += 1
##                else:
##                    continue
##            else:
##                continue
##        return stevilo

    def stevilo_zetonov(self):
        '''Vrne število žetonov na igralnem območju.'''
        # Teh bo največ 6*7 = 42
        st_zet = 0
        for i in self.polozaj:
            st_zet += i.count(IGRALEC_R)
            st_zet += i.count(IGRALEC_Y)
        return st_zet

    def uveljavi(self):
        '''Uveljavi zadnjo razveljavljeno potezo in se vrne v njeno stanje.'''
        if self.stevec < len(self.zgodovina)-1: # -1 začasno, dokler ne dodam zadnje poteze
            self.stevec += 1
            (self.polozaj, self.na_potezi) = self.zgodovina[self.stevec]
            return (self.polozaj, self.na_potezi)
        elif self.stevec == len(self.zgodovina)-1:
            self.stevec += 1
            (self.polozaj, self.na_potezi) = self.zadnja
            return (self.polozaj, self.na_potezi)
        else:
            return None

    def veljavne_poteze(self):
        '''Vrne seznam veljavnih potez.'''
        poteze = []
        for (i,a) in enumerate(self.polozaj):
            if a[-1] == 0:
                poteze.append(i+1)
        return poteze
    
    def vrstica(self, i):
        for (j,b) in enumerate(self.polozaj[i]):
            if b == 0:
                return j
