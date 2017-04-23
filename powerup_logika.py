####################
## LOGIKA POWERUP ##
####################

from logika import *

class Powerup_logika(Igra):

    def __init__(self):
        super(Powerup_logika, self).__init__()

        # Vsak igralec ima na voljo 4x 'power up'
        # V tem seznamu seznamov bomo hranili kateri 'power up' še ima
        # kateri igralec na voljo
        # Po vrsti so: Poteptaj stolpec, odstrani nasprotnikov žeton, 2x non-winning move, 2x move
        self.powerups = [[1, 1, 1, 1], [1, 1, 1, 1]]

        # Shranimo stanje, ki nam pove, če igralec sme v naslednji potezi zmagati
        # Vrednost False bo zaseglo, če bo uporabljen 2x non-winning power up
        self.sme_zmagati = True

    def ima_zmagovalca(self):
        '''Vrne zmagovalca, če je igre konec, None sicer.'''
        for s in Igra.stirke:
            ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
            barva = self.polozaj[i1][j1]
            if (barva != PRAZNO) and (barva == self.polozaj[i2][j2] == self.polozaj[i3][j3] == self.polozaj[i4][j4]):
                # s je naša zmagovalna štirka
                return barva
        return None

    def kopija(self):
        '''Vrne kopijo te igre, brez zgodovine.'''
        k = Powerup_logika()
        k.polozaj = [self.polozaj[i][:] for i in range(7)]
        k.na_potezi = self.na_potezi
        k.stevilo_potez = self.stevilo_potez
        return k

    def povleci_potezo(self, p):
        '''Povleci potezo p, če je veljavna, sicer ne naredi nič.
            Veljavna igra -> vrne stanje_igre() po potezi, sicer None.'''
        poteze = self.veljavne_poteze()
        ponovi = False # Pove, če bo na potezi še 1x isti igralec
        osvezi = False # Če moramo osvežiti igralno površino, ker smo izbrisali kakšne žetone

        # Preverimo, če je poteza veljavna
        if p in poteze:
            self.sme_zmagati = True
            # Poteza je veljavna
            if len(self.zgodovina) > self.stevec:
                self.zgodovina = self.zgodovina[:self.stevec]
            self.shrani_polozaj()
            if p < 11:
                # Imamo 'normalno' potezo
                j = self.vrstica(p-1)
                self.polozaj[p-1][j] = self.na_potezi
            elif p < 21:
                # Imamo potezo, ki potepta stolpec
                stolpec = p - 11
                self.polozaj[stolpec] = [self.na_potezi, 0, 0, 0, 0, 0]
                osvezi = True
            elif p < 71:
                # Imamo potezo, ki odstrani nasprotnikov žeton
                stolpec = (p - 21) % 7
                vrstica = (p - 21) // 7
                del self.polozaj[stolpec][vrstica]
                self.polozaj[stolpec].append(0)
                osvezi = True
            elif p < 81:
                # Imamo dvojno potezo brez dovoljene zmage
                j = self.vrstica(p-71)
                self.polozaj[p-71][j] = self.na_potezi
                ponovi = True
                self.sme_zmagati = False
            else:
                # Imamo dvojno potezo z dovoljeno zmago
                j = self.vrstica(p-81)
                self.polozaj[p-81][j] = self.na_potezi
                ponovi = True
        else:
            # Poteza ni veljavna
            return None
        (zmagovalec, stirka) = self.stanje_igre()
        if zmagovalec == NI_KONEC:
            # Igra se nadaljuje
            if ponovi:
                # Na potezi je ponovno isti igralec
                pass
            else:
                # Na potezi je nasprotnik
                self.na_potezi = nasprotnik(self.na_potezi)
        else:
            # Igra se je zaključila
            self.na_potezi = None
        self.zadnja = ([self.polozaj[i][:] for i in range(7)], self.na_potezi)
        return (zmagovalec, stirka, (p%10-1,j) if (p<11 or p>70) else 0, osvezi)

    def veljavne_poteze(self):
        '''Vrne seznam veljavnih potez.'''
        poteze = []
        kateri_igr = 0 if self.na_potezi == IGRALEC_R else 1
        # Najprej dodajmo 'normalne' poteze
        for (i,a) in enumerate(self.polozaj):
            if a[-1] == 0:
                if self.sme_zmagati:
                    poteze.append(i+1)
                    zmagovalec = self.ima_zmagovalca()
                elif zmagovalec == self.na_potezi:
                    # Poteza ni dovoljena, moramo jo odstraniti
                    del poteze[-1]
                else:
                    # Poteza je dovoljena
                    pass

        # Dodajmo poteze, kjer poteptamo stolpec
        # Označimo jih z 11-17
        if self.powerups[kateri_igr][0] == 1:
            for (i,a) in enumerate(self.polozaj):
                if a[0] == 0:
                    # Stolpec je prazen
                    # To je kar navadna poteza, nočemo se ponavljati ali porabiti 'power up-a'
                    continue
                else:
                    poteze.append(11+i)
                
        # Dodajmo poteze, kjer odstranimo nasprotnikov žeton
        # Označimo jih z 21-62
        if self.powerups[kateri_igr][1] == 1:
            for (i,a) in enumerate(self.polozaj):
                for (j,barva) in enumerate(a):
                    if barva == nasprotnik(self.na_potezi):
                        poteze.append(21+i+7*j)

        # Dodajmo poteze, kjer bo naslednja poteza zaporedna brez možnosti zmage
        # Označimo jih z 71-77
        if self.powerups[kateri_igr][2] == 1:
            for (i,a) in enumerate(self.polozaj):
                if a[-1] == 0:
                    poteze.append(71+i)

        # Dodajmo poteze, kjer bo naslednja poteza zaporedna z možnostjo zmage
        # Označimo jih z 81-88
        if self.powerups[kateri_igr][3] == 1:
            for (i,a) in enumerate(self.polozaj):
                if a[-1] == 0:
                    poteze.append(81+i)
        
        return poteze
