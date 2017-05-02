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
        if racunalnik or p in poteze:
            # Poteza je veljavna
            if len(self.zgodovina) > self.stevec:
                # Bili smo v zgodovini in povlekli novo potezo
                # Vsaj zgodovina naprej od števca torej 'zapade'
                self.zgodovina = self.zgodovina[:self.stevec]
            self.shrani_polozaj()
            if p < 0:
                # Imamo Pop out potezo
                k = -p-1 # Kateri stolpec to dejansko je
                # Odstranimo spodnji žeton
                del self.polozaj[k][0]
                self.polozaj[k].append(PRAZNO)
                je_popout = True
            else:
                # Imamo 'navadno' potezo
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
        return (zmagovalec, stirka, (p-1,j) if p>0 else None, je_popout) # Če je p<0, je je_popout=True, torej ne izrisujemo poteze, ki je torej lahko None

    def stanje_igre(self):
        '''Vrne nam trenutno stanje igre. Možnosti so:
            - (IGRALEC_R, [stirka]), če je igre konec in je zmagal IGRALEC_R z dano zmagovalno štirko,
            - (IGRALEC_Y, [stirka]), če je igre konec in je zmagal IGRALEC_Y z dano zmagovalno štirko,
            - (NEODLOCENO, None), če je igre konec in je neodločeno ter ni nobenih štirk,
            - (NEODLOCENO, [stirki]), če je igre konec in je neodločeno ter sta štirki različnih barv,
            - (NI_KONEC, None), če je igra še vedno v teku.'''
        # Najprej preverimo, če obstaja kakšna zmagovalna štirka ali izenačitveni štirki
        # Hranili bomo največ 1 štirko na igralca
        zmagovalci = [] # Seznam igralcev, ki imajo vsaj 1 štirko
        stirke = [] # Štirke različnih igralcev
        for s in Logika.stirke:
            ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
            barva = self.polozaj[i1][j1]
            if (barva != PRAZNO) and (barva == self.polozaj[i2][j2] == self.polozaj[i3][j3] == self.polozaj[i4][j4]):
                # s se pojavi v igri
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
            if a[0] == barva:
                # Spodnji element stolpca je od igralca, ki je na potezi
                poteze.append(-i-1)
        return poteze
