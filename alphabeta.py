from logika import IGRALEC_R, IGRALEC_Y, PRAZNO, NEODLOCENO, NI_KONEC, MAKSIMALNO_STEVILO_POTEZ, nasprotnik
from five_logika import Five_logika
from powerup_logika import Powerup_logika, POWER_STOLPEC, POWER_ZETON, POWER_2X_NW, POWER_2X_W
from pop10_logika import Pop10_logika
from pop_logika import Pop_logika
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
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            # Nismo bili prekinjeni, torej potezo izvedemo
            self.poteza = poteza

    def uredi_poteze(self, poteze):
        '''Vrne urejen seznam potez, ki ga nato uporabimo v alphabeta.'''
        urejene_poteze = [] # Urejen seznam potez
        if isinstance(self.igra, Five_logika):
            # Imamo 5 v vrsto
            zeljen_vrstni_red = [1,4,7] # Željen vrstni red, če so na voljo vse poteze
            zeljen_vrstni_red = random.sample(zeljen_vrstni_red, 3)
            for i in range(1,3):
                dodajamo = [4-i,4+i] # Poteze, ki jih želimo dodati
                dodajamo = random.sample(dodajamo, 2)
                for j in dodajamo:
                    zeljen_vrstni_red.append(j)
        elif isinstance(self.igra, Powerup_logika):
            # Imamo Power Up igro
            
            # Dodajmo dvojne poteze brez možnosti zmage
            # Najprej dodamo te, ker če bi takšne z možnostjo zmage,
            # bi jih (lahek) algoritem že na začetku porabil
            zeljen_vrstni_red = [74]
            for i in range(1,4):
                zeljen_vrstni_red += random.sample([74+i, 74-i], 2)
            # Dodajmo dvojne poteze z možno zmago
            zeljen_vrstni_red.append(84)
            for i in range(1,4):
                zeljen_vrstni_red += random.sample([84+i, 84-i], 2)
            # Dodajmo 'navadne' poteze
            zeljen_vrstni_red.append(4)
            for i in range(1,4):
                zeljen_vrstni_red += random.sample([4+i, 4-i], 2)
            # Dodajmo poteze, ki poteptajo stolpec pod sabo
            zeljen_vrstni_red.append(14)
            for i in range(1,4):
                zeljen_vrstni_red += random.sample([14+i, 14-i], 2)
            # Dodajmo poteze, ki odstranijo nasprotnikov žeton
            zeljen_vrstni_red += random.sample([24+7*i for i in range(6)], 6)
            for i in range(1,4):
                dodajamo = [24+i+7*j for j in range(6)] + [24-i+7*j for j in range(6)]
                zeljen_vrstni_red += random.sample(dodajamo, 12)
        elif isinstance(self.igra, Pop10_logika):
            # Imamo Pop 10 igro
            if self.igra.faza == 1:
                # Smo v fazi odstranjevanja žetonov
                zeljen_vrstni_red = random.sample([18, 68, 25, 75], 4) # Središčni dve polji
                dodajamo = [10, 11, 12, 17, 19, 24, 26, 31, 32, 33]
                dodajamo += [50+i for i in dodajamo]
                zeljen_vrstni_red += random.sample(dodajamo, len(dodajamo))
                dodajamo = [i for i in range(2, 7)] + [i for i in range(37, 42)] + [9+7*i for i in range(4)] + [13+7*i for i in range(4)]
                dodajamo += [50+i for i in dodajamo]
                zeljen_vrstni_red += random.sample(dodajamo, len(dodajamo))
                dodajamo = [1+7*i for i in range(6)] + [7+7*i for i in range(6)]
                dodajamo += [50+i for i in dodajamo]
                zeljen_vrstni_red += random.sample(dodajamo, len(dodajamo))                
            else:
                # Smo v fazi dodajanja žetonov (lahko faza 0 ali 2)
                zeljen_vrstni_red = [4]
                for i in range(1,4):
                    zeljen_vrstni_red += random.sample([4+i, 4-i], 2)
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
        '''Vrne oceno vrednosti polozaja.'''
        vrednost = 0
        if self.igra is None:
            # Če bi se slučajno zgodilo, da ne bi bila izbrana nobena igra
            return vrednost
        elif self.igra.na_potezi is None:
            # Igre je konec
            # Sem ne bi smeli nikoli priti zaradi if stavkov v alphabeta
            return vrednost
        else:
            delez = 0.8 # Faktor za katerega mu je izguba manj vredna kot dobiček
            tocke = [0, 0] # Sem bomo shranili število točk igralcev [R,Y]
            # Najprej preverimo kateri tip igre imamo
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

                for s in stirke_R: # Štirke na voljo rdečemu
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                    stirka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                             self.igra.polozaj[i3][j3], self.igra.polozaj[i4][j4]]
                    if IGRALEC_Y in stirka:
                        continue
                    else:
                        tocke[0] += 0.2 + stirka.count(IGRALEC_R) / 5
                for s in stirke_Y: # Štirke na voljo rumenemu
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                    stirka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                             self.igra.polozaj[i3][j3], self.igra.polozaj[i4][j4]]
                    if IGRALEC_R in stirka:
                        continue
                    else:
                        tocke[1] += 0.2 + stirka.count(IGRALEC_Y) / 5
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
                            else:
                                tocke[1] += petka.count(b) / 5
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
            elif isinstance(self.igra, Pop10_logika):
                # Naš cilj tukaj je, da bi imeli čim več štirk in še pomembneje,
                # da bi izločili čim več žetonov
                vrednost_tocke = AlphaBeta.ZMAGA / 30 # Da ne bomo nikoli imeli > ZMAGA brez da smo zmagali. To je vbistvu vrednost zmagovalne štirke.
                for s in self.igra.stirke:
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                    stirka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                              self.igra.polozaj[i3][j3], self.igra.polozaj[i4][j4]]
                    tocke[0] += stirka.count(IGRALEC_R) / 4 / (10-self.igra.odstranjeni[0])
                    tocke[1] += stirka.count(IGRALEC_Y) / 4 / (10-self.igra.odstranjeni[1])
                vrednost_razlike_ods = (self.igra.odstranjeni[0] - self.igra.odstranjeni[1]) * 3 # Vrednost razlike odstranjenih
                if self.jaz == IGRALEC_R:
                    vrednost += (tocke[0] - delez*tocke[1] + vrednost_razlike_ods) * vrednost_tocke
                elif self.jaz == IGRALEC_Y:
                    vrednost += (tocke[1] - delez*tocke[0] - vrednost_razlike_ods) * vrednost_tocke
                vrednost *= 0.984**(max(self.igra.stevilo_potez - 42, 0)) / 10
                return vrednost
            else:
                # Imamo normalno, popout ali powerup igro
                # Pojdimo sedaj skozi vse možne zmagovalne štirke in jih
                # primerno ovrednotimo
                # Stirke, ki ze vsebujejo zetone obeh igralec so vredne 0 tock
                # Prazne stirke so vredne 0.1 tocke
                # Ostale so vredne a/4 tock, kjer je a stevilo zetonov znotraj stirke
                for s in self.igra.stirke:
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
                            else:
                                tocke[1] += stirka.count(b) / 4
                        else:
                            continue
                    elif barve == [PRAZNO]:
                        # Štirka je prazna
                        tocke[0] += 0.1
                        tocke[1] += 0.1
                    else:
                        # V štirki so rumene in rdeče
                        continue
            
            if self.jaz == IGRALEC_R:
                vrednost += (tocke[0] - delez*tocke[1]) / 69 * 0.1 * AlphaBeta.ZMAGA
            else:
                vrednost += (tocke[1] - delez*tocke[0]) / 69 * 0.1 * AlphaBeta.ZMAGA
            if isinstance(self.igra, Pop_logika):
                k = 0.984**self.igra.stevilo_potez
            elif isinstance(self.igra, Powerup_logika):
                k = 1 - self.igra.stevilo_potez / (2*58)
            else:
                k = 1 - self.igra.stevilo_potez / (2*6*7)
            vrednost *= k
        return vrednost

    def alphabeta(self, globina, alpha, beta, maksimiziramo):
        '''Glavna metoda AlphaBeta.
            Vrne zmagovalno potezo in njeno vrednost, če jo najde, sicer (None, 0).'''
        if self.prekinitev:
            # Sporočili so nam, da moramo prekiniti
            return (None, 0)

        (zmagovalec, stirka) = self.igra.stanje_igre()
        if zmagovalec in (IGRALEC_R, IGRALEC_Y, NEODLOCENO):
            if isinstance(self.igra, Pop10_logika):
                k = 0.984**(max(self.igra.stevilo_potez - 42, 0))
            elif isinstance(self.igra, Pop_logika):
                k = 0.984**self.igra.stevilo_potez
            elif isinstance(self.igra, Powerup_logika):
                k = 1 - self.igra.stevilo_potez / (2*58) # Kjer je 58 max število potez v tej igri
            else:
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
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                # Naredimo en korak alphabeta metode
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    for p in self.uredi_poteze(self.igra.veljavne_poteze()):
                        self.igra.povleci_potezo(p, True)
                        if (p > 70 and isinstance(self.igra, Powerup_logika)) or (isinstance(self.igra, Pop10_logika) and self.igra.faza == 2):
                            # Imamo dvojno potezo
                            for p2 in self.uredi_poteze(self.igra.veljavne_poteze()):
                                self.igra.povleci_potezo(p2, True)
                                vrednost = self.alphabeta(max(globina-2, 0), alpha, beta, not maksimiziramo)[1]
                                self.igra.razveljavi()
                                if vrednost > alpha:
                                    najboljsa_poteza = [p, p2]
                                    alpha = vrednost
                                if najboljsa_poteza is None:
                                    najboljsa_poteza = [p, p2]
                                if beta <= alpha:
                                    break
                            self.igra.razveljavi()
                            if beta <= alpha:
                                break
                        else:
                            vrednost = self.alphabeta(globina-1, alpha, beta, not maksimiziramo)[1]
                            self.igra.razveljavi()
                            if vrednost > alpha:
                                najboljsa_poteza = p
                                alpha = vrednost
                            if najboljsa_poteza is None:
                                najboljsa_poteza = p
                            if beta <= alpha:
                                break
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    for p in self.uredi_poteze(self.igra.veljavne_poteze()):
                        self.igra.povleci_potezo(p, True)
                        if (p > 70 and isinstance(self.igra, Powerup_logika)) or (isinstance(self.igra, Pop10_logika) and self.igra.faza == 2):
                            # Imamo dvojno potezo
                            for p2 in self.uredi_poteze(self.igra.veljavne_poteze()):
                                self.igra.povleci_potezo(p2, True)
                                vrednost = self.alphabeta(max(globina-2, 0), alpha, beta, not maksimiziramo)[1]
                                self.igra.razveljavi()
                                if vrednost < beta:
                                    najboljsa_poteza = [p, p2]
                                    beta = vrednost
                                if najboljsa_poteza is None:
                                    najboljsa_poteza = [p, p2]
                                if beta <= alpha:
                                    break
                            self.igra.razveljavi()
                            if beta <= alpha:
                                break
                        else:
                            vrednost = self.alphabeta(globina-1, alpha, beta, not maksimiziramo)[1]
                            self.igra.razveljavi()
                            if vrednost < beta:
                                najboljsa_poteza = p
                                beta = vrednost
                            if najboljsa_poteza is None:
                                najboljsa_poteza = p
                            if beta <= alpha:
                                break
                assert (najboljsa_poteza is not None), 'alphabeta: izračunana poteza je None, veljavne_poteze={0}, globina={1}'.format(self.igra.veljavne_poteze(), globina)
                return (najboljsa_poteza, alpha if maksimiziramo else beta)
        else:
            assert False, 'alphabeta: nedefinirano stanje igre'
