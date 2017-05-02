import random

#################
## LOGIKA IGRE ##
#################

IGRALEC_R = 1 # Igralec, ki ima rdeče krogce
IGRALEC_Y = 2 # Igralec, ki ima rumene krogce
PRAZNO = 0 # Prazno polje
NEODLOCENO = "neodločeno" # Igra se je končala z neodločenim izzidom
NI_KONEC = "ni konec" # Igre še ni konec
MAKSIMALNO_STEVILO_POTEZ = 150 # Najdaljša dovoljena igra (da nimamo neskončnih iger)

def nasprotnik(igralec):
    '''Vrne nasprotnika od igralca.'''
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
        assert False, "neveljaven nasprotnik = {0}".format(igralec)

class Logika():
    # Tabela vseh možnih zmagovalnih kombinacij igre 4 v vrsto (hrani položaje)
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

    
    def __init__(self):
        # Ustvarimo seznam trenutne pozicije
        self.polozaj = [[PRAZNO]*6 for i in range(7)]

        # Prvi na potezi je naključni igralec.
        self.na_potezi = random.choice([IGRALEC_R, IGRALEC_Y])

        # Shranjujmo si zgodovino, da lahko uporabimo 'undo'
        self.zgodovina = []

        # Števec, ki nam pove, na katerem mestu v zgodovini smo
        self.stevec = 0

        # Zadnje stanje igre, če želiš `Redo`-jati do konca
        self.zadnja_poteza = ([self.polozaj[i][:] for i in range(7)], self.na_potezi)

        # Število potez, ki se nato uporabi pri računanju vrednosti položaja
        # To imamo zato, ker število žetonov na plošči ni vedno
        #   točen pokazatelj števila odigranih potez (glej Pop Out)
        self.stevilo_potez = 0

    def kopija(self):
        '''Vrni kopijo te igre, brez zgodovine.'''
        # Potrebujemo, da se ne rišejo poteze, ko računalnik razmišlja
        k = Logika()
        k.polozaj = [self.polozaj[i][:] for i in range(7)]
        k.na_potezi = self.na_potezi
        k.stevilo_potez = self.stevilo_potez
        return k

    def povleci_potezo(self, p, racunalnik=False):
        '''Povleci potezo p, če je veljavna, sicer ne naredi nič.
            Veljavna igra -> vrne stanje_igre() po potezi, sicer None.'''
        if racunalnik:
            # Računalnik izbira samo med veljavnimi potezami
            # S tem si prihranimo ponovno računanje veljavnih potez
            pass
        else:
            # Potezo vleče človek
            poteze = self.veljavne_poteze()

        # Preverimo, če je poteza veljavna
        if racunalnik or p in poteze:
            # Poteza je veljavna
            if len(self.zgodovina) > self.stevec:
                # Bili smo v zgodovini in povlekli novo potezo
                # Vsaj zgodovina naprej od števca torej 'zapade'
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
        return (zmagovalec, stirka, (p-1,j), False)

    def razveljavi(self, i=1):
        '''Razveljavi potezo in se vrne v prejšnje stanje.
            Uspe razveljaviti -> vrne prejšnje stanje, None sicer.'''
        if self.stevec > i-1:
            # Zgodovina je dovolj globoka, da gremo 'i' korakov nazaj
            if self.stevec == len(self.zgodovina):
                # Smo bili na koncu zgodovine, ki pa ne hrani trenutnega stanja
                # Zato si ga shranimo v self.zadnja_poteza
                # TODO
                self.zadnja_poteza = ([self.polozaj[i][:] for i in range(7)], self.na_potezi)
            self.stevec -= i
            (self.polozaj, self.na_potezi) = self.zgodovina[self.stevec]
            self.stevilo_potez -= i
            return (self.polozaj, self.na_potezi)
        else:
            return None

    def shrani_polozaj(self):
        '''Shrani trenutni položaj igre, da se lahko vanj vrnemo
            s klicem metode 'razveljavi'.'''
        p = [self.polozaj[i][:] for i in range(7)]
        self.zgodovina.append((p, self.na_potezi))
        self.stevec += 1
        self.stevilo_potez += 1

    def stanje_igre(self):
        '''Vrne nam trenutno stanje igre. Možnosti so:
            - (IGRALEC_R, [stirka]), če je igre konec in je zmagal IGRALEC_R z dano zmagovalno štirko,
            - (IGRALEC_Y, [stirka]), če je igre konec in je zmagal IGRALEC_Y z dano zmagovalno štirko,
            - (NEODLOCENO, None), če je igre konec in je neodločeno,
            - (NI_KONEC, None), če je igra še vedno v teku.'''
        # Najprej preverimo, če obstaja kakšna zmagovalna štirka
        for s in Logika.stirke:
            ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
            barva = self.polozaj[i1][j1]
            if (barva != PRAZNO) and (barva == self.polozaj[i2][j2] == self.polozaj[i3][j3] == self.polozaj[i4][j4]):
                # s je naša zmagovalna štirka
                return (barva, [s])
        # Če zmagovalca ni, moramo preveriti, če je igre konec
        poteze = self.veljavne_poteze()
        if len(poteze) > 0:
            # Obstaja še vsaj 1 veljavna poteza
            return (NI_KONEC, None)
        else:
            # Če pridemo do sem, so vsa polja zasedena in ni več veljavnih potez
            # Pravtako tudi zmagovalca ni, torej je rezultat neodločen
            return (NEODLOCENO, None)

    def uveljavi(self, i=1):
        '''Uveljavi zadnjo razveljavljeno potezo in se vrne v njeno stanje.
            Uspe uveljaviti -> vrne novo stanje, None sicer.'''
        # TODO
        if self.stevec < len(self.zgodovina)-i:
            self.stevec += i
            (self.polozaj, self.na_potezi) = self.zgodovina[self.stevec]
            self.stevilo_potez += i
            return (self.polozaj, self.na_potezi)
        elif self.stevec == len(self.zgodovina)-i:
            self.stevec += i
            (self.polozaj, self.na_potezi) = self.zadnja_poteza
            self.stevilo_potez += i
            return (self.polozaj, self.na_potezi)
        else:
            return None

    def veljavne_poteze(self):
        '''Vrne seznam veljavnih potez.'''
        poteze = []
        for (i,a) in enumerate(self.polozaj):
            if a[-1] == PRAZNO:
                poteze.append(i+1)
        return poteze
    
    def vrstica(self, i):
        '''Vrne najnižjo vrstico, ki je na voljo v i-tem stolpcu,
            oz. None, če je ni.'''
        for (j,b) in enumerate(self.polozaj[i]):
            if b == PRAZNO:
                # Kličemo samo v primeru, ko imamo veljavno potezo,
                # torej bo vedno obstajal tak b
                return j
        return None
