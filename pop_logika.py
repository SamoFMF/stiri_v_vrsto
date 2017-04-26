from logika import *

###################
## LOGIKA POPOUT ##
###################

class Pop_logika(Logika):

    def kopija(self):
        '''Vrne kopijo te igre, brez zgodovine.'''
        k = Pop_logika()
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
        
        je_popout = False # Če bo poteza popout, bomo morali osvežiti grafični prikaz igralne površine

        # Preverimo, če je poteza veljavna
        if p < 0:
            k = -(p+1) # Kateri stolpec to dejansko je
            if racunalnik or p in poteze:
                # Imamo popout potezo
                if len(self.zgodovina) > self.stevec:
                    self.zgodovina = self.zgodovina[:self.stevec]
                self.shrani_polozaj()
                # Odstranimo spodnji žeton
                del self.polozaj[k][0]
                self.polozaj[k].append(PRAZNO)
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
        elif racunalnik or p in poteze:
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

    def stanje_igre(self):
        '''Vrne nam trenutno stanje igre. Možnosti so:
            - (IGRALEC_R, stirka), če je igre konec in je zmagal IGRALEC_R z dano zmagovalno štirko,
            - (IGRALEC_Y, stirka), če je igre konec in je zmagal IGRALEC_Y z dano zmagovalno štirko,
            - (NEODLOCENO, None), če je igre konec in je neodločeno,
            - (NI_KONEC, None), če je igra še vedno v teku.'''
        # Najprej preverimo, če obstaja kakšna zmagovalna štirka
        zmagovalci = []
        stirke = []
        for s in Logika.stirke:
            ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
            barva = self.polozaj[i1][j1]
            if (barva != PRAZNO) and (barva == self.polozaj[i2][j2] == self.polozaj[i3][j3] == self.polozaj[i4][j4]):
                # s je naša zmagovalna štirka
                if barva in zmagovalci:
                    # Ta igralec že ima vsaj 1 zmagovalno štirko
                    continue
                else:
                    zmagovalci.append(barva)
                    stirke.append(s)
        if len(zmagovalci) == 1:
            return (zmagovalci[0], stirke)
        elif len(zmagovalci) == 2:
            # Imamo 2 zmagovalca, torej je igra neodločena
            return (NEODLOCENO, stirke)
        # Če zmagovalca ni, moramo preveriti, če je igre konec
        poteze = self.veljavne_poteze()
        if len(poteze) > 0:
            # Obstaja še vsaj 1 veljavna poteza
            return (NI_KONEC, None)
        else:
            # Če pridemo do sem, so vsa polja zasedena in ni več veljavnih potez
            # Pravtako tudi zmagovalca ni, torej je rezultat neodločen
            return (NEODLOCENO, None)

    def veljavne_poteze(self):
        '''Vrne seznam veljavnih potez.'''
        poteze = []
        barva = self.na_potezi
        for (i,a) in enumerate(self.polozaj):
            if a[-1] == PRAZNO:
                # V stolpcu je še vsaj 1 prosto mesto
                poteze.append(i+1)
            if barva and a[0] == barva:
                # Spodnji element stolpca je od igralca, ki je na potezi
                poteze.append(-i-1)
        return poteze
