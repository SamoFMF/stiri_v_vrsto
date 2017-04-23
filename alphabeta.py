import logging

from logika import IGRALEC_R, IGRALEC_Y, PRAZNO, NEODLOCENO, NI_KONEC, nasprotnik, NEVELJAVNO
from five_logika import Five_logika
import random

#######################
## ALGORITEM MINIMAX ##
#######################

class AlphaBeta:
    # Algoritem alphabeta

    def __init__(self, globina):
        self.globina = globina # Kako globoko iščemo?
        self.prekinitev = False # Želimo algoritem prekiniti?
        self.igra = None # Objekt, ki predstavlja igro
        self.jaz = None # Katerega igralca igramo?
        self.poteza = None # Sem vpišemo potezo, ko jo najdemo

    def prekini(self):
        '''Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
            je uporabnik zapr okno ali izbral novo igro.'''
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        '''Izračunaj potezo za trenutno stanje dane igre.'''
        # To metodo pokličemo iz vzporednega vlakna
        self.igra = igra
        self.jaz = self.igra.na_potezi
        self.prekinitev = False # Glavno vlakno bo to nastavilo na True, če bomo morali prekiniti
        self.poteza = None # Sem napišemo potezo, ko jo najdemo

        # Poženemo alphabeta
        (poteza, vrednost) = self.alphabeta(self.globina, -AlphaBeta.NESKONCNO, AlphaBeta.NESKONCNO, True)
        assert (poteza is not None), 'alphabeta: izračunana poteza je None'
        print('igralec = {2}, poteza = {0}, vrednost = {1}'.format(poteza, vrednost, self.jaz))
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            # Nismo bili prekinjeni, torej potezo izvedemo
            self.poteza = poteza

    def uredi_poteze(self, poteze):
        '''Uredi seznam potez, ki ga nato uporabimo v alphabeta.'''
        urejene_poteze = [] # Urejen seznam potez
        if isinstance(self.igra, Five_logika):
            # Imamo 5 v vrsto
            zeljen_vrstni_red = [1,-1,4,-4,7,-7] # Željen vrstni red, če so na voljo vse poteze
            zeljen_vrstni_red = random.sample(zeljen_vrstni_red, 6)
            for i in range(1,3):
                dodajamo = [4-i,-4+i,4+i,-4-i] # Poteze, ki jih želimo dodati
                dodajamo = random.sample(dodajamo, 4)
                for j in dodajamo:
                    zeljen_vrstni_red.append(j)
        else:
            # Imamo 4 v vrsto ali Pop Out
            zeljen_vrstni_red = [4,-4] # Željen vrstni red, če so na voljo vse poteze
            for i in range(1,4):
                dodajamo = [4-i,-4+i,4+i,-4-i] # Poteze, ki jih želimo dodati
                dodajamo = random.sample(dodajamo, 4)
                for j in dodajamo:
                    zeljen_vrstni_red.append(j)
        for i in zeljen_vrstni_red:
            if i in poteze:
                # Poteza je na voljo, treba jo je dodati
                urejene_poteze.append(i)
            else:
                # Poteza ni na voljo
                continue
        return urejene_poteze

    # Vrednosti igre
    ZMAGA = 10**5
    NESKONCNO = ZMAGA + 1 # Več kot zmaga

    def vrednost_pozicije(self):
        '''Ocena vrednosti polozaja.'''
        vrednost = 0
        if self.igra is None:
            # Če bi se slučajno zgodilo, da ne bi bila izbrana nobena igra
            return vrednost
        elif self.igra.na_potezi is None:
            # Igre je konec
            # Sem ne bi smeli nikoli priti zaradi if stavkov v alphabeta
            return vrednost
        else:
            a = 0.8 # Faktor za katerega mu je izguba manj vredna kot dobiček
            # Najprej preverimo ker tip igre imamo
            if isinstance(self.igra, Five_logika):
                # Imamo 5 v vrsto, torej imamo zmagovalne štirke (robne)
                # ter petke, pokličimo jih spodaj
                stirke_R = self.igra.stirke_R
                stirke_Y = self.igra.stirke_Y
                petke = self.igra.petke

                # Pojdimo skozi vse štirke & petke ter jih primerno ovrednotimo
                # Štirke / petke, ki vsebujejo žetone obeh igralcev so vredne 0 točk
                # Prazne petke so vredne 0.1 točke
                # Štirke so vredne 0.2 + a/5 točke, kjer je a število žetonov v štirki,
                # če je igralec pravilne barve za to štirko.
                # Petke so vredne a/5 točke, kjer je a število žetonov v petki.
                tocke = [0, 0] # Sem bomo shranili število točk igralcev [R,Y]

                for s in stirke_R: # Štirke na voljo rdečemu
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                    stirka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                             self.igra.polozaj[i3][j3], self.igra.polozaj[i4][j4]]
                    if IGRALEC_Y in stirka:
                        continue
                    else:
                        tocke[0] += 0.2 + stirka.count(IGRALEC_R) / 5
                        tocke[1] -= a * (0.2 + stirka.count(IGRALEC_R) / 5)
                for s in stirke_Y: # Štirke na voljo rumenemu
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                    stirka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                             self.igra.polozaj[i3][j3], self.igra.polozaj[i4][j4]]
                    if IGRALEC_R in stirka:
                        continue
                    else:
                        tocke[1] += 0.2 + stirka.count(IGRALEC_Y) / 5
                        tocke[0] -= a * (0.2 + stirka.count(IGRALEC_Y) / 5)

                for p in petke:
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4),(i5,j5)) = p
                    petka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                             self.igra.polozaj[i3][j3], self.igra.polozaj[i4][j4],
                             self.igra.polozaj[i5][j5]]
                    barve = list(set(stirka))
                    if len(barve) == 2:
                        if PRAZNO in barve:
                            # V petki so žetoni samo 1 barve
                            b = list(set(barve) - set([PRAZNO]))[0]
                            if b == IGRALEC_R:
                                tocke[0] += petka.count(b) / 5
                                tocke[1] -= a * (petka.count(b) / 5)
                            else:
                                tocke[1] += petka.count(b) / 5
                                tocke[0] -= a * (petka.count(b) / 5)
                        else:
                            # V petki so rdeči in rumeni
                            continue
                    elif barve == [PRAZNO]:
                        # Petka je prazna
                        tocke[0] += 0.1
                        tocke[1] += 0.1
                    else:
                        # V petki so rumeni in rdeči žetoni
                        continue
            else:
                # Imamo normalno ali popout igro, torej so štirke definirane sledeče
                stirke = self.igra.stirke
                # Pojdimo sedaj skozi vse možne zmagovalne štirke in jih
                # primerno ovrednotimo
                # Stirke, ki ze vsebujejo zetone obeh igralec so vredne 0 tock
                # Prazne stirke so vredne 0.1 tocke
                # Ostale so vredne a/4 tock, kjer je a stevilo zetonov znotraj stirke
                tocke = [0, 0] # Sem bomo shranili stevilo tock igralcev [R,Y]
                for s in stirke:
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                    stirka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                             self.igra.polozaj[i3][j3], self.igra.polozaj[i4][j4]]
                    barve = list(set(stirka))
                    # barve bo dolžine 2 ali 3, če bi bilo dolžine 1,
                    # bi bilo igre že konec
                    if len(barve) == 2:
                        if PRAZNO in barve:
                            # V štirki so žetoni samo 1 barve
                            b = list(set(barve) - set([PRAZNO]))[0]
                            if b == IGRALEC_R:
                                tocke[0] += stirka.count(b) / 4
                                tocke[1] -= a * (stirka.count(b) / 4)
                            else:
                                tocke[1] += stirka.count(b) / 4
                                tocke[0] -= a * (stirka.count(b) / 4)
                        else:
                            continue
                    elif barve == [PRAZNO]:
                        # Štirka je prazna
                        tocke[0] += 0.1
                        tocke[1] += 0.1
                    else:
                        # V štirki so rumene in rdeče
                        continue
                    
            (dos1, dos2) = tocke
            if self.jaz == IGRALEC_R:
                vrednost += (dos1 - dos2) / 69 * 0.1 * AlphaBeta.ZMAGA
            else:
                vrednost += (dos2 - dos1) / 69 * 0.1 * AlphaBeta.ZMAGA
            # Tukaj opazimo, da pri Pop Out lahko pride, da množimo z negativno vrednostjo
            vrednost *= 1 - self.igra.stevilo_potez / (2*6*7)
        return int(vrednost)

    def alphabeta(self, globina, alpha, beta, maksimiziramo):
        '''Glavna metoda AlphaBeta.'''
        if self.prekinitev:
            # Sporočili so nam, da moramo prekiniti
            return (None, 0)

        (zmagovalec, stirka) = self.igra.stanje_igre()
        if zmagovalec in (IGRALEC_R, IGRALEC_Y, NEODLOCENO):
            # Tukaj opazimo, da pri Pop Out lahko pride do tega, da je k < 0
            # Premisli, kaj storiti
            k = 1 - self.igra.stevilo_potez / (2*6*7)
            # Igre je konec, vrnemo njeno vrednost
            if zmagovalec == self.jaz:
                return (None, AlphaBeta.ZMAGA * k)
            elif zmagovalec == nasprotnik(self.jaz):
                return (None, -AlphaBeta.ZMAGA * k)
            else:
                return (None, 0)
        elif zmagovalec == NI_KONEC:
            # Igre ni konec
            igralec = self.igra.na_potezi
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                # Naredimo en korak alphabeta metode
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    for p in self.uredi_poteze(self.igra.veljavne_poteze()):
                        self.igra.povleci_potezo(p)
                        vrednost = self.alphabeta(globina-1, alpha, beta, not maksimiziramo)[1]
                        self.igra.razveljavi1()
                        if vrednost > alpha:
                            najboljsa_poteza = p
                            alpha = vrednost
                        if beta <= alpha:
                            break
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    for p in self.uredi_poteze(self.igra.veljavne_poteze()):
                        self.igra.povleci_potezo(p)
                        vrednost = self.alphabeta(globina-1, alpha, beta, not maksimiziramo)[1]
                        self.igra.razveljavi1()
                        if vrednost < beta:
                            najboljsa_poteza = p
                            beta = vrednost
                        if beta <= alpha:
                            break
                return (najboljsa_poteza, alpha if maksimiziramo else beta)
        else:
            assert False, 'alphabeta: nedefinirano stanje igre'
