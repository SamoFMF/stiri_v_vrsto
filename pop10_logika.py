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

        # Preverimo najprej, če smo v fazi 1 in je poteza p+50 namesto p
        if self.faza == 1 and not p in poteze and p+50 in poteze:
            p += 50

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
                i = (p % 50 - 1) % 7
                j = (p % 50 - 1) // 7
                del self.polozaj[i][j]
                self.polozaj[i].append(0)
                osvezi = True
                if p > 50:
                    # Žeton ni bil v štirki, ponovno smo na potezi
                    self.faza = 2
                elif self.na_potezi == IGRALEC_R:
                    self.odstranjeni[0] += 1
                elif self.na_potezi == IGRALEC_Y:
                    self.odstranjeni[1] += 1
            else:
                # Smo v fazi 2 (dodajanje odstranjenih žetonov)
                j = self.vrstica(p-1)
                self.polozaj[p-1][j] = self.na_potezi
                self.faza = 1
        else:
            # Poteza ni veljavna
            return None
        (zmagovalec, stirka) = self.stanje_igre()
        if zmagovalec == NI_KONEC:
            # Igra se nadaljuje
            if self.faza == 2:
                # Na potezi je ponovno isti igralec
                pass
            else:
                # Na potezi je nasprotnik
                self.na_potezi = nasprotnik(self.na_potezi)
        else:
            # Igra se je zaključila
            self.na_potezi = None
        self.zadnja = ([self.polozaj[i][:] for i in range(7)], self.na_potezi)
        return (zmagovalec, stirka, (p-1,j), osvezi) # (p-1,j) nas ne zanima, ko je osvezi == 1, torej pri edinem primeru, kjer to ni pravi zapis (self.faza = 1)

    def razveljavi(self, i=1):
        '''Razveljavi potezo in se vrne v prejšnje stanje.'''
        if self.stevec > i-1:
            self.stevec -= i
            (self.polozaj, self.na_potezi, self.faza, self.odstranjeni) = self.zgodovina[self.stevec]
            self.stevilo_potez -= i
            return (self.polozaj, self.na_potezi)
        else:
            return None

    def shrani_polozaj(self):
        '''Shrani trenutni položaj igre, da se lahko vanj vrnemo
            s klicem metode 'razveljavi'.'''
        p = [self.polozaj[i][:] for i in range(7)] # Položaj
        ods = [i for i in self.odstranjeni] # Število odstranjenih žetonov
        self.zgodovina.append((p, self.na_potezi, self.faza, ods))
        self.stevec += 1
        self.stevilo_potez += 1
    
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
            return (IGRALEC_R, None)
        elif self.odstranjeni[1] == 10:
            # Zmagal je rumeni
            return (IGRALEC_Y, None)
        else:
            return (NI_KONEC, None)

    def uveljavi(self, i=1):
        '''Uveljavi zadnjo razveljavljeno potezo in se vrne v njeno stanje.'''
        if self.stevec < len(self.zgodovina)-i:
            self.stevec += i
            (self.polozaj, self.na_potezi, self.faza, self.odstranjeni) = self.zgodovina[self.stevec]
            self.stevilo_potez += i
            return (self.polozaj, self.na_potezi)
        elif self.stevec == len(self.zgodovina)-i:
            self.stevec += 1
            (self.polozaj, self.na_potezi, self.faza, self.odstranjeni) = self.zadnja
            self.stevilo_potez += i
            return (self.polozaj, self.na_potez)
        else:
            return None

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
                for (j,b) in enumerate(a):
                    if b == self.na_potezi:
                        # Na položaju je naš žeton, lahko ga odstranimo
                        if self.znotraj_stirke(i,j):
                            # Žeton je znotraj štirke
                            # Poteze so označene z 1-42
                            poteze.append(i+1+7*j)
                        else:
                            # Žeton ni znotraj nobene štirke
                            # Ta poteza nas postavi v fazo 2
                            # Poteze so označene z 51-92
                            poteze.append(i+51+7*j)
            return poteze
        else:
            # Smo v fazi dodajanja žetona na vrh
            
            poteze = []
            for (i,a) in enumerate(self.polozaj):
                if a[-1] == 0:
                    poteze.append(i+1)
            return poteze

    def znotraj_stirke(self, x, y):
        '''Pove, če je žeton na (x,y) položaju v kakšni štirki.'''
        # Funkcija bo vrnila True, če je žeton (x,y) znotraj
        # kake štirke in False sicer
        for s in Igra.stirke:
            if (x,y) in s:
                ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                stirka = [self.polozaj[i1][j1], self.polozaj[i2][j2],
                          self.polozaj[i3][j3], self.polozaj[i4][j4]]
                if stirka.count(self.na_potezi) == 4:
                    # Imamo štirko
                    return True
        return False
