#################
## LOGIKA IGRE ##
#################

from logika import *

class Pop10_logika(Igra):

    def __init__(self):
        # Prekopiramo __init__ iz objekta Igra
        super(Pop10_logika, self).__init__()

        # V spremenljivko 'faza' bomo shranili fazo igre, ki je lahko:
        # 0: Igralca še dodajata žetone - vsak dodaja žetone nasprotnika
        # 1: Igralca odstranjujeta žetone
        # 2: Igralec dodaja žeton, ki ga je odstranil
        self.faza = 0

        # Število žetonov, ki jih je posamezen igralec uspešno odstranil
        # Seznam je oblike [Rdeči, Rumeni]
        self.odstranjeni = [0, 0]

    def kopija(self):
        '''Vrne kopijo te igre, brez zgodovine.'''
        k = Pop10_logika()
        k.polozaj = [self.polozaj[i][:] for i in range(7)]
        k.na_potezi = self.na_potezi
        k.stevilo_potez = self.stevilo_potez
        k.faza = self.faza
        k.odstranjeni = [i for i in self.odstranjeni]
        return k

    def povleci_potezo(self, p):
        '''Povleci potezo p, če je veljavna, sicer ne naredi nič.
            Veljavna igra -> vrne stanje_igre() po potezi, sicer None.'''
        poteze = self.veljavne_poteze()
        osvezi = False # Če moramo osvežiti grafični prikaz igralne površine
        dvojna = False # Ostane isti igralec na potezi?

        # Preverimo, če je poteza veljavna
        if p in poteze:
            # Poteza je veljavna
            if len(self.zgodovina) > self.stevec:
                self.zgodovina = self.zgodovina[:self.stevec]
            self.shrani_polozaj()

            if self.faza == 0:
                # Smo v fazi 0 (sestavljanje igralne površine)
                j = self.vrstica(p-1)
                self.polozaj[p-1][j] = nasprotnik(self.na_potezi)
                if self.stevilo_potez == 42:
                    # Zapolnili smo igralno površino, čas za fazo 1
                    self.faza = 1
            elif self.faza == 1:
                # Smo v fazi 1 (odstranjevanje žetonov)
                if p == 21:
                    # Nimamo "veljavnih" potez, ne naredi ničesar
                    pass
                else:
                    # Imamo veljavno potezo
                    j = 0
                    del self.polozaj[p%10-1][j]
                    self.polozaj[p%10-1].append(j)
                    osvezi = True
                    if p > 10:
                        dvojna = True
                        self.faza = 3
                    elif self.na_potezi == IGRALEC_R:
                        self.odstranjeni[0] += 1
                    elif self.na_potezi == IGRALEC_Y:
                        self.odstranjeni[1] += 1
            else:
                # Smo v fazi 3 (dodajanje odstranjenih žetonov)
                j = self.vrstica(p-1)
                self.polozaj[p-1][j] = self.na_potezi
                self.faza = 2
        else:
            # Poteza ni veljavna
            return None
        (zmagovalec, stirka) = self.stanje_igre()
        if zmagovalec == NI_KONEC:
            # Igra se nadaljuje
            if dvojna:
                # Na potezi je ponovno isti igralec
                pass
            else:
                # Na potezi je nasprotnik
                self.na_potezi = nasprotnik(self.na_potezi)
        else:
            # Igra se je zaključila
            self.na_potezi = None
        self.zadnja = ([self.polozaj[i][:] for i in range(7)], self.na_potezi)
        return (zmagovalec, stirka, None if (self.faza == 1 and p == 21) else (p%10-1,j), osvezi)

    def stanje_igre(self):
        '''Vrne nam trenutno stanje igre. Možnosti so:
            - (IGRALEC_R, stirka), če je igre konec in je zmagal IGRALEC_R z dano zmagovalno štirko,
            - (IGRALEC_Y, stirka), če je igre konec in je zmagal IGRALEC_Y z dano zmagovalno štirko,
            - (NEODLOCENO, None), če je igre konec in je neodločeno,
            - (NI_KONEC, None), če je igra še vedno v teku.'''
        # Zaenkrat podajmo neko poljubno štirko ob koncu
        # Premisli, kako integrirati to v Gui brez štirke
        # TODO
        if self.odstranjeni[0] == 10:
            # Zmagal je rdeči
            return (IGRALEC_R, [(0,0),(1,0),(2,0),(3,0)])
        elif self.odstranjeni[1] == 10:
            # Zmagal je rumeni
            return (IGRALEC_Y, [(0,0),(1,0),(2,0),(3,0)])
        else:
            return (NI_KONEC, None)

    def veljavne_poteze(self):
        if self.faza == 0:
            # Smo v fazi dodajanja žetonov

            # Najprej preverimo v katero vrstico vstavljamo žetone
            vrstica = None
            for v in range(6):
                for (s,a) in enumerate(self.polozaj):
                    if a[v] == 0:
                        vrstica = v
                        break
                if vrstica is not None:
                    break
            assert (vrstica is not None), 'Smo v fazi "0", ko bi morali biti v fazi "1"'

            # Dodajmo sedaj proste poteze
            poteze = []
            for i in range(7):
                if self.polozaj[i][vrstica] == 0:
                    poteze.append(i+1)
            return poteze
        elif self.faza == 1:
            # Smo v fazi odstranjevanja žetonov

            poteze = []
            for (i,a) in enumerate(self.polozaj):
                if a[0] == self.na_potezi:
                    # Če je žeton v spodnji vrstici naš, ga lahko izvlečemo
                    if self.znotraj_stirke(i):
                        # Smo znotraj štirke
                        # Te poteze samo odstranijo žeton
                        poteze.append(i+1)
                    else:
                        # Nismo v nobeni štirki
                        # Te poteze nas postavijo v fazo 3
                        poteze.append(i+11)
            if len(poteze) == 0:
                # Če ni v spodnji vrstici nobenega našega žetona,
                # dodamo 'kvazi' potezo, ki bo samo spremenili igralca na potezi
                poteze.append(21)
            return poteze
        else:
            # Smo v fazi dodajanja žetona na vrh
            
            poteze = []
            for (i,a) in enumerate(self.polozaj):
                if a[-1] == 0:
                    poteze.append(i+1)
            return poteze

    def znotraj_stirke(self, p):
        '''Pove, če je poteza znotraj kake štirke.'''
        # Funkcija bo vrnila True, če je poteza p znotraj
        # kake štirke in False sicer
        i = p-1
        for s in Igra.stirke:
            if (i,0) in s:
                ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                stirka = [self.polozaj[i1][j1], self.polozaj[i2][j2],
                          self.polozaj[i3][j3], self.polozaj[i4][j4]]
                if stirka.count(self.na_potezi) == 4:
                    # Imamo štirko
                    return True
        return False
