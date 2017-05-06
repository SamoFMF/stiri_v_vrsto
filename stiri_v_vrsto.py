import tkinter # Uvozimo tkinter za uporabniški vmesnik
from math import sqrt
import random

from logika import *
from pop_logika import Pop_logika
from five_logika import Five_logika
from powerup_logika import Powerup_logika, POWER_STOLPEC, POWER_ZETON, POWER_2X_NW, POWER_2X_W
from pop10_logika import Pop10_logika
from clovek import *
from racunalnik import *
from rand_algoritem import Rand_alg
from alphabeta import AlphaBeta

#########################
## UPORABNIŠKI VMESNIK ##
#########################

# Najboljše, če se ne spreminja preveč, ker izgleda najlepše pri teh številkah
# Če že spreminjaš, povečaj, ne zmanjšaj in
# poizkusi ohraniti razmerje MIN_SIRINA / MIN_VISINA
# Preden spreminjaš si preberi v README poglavje 'Spreminjanje dimenzij'
MIN_SIRINA = 500
MIN_VISINA = 555
ZVP = 100 # Zacetna velikost polja

class Gui():
    # To so vsi grafični elementi v self.platno, ki 'pripadajo'
    # igralcema, torej krožci, ki so bili igrani
    TAG_FIGURA = 'figura'

    # Oznaka za črte, ki sestavljajo okvir
    TAG_OKVIR = 'okvir'

    # Oznaka za gumbe, ki so na voljo v meniju levo od igralne površine
    TAG_GUMB = 'gumb'

    # Oznaka za spremenljive dele na platno_menu
    TAG_SPREMENLJIVI = 'spremenljivi'

    # Velikost okvirja za stranski menu
    OKVIR = 5

    # Background barva za meni na levi
    BG_BARVA = 'black'

    # Visina in sirina platna z rezultatom itd.
    # ODSVETUJEM SPREMINJANJE - če že moraš, spremeni MIN_SIRINA in MIN_VISINA
    VISINA_PLATNO_MENU = 0.55 * MIN_VISINA
    SIRINA_PLATNO_MENU = 0.8 * MIN_SIRINA - 3 * OKVIR

    # Odmik od roba pri platno_menu
    ODMIK = int(SIRINA_PLATNO_MENU / 40)

    def __init__(self, master):
        self.igralec_r = None # Objekt, ki igra rdeče krogce
        self.igralec_y = None # Objekt, ki igra rumene krogce
        self.igra = None # Objekt, ki predstavlja igro
        self.velikost_polja = ZVP # Velikost polja
        self.velikost_gap = self.velikost_polja / 20 # Razdalja med okvirjem in figuro
        self.rezultat = [0, 0] # Trenutni rezultat

        self.velikost_pisave = int(min(Gui.SIRINA_PLATNO_MENU * 0.0793, Gui.VISINA_PLATNO_MENU / 10)) # Velikost pisave (t.j. pri izpisih za to, kdo je na potezi, kdo je zmagal itd.)

        self.tip_rdeci = tkinter.IntVar() # Kakšen je rdeči - 0='človek',1='rac-rand',2='rac-easy',3='rac-med',4='rac-hard',5='rac_nepr'
        self.tip_rumeni = tkinter.IntVar() # Kot pri rdečem

        self.tip_igre = tkinter.IntVar() # Katero igro igramo - 0='4inarow',1='5inarow',2='popout',3='powerup'

        self.pup = tkinter.IntVar() # Kateri power up imamo izbran - 0='noben',1='stolpec',2='zeton',3='2x-nw',4='2x-w'
        self.pup.set(0)
        self.pup_pomozni = 0 # Pomožni števec, ki bo povedal, kaj je bilo izbrano predhodno in bo omogočil 'odizbrati'

        # Slovar 'tipov' igralcev
        self.tipi_igralcev = {0: lambda: Clovek(self),
                              1: lambda: Racunalnik(self, Rand_alg()),
                              2: lambda: Racunalnik(self, AlphaBeta(2)),
                              3: lambda: Racunalnik(self, AlphaBeta(4)),
                              4: lambda: Racunalnik(self, AlphaBeta(6)),
                              5: lambda: Racunalnik(self, AlphaBeta(8))}

        # Slovar 'tipov' igre
        self.tipi_iger = {0: lambda: Logika(),
                          1: lambda: Five_logika(),
                          2: lambda: Pop_logika(),
                          3: lambda: Powerup_logika(),
                          4: lambda: Pop10_logika()}

        # Nastavimo imeni igralcev, ki jih lahko uporabnik nato spreminja
        self.ime_r = tkinter.StringVar() # Ime igralca z rdečimi žetoni
        self.ime_r.set('Rdeči') # Po defaultu je rdečemu ime 'Rdeči'
        self.ime_y = tkinter.StringVar() # Ime igralca z rumenimi žetoni
        self.ime_y.set('Rumeni') # Po defaultu je rumenemu ime 'Rumeni'
        
        # Beležiti želimo spremembe imen in ju primerno urediti
        self.ime_r.trace('w', lambda name, index, mode: self.uredi_ime(self.ime_r))
        self.ime_y.trace('w', lambda name, index, mode: self.uredi_ime(self.ime_y))

        # Beležiti želimo tudi spremembe tipa igre, da bomo s pomočjo tega določili ime igralcev
        self.tip_rdeci.trace('w', lambda name, index, mode: self.nastavi_ime_igralca(self.tip_rdeci.get(), IGRALEC_R))
        self.tip_rumeni.trace('w', lambda name, index, mode: self.nastavi_ime_igralca(self.tip_rumeni.get(), IGRALEC_Y))

        # Dodajmo slike za igro Power Up
        # OPOZORILO:
        # Pri spreminjanju velikosti menuja je potrebno primerno prilagoditi tudi
        # velikost slik. Dimenziji sta izračunani po formuli:
        # dim ~ a * (0.8 * MIN_SIRINA - 3 * OKVIR), kjer je a med 0.125 in 0.13
        self.slika_pup_2x_nw = tkinter.PhotoImage(file='slike/2x-nw-icon.gif') # Slika za 2x potezo brez dovoljene zmage
        self.slika_pup_2x_w = tkinter.PhotoImage(file='slike/2x-w-icon.gif') # Slika za 2x potezo brez omejitev
        self.slika_pup_cross = tkinter.PhotoImage(file='slike/cross-icon.gif') # Slika za beli 'X', ki skupaj s krogom predstavlja uničenje žetona
        self.slika_pup_stolpec = tkinter.PhotoImage(file='slike/stolpec-icon.gif') # Slika za poteptanje stolpca
        
        # Če uporabnik zapre okno, naj se pokliče self.zapri_okno
        master.protocol('WM_DELETE_WINDOW', lambda: self.zapri_okno(master))

        # Glavni menu
        menu = tkinter.Menu(master)
        master.config(menu=menu)

        # Podmenu "Igra"
        menu_igra = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Igra', menu=menu_igra)
        # Gumb za začetek nove igre
        menu_igra.add_command(label='Nova igra',
                              command=lambda: self.zacni_igro(nova=True))
        # Gumb za začetek naslednje igre
        menu_igra.add_command(label='Naslednja igra', command=self.naslednja_igra)
        menu_igra.add_separator()
        # Gumb za začetek igre 'štiri v vrsto'
        menu_igra.add_radiobutton(label='Štiri v vrsto',
                                  variable=self.tip_igre, value=0,
                                  command=lambda: self.naslednja_igra())
        # Gumb za začetek igre 'pet v vrsto'
        menu_igra.add_radiobutton(label='Pet v vrsto',
                                  variable=self.tip_igre, value=1,
                                  command=lambda: self.naslednja_igra())
        # Gumb za začetek igre 'pop out'
        menu_igra.add_radiobutton(label='Pop Out',
                                  variable=self.tip_igre, value=2,
                                  command=lambda: self.naslednja_igra())
        # Gumb za začetek igre 'power up'
        menu_igra.add_radiobutton(label='Power Up',
                                  variable=self.tip_igre, value=3,
                                  command=lambda: self.naslednja_igra())
        # Gumb za začetek igre 'pop ten'
        menu_igra.add_radiobutton(label='Pop 10',
                                  variable=self.tip_igre, value=4,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_separator()
        # Gumb za zapreti aplikacijo
        menu_igra.add_command(label='Izhod',
                              command=lambda: self.zapri_okno(master))

        # Podmenu "Uredi"
        menu_uredi = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Uredi', menu=menu_uredi)
        # Gumb, ki razveljavi potezo
        menu_uredi.add_command(label='Razveljavi', command=self.platno_razveljavi)
        # Gumb, ki uveljavi razveljavljeno potezo
        menu_uredi.add_command(label='Uveljavi', command=self.platno_uveljavi)

        # Podmenu "Rdeči"
        menu_rdeci = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Rdeči', menu=menu_rdeci)
        # Igralec je človek
        menu_rdeci.add_radiobutton(label='Človek',
                                   variable=self.tip_rdeci, value=0,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_separator()
        # Različne težavnosti za računalnik
        menu_rdeci.add_radiobutton(label='Računalnik - naključen',
                                   variable=self.tip_rdeci, value=1,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - lahek',
                                   variable=self.tip_rdeci, value=2,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - srednji',
                                   variable=self.tip_rdeci, value=3,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - težek',
                                   variable=self.tip_rdeci, value=4,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - nepremagljiv',
                                   variable=self.tip_rdeci, value=5,
                                   command=lambda: self.zacni_igro(True))

        # Podmenu "Rumeni"
        menu_rumeni = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Rumeni', menu=menu_rumeni)
        # Igralec je človek
        menu_rumeni.add_radiobutton(label='Človek',
                                   variable=self.tip_rumeni, value=0,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_separator()
        # Različne težavnosti za računalnik
        menu_rumeni.add_radiobutton(label='Računalnik - naključen',
                                   variable=self.tip_rumeni, value=1,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - lahek',
                                   variable=self.tip_rumeni, value=2,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - srednji',
                                   variable=self.tip_rumeni, value=3,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - težek',
                                   variable=self.tip_rumeni, value=4,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - nepremagljiv',
                                   variable=self.tip_rumeni, value=5,
                                   command=lambda: self.zacni_igro(True))

        ###############################################################
        ###############################################################
        ##                      IGRALNO OBMOČJE                      ##
        ###############################################################
        ###############################################################
        self.platno = tkinter.Canvas(master,
                                     width=8*self.velikost_polja,
                                     height=7*self.velikost_polja)
        self.platno.pack(fill=tkinter.BOTH, expand=1, side=tkinter.RIGHT)

        # Narišemo črte na igralnem polju (ustvarimo igralno površino)
        self.narisi_okvir()

        # Določimo, kaj se zgodi, ko uporabnik pritisne določene tipke
        self.platno.bind('<Button-1>', self.platno_klik)
        self.platno.bind_all('<Control-z>', self.platno_razveljavi)
        self.platno.bind_all('<Control-y>', self.platno_uveljavi)
        self.platno.bind('<Configure>', self.spremeni_velikost)

        ###############################################################
        ###############################################################
        ##                    UREJEVALNO OBMOČJE                     ##
        ###############################################################
        ###############################################################
        # Dodamo frame, kamor bomo postavili platno z rezultatom
        # ter meni z možnostmi
        self.stranski_menu = tkinter.Frame(master,
                                    width=0.8 * MIN_SIRINA,
                                    height=MIN_VISINA,
                                    relief=tkinter.GROOVE,
                                    borderwidth=Gui.OKVIR,
                                    bg=Gui.BG_BARVA)
        self.stranski_menu.pack(side=tkinter.LEFT, anchor=tkinter.NW)
        self.stranski_menu.grid_propagate(0)

        # Narišemo stransko platno, kjer bodo podatki o trenutni igri
        self.platno_menu = tkinter.Canvas(self.stranski_menu,
                                          width=Gui.SIRINA_PLATNO_MENU,
                                          height=Gui.VISINA_PLATNO_MENU,
                                          borderwidth=0,
                                          bg=Gui.BG_BARVA)
        self.platno_menu.grid(row=0, column=0, columnspan=4, sticky=tkinter.N)

        # Dodamo možnosti
        pad_y = (MIN_VISINA - Gui.VISINA_PLATNO_MENU) * 0.02 # pady vrednost
        self.gumb_nova_igra = tkinter.Button(self.stranski_menu, text='Nova igra',
                                             width=int(0.4*MIN_SIRINA/7.25),
                                             command=lambda: self.zacni_igro(nova=True))
        self.gumb_nova_igra.grid(row=1, column=0, columnspan=4, pady=pad_y)
        self.gumb_naslednja_igra = tkinter.Button(self.stranski_menu, text='Naslednja igra',
                                                  width=int(0.4*MIN_SIRINA/7.25),
                                                  command=self.naslednja_igra)
        self.gumb_naslednja_igra.grid(row=2, column=0, columnspan=4, pady=(0,pad_y))
        self.gumb_razveljavi = tkinter.Button(self.stranski_menu, text='Razveljavi',
                                              width=int(0.4*MIN_SIRINA/7.25),
                                              command=self.platno_razveljavi)
        self.gumb_razveljavi.grid(row=3, column=0, columnspan=4, pady=pad_y)
        self.gumb_uveljavi = tkinter.Button(self.stranski_menu, text='Uveljavi',
                                            width=int(0.4*MIN_SIRINA/7.25),
                                            command=self.platno_uveljavi)
        self.gumb_uveljavi.grid(row=4, column=0, columnspan=4, pady=(0,pad_y))
        
        # Ti gumbi so aktivni samo v primeru, da imamo 'Power Up' igro
        self.gumb_pup1 = tkinter.Radiobutton(self.stranski_menu, text='Stolpec',
                                             variable=self.pup, value=1,
                                             command=self.odznaci_gumb)
        self.gumb_pup1.grid(row=5,column=0, pady=3*pad_y)
        self.gumb_pup2 = tkinter.Radiobutton(self.stranski_menu, text='Uniči žeton',
                                             variable=self.pup, value=2,
                                             command=self.odznaci_gumb)
        self.gumb_pup2.grid(row=5,column=1, pady=3*pad_y)
        self.gumb_pup3 = tkinter.Radiobutton(self.stranski_menu, text='2x-NW',
                                             variable=self.pup, value=3,
                                             command=self.odznaci_gumb)
        self.gumb_pup3.grid(row=5,column=2,pady=3*pad_y)
        self.gumb_pup4 = tkinter.Radiobutton(self.stranski_menu, text='2x-W',
                                             variable=self.pup, value=4,
                                             command=self.odznaci_gumb)
        self.gumb_pup4.grid(row=5,column=3,pady=3*pad_y)

        # Vsi ti gumbi za power upe na začetku niso aktivni, saj pričnemo z navadno igro 'štiri v vrsto'
        self.gumb_pup1.config(state=tkinter.DISABLED)
        self.gumb_pup2.config(state=tkinter.DISABLED)
        self.gumb_pup3.config(state=tkinter.DISABLED)
        self.gumb_pup4.config(state=tkinter.DISABLED)

        # Gumb za izhod
        self.gumb_izhod = tkinter.Button(self.stranski_menu, text='Izhod',
                                         width=int(0.3*0.8*MIN_SIRINA/7.25),
                                         command=lambda: self.zapri_okno(master))
        self.gumb_izhod.grid(row=6, column=0, columnspan=4, pady=(3*pad_y,pad_y))

        # Narišemo figure za platno_menu
        # Najprej nespremenljiv del

        # Ustvarimo widget za ime rdečega igralca
        velikost_pisave_ime = int(min(Gui.SIRINA_PLATNO_MENU * 0.0661, Gui.VISINA_PLATNO_MENU/12)) # Velikost pisave za imeni
        self.platno_ime_r = tkinter.Entry(master, fg='red', bg=Gui.BG_BARVA,
                                font=('Helvetica', '{0}'.format(velikost_pisave_ime),
                                           'bold'),
                                width='10', borderwidth='0', justify='center',
                                textvariable=self.ime_r)
        
        # Ustvarimo widget za ime rumenega igralca
        self.platno_ime_y = tkinter.Entry(master, fg='yellow', bg=Gui.BG_BARVA,
                                font=('Helvetica', '{0}'.format(velikost_pisave_ime),
                                           'bold'),
                                width='10', borderwidth='0', justify='center',
                                textvariable=self.ime_y)

        self.ime_r_widget = self.platno_menu.create_window(Gui.SIRINA_PLATNO_MENU / 4, 2 * Gui.ODMIK, anchor=tkinter.N, window=self.platno_ime_r)
        
        self.ime_y_widget = self.platno_menu.create_window(3 * Gui.SIRINA_PLATNO_MENU / 4, 2 * Gui.ODMIK,
                                                           anchor=tkinter.N, window=self.platno_ime_y)

        # Uredimo velikosti vseh uporabljenih pisav
        self.doloci_velikost_pisave(velikost_pisave_ime)
        
        # Pričnemo igro
        self.zacni_igro(nova=True)

    def doloci_velikost_pisave(self, velikost):
        '''Določi self.velikost_pisave in velikost_pisave_ime.'''
        # Najprej preverimo, če je velikost pisave za ime pravilna in jo primerno popravimo
        velikost_pisave_ime = velikost
        while self.ime_r_widget in self.platno_menu.find_overlapping(0, 0, Gui.SIRINA_PLATNO_MENU / 40, Gui.VISINA_PLATNO_MENU / 10):
            velikost_pisave_ime -= 1
            self.platno_ime_r.config(font=('Helvetica', '{0}'.format(velikost_pisave_ime), 'bold'))
        self.platno_ime_y.config(font=('Helvetica', '{0}'.format(velikost_pisave_ime), 'bold'))

        # Sedaj pa še določimo pisavo teksta, ki nam pove, kdo je na potezi itd.
        # Ker je text centriran, je simetrično oddaljen od robov in lahko prevelimo glede na 1 stran
        x = 0.2 * Gui.SIRINA_PLATNO_MENU
        y = 0.5 * Gui.VISINA_PLATNO_MENU
        velikost_pisave = self.velikost_pisave
        zacasni_tag = 'zacasno' # Tag začasnega texta, ki ga uporabimo za določanje velikosti pisave
        self.zacasni_text = self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.VISINA_PLATNO_MENU / 2,
                                                         text='Na potezi je',
                                                         anchor=tkinter.CENTER,
                                                         font=('Helvetica', '{0}'.format(velikost_pisave), 'bold'),
                                                         tag=zacasni_tag)
        while self.zacasni_text in self.platno_menu.find_overlapping(0, y-1, x, y+1):
            velikost_pisave -= 1
            self.platno_menu.itemconfig(self.zacasni_text, font=('Helvetica','{0}'.format(velikost_pisave), 'bold'))
        self.velikost_pisave = velikost_pisave
        self.platno_menu.delete(zacasni_tag)

    def odznaci_gumb(self):
        '''Deselecta gumb, če je le-ta že bil izbran in ponovno kliknjen.'''
        if self.pup.get() == self.pup_pomozni:
            self.pup.set(0)
            self.pup_pomozni = 0
        else:
            self.pup_pomozni = self.pup.get()
        pass

    def koncaj_igro(self, zmagovalec, stirka):
        '''Nastavi stanje igre na 'konec igre'.'''
        self.narisi_platno_menu(zmagovalec)
        if stirka is not None:
            self.obkrozi(stirka)

    def narisi_okvir(self):
        '''Nariše črte (okvir) na igralno povrčino.'''
        self.platno.delete(Gui.TAG_OKVIR)
        d = self.velikost_polja
        for i in range(8):
            self.platno.create_line(d/2 + i*d, d/2,
                                    d/2 + i*d, 13*d/2,
                                    width=2,
                                    tag=Gui.TAG_OKVIR)
        for i in range(7):
            self.platno.create_line(d/2, d/2 + i*d,
                                    15*d/2, d/2 + i*d,
                                    width=2,
                                    tag=Gui.TAG_OKVIR)

    def narisi_R(self, p):
        '''Nariše rdeči žeton.'''
        d = self.velikost_polja
        x = (p[0] + 1) * d
        y = (6 - p[1]) * d
        gap = self.velikost_gap
        self.platno.create_oval(x - d/2 + gap, y - d/2 + gap,
                                x + d/2 - gap, y + d/2 - gap,
                                fill = 'red',
                                width=0,
                                tag=Gui.TAG_FIGURA)

    def narisi_platno_menu(self, zmagovalec=None):
        '''Nariše spremenljive dele od platno_menu.'''
        self.platno_menu.delete(Gui.TAG_SPREMENLJIVI)
        dy = Gui.VISINA_PLATNO_MENU / 6 # Korak za y os
        velikost_pisave = self.velikost_pisave
        self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 4, Gui.ODMIK+dy,
                                     text='{0}'.format(self.rezultat[0]),
                                     fill='white', anchor=tkinter.N,
                                     font=('Helvetica','{0}'.format(velikost_pisave),
                                           'bold'),
                                     tag=Gui.TAG_SPREMENLJIVI)
        self.platno_menu.create_text(3 * Gui.SIRINA_PLATNO_MENU / 4, Gui.ODMIK+dy,
                                     text='{0}'.format(self.rezultat[1]),
                                     fill='white', anchor=tkinter.N,
                                     font=('Helvetica','{0}'.format(velikost_pisave),
                                           'bold'),
                                     tag=Gui.TAG_SPREMENLJIVI)
        if zmagovalec==NEODLOCENO:
            # Izid je neodločen
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.ODMIK + 2.5*dy,
                                         text='Konec igre!',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(velikost_pisave),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.ODMIK + 3.5*dy,
                                         text='Izid je:',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(velikost_pisave),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.ODMIK + 4.5*dy,
                                         text='NEODLOČEN',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(velikost_pisave),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
        elif zmagovalec:
            # Imamo zmagovalca
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.ODMIK + 2.5*dy,
                                         text='Konec igre!',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(velikost_pisave),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.ODMIK + 3.5*dy,
                                         text='Zmagovalec je:',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(velikost_pisave),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.ODMIK + 4.5*dy,
                                         text='{0}'.format('RDEČI' if zmagovalec==IGRALEC_R else 'RUMENI'),
                                         fill='{0}'.format('red' if zmagovalec==IGRALEC_R else 'yellow'), anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(velikost_pisave),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
        else:
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.ODMIK + 2.5*dy,
                                         text='Na potezi je',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(velikost_pisave),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            r = 0.75 * min(0.132 * Gui.SIRINA_PLATNO_MENU, dy) # Polmer žetona, ki pove, kdo je na potezi
            self.platno_menu.create_oval(Gui.SIRINA_PLATNO_MENU / 2 - r, Gui.ODMIK + 4.5*dy - r,
                                         Gui.SIRINA_PLATNO_MENU / 2 + r, Gui.ODMIK + 4.5*dy + r,
                                         fill='{0}'.format('red' if self.igra.na_potezi==IGRALEC_R else 'yellow'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            if isinstance(self.igra, Powerup_logika):
                # Dodati moramo power upe
                pup_r = self.igra.powerups[0] # Power ups za rdečega
                pup_y = self.igra.powerups[1] # Power ups za rumenega
                stranica = Gui.SIRINA_PLATNO_MENU * 0.75 / 6 # Premer kroga za power up 'uniči žeton'
                # Za rdečega igralca
                if pup_r[POWER_STOLPEC] > 0:
                    self.platno_menu.create_image(Gui.ODMIK, Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_stolpec,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)
                if pup_r[POWER_ZETON] > 0:
                    self.platno_menu.create_oval(Gui.ODMIK, Gui.VISINA_PLATNO_MENU / 2,
                                                      Gui.ODMIK + stranica,
                                                      Gui.VISINA_PLATNO_MENU / 2 + stranica,
                                                      fill='yellow', tag=Gui.TAG_SPREMENLJIVI)
                    self.platno_menu.create_image(Gui.ODMIK, Gui.VISINA_PLATNO_MENU / 2,
                                                  image=self.slika_pup_cross,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)
                if pup_r[POWER_2X_NW] > 0:
                    self.platno_menu.create_image(Gui.ODMIK, 2 * Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_2x_nw,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)
                if pup_r[POWER_2X_W] > 0:
                    self.platno_menu.create_image(Gui.ODMIK, 5 * Gui.VISINA_PLATNO_MENU / 6,
                                                  image=self.slika_pup_2x_w,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)

                # Za rumenega igralca
                if pup_y[POWER_STOLPEC] > 0:
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - Gui.ODMIK, Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_stolpec,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
                if pup_y[POWER_ZETON] > 0:
                    self.platno_menu.create_oval(Gui.SIRINA_PLATNO_MENU - Gui.ODMIK, Gui.VISINA_PLATNO_MENU / 2,
                                                      Gui.SIRINA_PLATNO_MENU - Gui.ODMIK - stranica,
                                                      Gui.VISINA_PLATNO_MENU / 2 + stranica,
                                                      fill='red', tag=Gui.TAG_SPREMENLJIVI)
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - Gui.ODMIK, Gui.VISINA_PLATNO_MENU / 2,
                                                  image=self.slika_pup_cross,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
                if pup_y[POWER_2X_NW] > 0:
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - Gui.ODMIK, 2 * Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_2x_nw,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
                if pup_y[POWER_2X_W] > 0:
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - Gui.ODMIK, 5 * Gui.VISINA_PLATNO_MENU / 6,
                                                  image=self.slika_pup_2x_w,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
            elif isinstance(self.igra, Pop10_logika):
                # Dodajmo grafični prikaz odstranjenih žetonov
                premer = Gui.SIRINA_PLATNO_MENU * 0.7 / 6 # Premer krogov s številom odstranjenih žetonov
                velikost_stevca = int(min(Gui.SIRINA_PLATNO_MENU * 0.0529, Gui.VISINA_PLATNO_MENU / 15))
                # Za rdečega igralca
                self.platno_menu.create_oval(2*Gui.ODMIK, 1.5*Gui.ODMIK + 2.5*dy,
                                             2*Gui.ODMIK + premer, 1.5*Gui.ODMIK + 2.5*dy + premer,
                                             fill='red', tag=Gui.TAG_SPREMENLJIVI)
                self.platno_menu.create_text(2*Gui.ODMIK + premer / 2, 1.5*Gui.ODMIK + 2.5*dy + premer / 2,
                                             text='{0}'.format(self.igra.odstranjeni[0]),
                                             fill='white', anchor=tkinter.CENTER,
                                             font=('Helvetica', '{0}'.format(velikost_stevca),
                                                   'bold'),
                                             tag=Gui.TAG_SPREMENLJIVI)

                # Za rumenega igralca
                self.platno_menu.create_oval(Gui.SIRINA_PLATNO_MENU - 2*Gui.ODMIK, 1.5*Gui.ODMIK + 2.5*dy,
                                             Gui.SIRINA_PLATNO_MENU - 2*Gui.ODMIK - premer, 1.5*Gui.ODMIK + 2.5*dy + premer,
                                             fill='yellow', tag=Gui.TAG_SPREMENLJIVI)
                self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU - 2*Gui.ODMIK - premer / 2,
                                             1.5*Gui.ODMIK + 2.5*dy + premer / 2,
                                             text='{0}'.format(self.igra.odstranjeni[1]),
                                             fill='black', anchor=tkinter.CENTER,
                                             font=('Helvetica', '{0}'.format(velikost_stevca),
                                                   'bold'),
                                             tag=Gui.TAG_SPREMENLJIVI)
                if self.igra.faza == 1:
                    velikost_navodil = int(min(Gui.SIRINA_PLATNO_MENU * 0.0396, Gui.VISINA_PLATNO_MENU / 20))
                    self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.VISINA_PLATNO_MENU,
                                                 text='Odstranite žeton!', fill='white',
                                                 anchor=tkinter.S,
                                                 font=('Helvetica',
                                                       '{0}'.format(velikost_navodil),
                                                       'bold'),
                                                 tag=Gui.TAG_SPREMENLJIVI)
                elif self.igra.faza == 2:
                    velikost_navodil = int(min(Gui.SIRINA_PLATNO_MENU * 0.0396, Gui.VISINA_PLATNO_MENU / 20))
                    self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.VISINA_PLATNO_MENU,
                                                 text='Vstavite žeton!', fill='white',
                                                 anchor=tkinter.S,
                                                 font=('Helvetica',
                                                       '{0}'.format(velikost_navodil),
                                                       'bold'),
                                                 tag=Gui.TAG_SPREMENLJIVI)

                                                         
    def narisi_polozaj(self):
        '''Na igralno površino nariše trenutni položaj igre.'''
        self.platno.delete(Gui.TAG_FIGURA)
        for (i, a) in enumerate(self.igra.polozaj):
            for (j, b) in enumerate(a):
                if b == IGRALEC_R:
                    self.narisi_R((i,j))
                elif b == IGRALEC_Y:
                    self.narisi_Y((i,j))

        if isinstance(self.igra, Five_logika):
            self.narisi_crtice()

    def narisi_crtice(self):
        '''Nariše pomožne barvne 'črte' za igro 'pet v vrsto'.'''
        d = self.velikost_polja
        sirina = 5 # Se ne prilagaja velikosti polja, ker je črtice na malih poljih potem nemogoče videti
        for i in range(6):
            barva1 = 'yellow' if i%2 == 0 else 'red'
            barva2 = 'red' if i%2 == 0 else 'yellow'
            self.platno.create_line(d/4, d/2 + d/4 + i*d,
                                    d/4, d/2 + 3*d/4 + i*d,
                                    tag=Gui.TAG_FIGURA,
                                    fill=barva1,
                                    width=sirina)
            self.platno.create_line(8*d - d/4, d/2 + d/4 + i*d,
                                    8*d - d/4, d/2 + 3*d/4 + i*d,
                                    tag=Gui.TAG_FIGURA,
                                    fill=barva2,
                                    width=sirina)

    def narisi_Y(self, p):
        '''Nariše rumeni žeton.'''
        d = self.velikost_polja
        x = (p[0] + 1) * d
        y = (6 - p[1]) * d
        gap = self.velikost_gap
        self.platno.create_oval(x - d/2 + gap, y - d/2 + gap,
                                x + d/2 - gap, y + d/2 - gap,
                                fill = 'yellow',
                                width=0,
                                tag=Gui.TAG_FIGURA)

    def naslednja_igra(self):
        '''Prične naslednjo igro.'''
        if self.igra.na_potezi is None:
            (zmagovalec, stirka) = self.igra.stanje_igre()
            if zmagovalec == IGRALEC_R:
                self.rezultat[0] += 1
            elif zmagovalec == IGRALEC_Y:
                self.rezultat[1] += 1
            else:
                self.rezultat[0] += 0.5
                self.rezultat[1] += 0.5
                if self.rezultat[0] == int(self.rezultat[0]):
                    self.rezultat[0] = int(self.rezultat[0])
                    self.rezultat[1] = int(self.rezultat[1])
        self.zacni_igro()

    def nastavi_ime_igralca(self, tip, barva):
        '''Metoda nastavi ime igralca.'''
        if tip == 0:
            ime = 'Rdeči' if barva == IGRALEC_R else 'Rumeni'
        elif tip == 1:
            ime = 'Random'
        elif tip == 2:
            ime = 'Lahek'
        elif tip == 3:
            ime = 'Srednji'
        elif tip == 4:
            ime = 'Težek'
        elif tip == 5:
            ime = 'Samo'
        else:
            # Ne bi smelo nikoli biti
            ime = 'Napaka'
        if barva == IGRALEC_R:
            self.ime_r.set(ime)
        elif barva == IGRALEC_Y:
            self.ime_y.set(ime)
        else:
            # Ne bi smelo nikoli biti
            pass

    def nova_igra(self):
        '''Ponastavi rezultat in začne novo igro.'''
        self.rezultat = [0, 0]
        self.zacni_igro()

    def obkrozi(self, stirke):
        '''Obkroži zmagovalno štirko oz. štirke.'''
        d = self.velikost_polja
        w = 5 # Odsvetujem spreminjanje (namenoma je fiksna vrednost). Širina črte.
        for stirka in stirke: # Gremo po vseh štirkah
            (i1,j1) = stirka[0]
            (i2,j2) = stirka[-1]
            if (i1 == i2) or (j1 == j2):
                # Štirka je vodoravna ali navpična
                x1 = d/2 + i1*d
                y1 = 13*d/2 - j1*d
                x2 = d/2 + (i2+1)*d
                y2 = 13*d/2 - (j2+1)*d
                self.platno.create_rectangle(x1, y1, x2, y2,
                                             width=w,
                                             tag=Gui.TAG_FIGURA)
            else:
                # Štirka je diagonalna
                # Najprej izračunamo središče S = (xt1,yt1)
                # najbolj levega kvadratka
                xt1 = (i1+1)*d
                yt1 = (6-j1)*d

                # Zarotiramo kvadrat za pi/4 v levo
                r = sqrt(2)*d/2
                x1 = xt1 - r
                y1 = yt1
                x2 = xt1
                # Če je štirka desno dol samo preslikamo y2 čez S
                y2 = yt1 + r if j1 < j2 else yt1 - r

                dxy = (sqrt(2) + 6) * d / 2 + (i2-i1-3)*d
                x3 = x1 + dxy
                x4 = x2 + dxy

                if j1 < j2:
                    y3 = y1 - dxy
                    y4 = y2 - dxy
                else:
                    y3 = y1 + dxy
                    y4 = y2 + dxy

                self.platno.create_line(x1, y1, x3, y3,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)
                self.platno.create_line(x2, y2, x4, y4,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)
                self.platno.create_line(x1, y1, x2, y2,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)
                self.platno.create_line(x3, y3, x4, y4,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)

    def platno_klik(self, event):
        '''Obravnava klik na igralni površini.'''
        (x,y) = (event.x, event.y)
        d = self.velikost_polja
        if (x < d/2) or (x > 15*d/2) or (y < d/2) or (y > 13*d/2):
            # V tem primeru smo zunaj igralnega območja
            pass
        else:
            i = int((x - d/2) // d) + 1
            if i == 8:
                # Uporabnik je kliknil na desni rob
                i = 7
            j = 5 - int((y - d/2) // d)
            if j == 6:
                # Uporabnik je kliknil na zgornji rob
                j = 5
            if isinstance(self.igra, Powerup_logika):
                # Imamo Power Up igro
                if self.pup.get() == 0:
                    # Aktiven ni noben power up
                    # Naredimo navadno potezo, torej je i že pravilno definiran
                    pass
                elif self.pup.get() == 1:
                    # Imamo potezo, ki uniči stolpec pod seboj
                    i += 10
                elif self.pup.get() == 2:
                    # Imamo potezo, ki odstrani nasprotnikov žeton
                    i += 20 + 7*j
                elif self.pup.get() == 3:
                    # Imamo dvojno potezo, kjer NI dovoljeno zmagati
                    i += 70
                else:
                    # Imamo dvojno potezo, kjer JE dovoljeno zmagati
                    i += 80
            elif isinstance(self.igra, Pop_logika) and j == 0:
                i = -i
            elif isinstance(self.igra, Pop10_logika):
                if self.igra.faza == 1:
                    i += j*7
            if self.igra.na_potezi == IGRALEC_R:
                self.igralec_r.klik(i)
            elif self.igra.na_potezi == IGRALEC_Y:
                self.igralec_y.klik(i)
            else:
                # Nihče ni na potezi
                pass

    def platno_razveljavi(self, event=None):
        '''Razveljavimo zadnjo potezo in prikažemo prejšnje stanje.'''

        # Razveljavimo prejšnjo potezo
        # Če je en igralec računalnik, razveljavimo do zadnje igralčeve poteze
        if isinstance(self.igralec_r, Racunalnik):
            if isinstance(self.igralec_y, Racunalnik):
                # Oba igralca sta računalnik, ne naredi ničesar
                return
            elif self.igra.na_potezi == IGRALEC_R:
                # Na potezi računalnik, ne naredi ničesar
                return
            elif self.igra.na_potezi == IGRALEC_Y and not isinstance(self.igra, Powerup_logika) and not isinstance(self.igra, Pop10_logika):
                # Gremo 2 potezi nazaj, ker imata oba igralca na voljo le 'eno-potezne poteze'
                # Torej bo igralec vedno na vrsti, če gremo 2 potezi nazaj
                novo_stanje = self.igra.razveljavi(2)
            else:
                # Želimo iti toliko korakov nazaj, da bo na potezi ponovno človek
                koliko_nazaj = [0, False] # Nam pove, koliko potez nazaj moramo it in če je že sploh bil človek na potezi
                zgodovina = self.igra.zgodovina[:self.igra.stevec] # Omejimo se na zgodovino glede na trenutni položaj
                for zgo in zgodovina[::-1]:
                    koliko_nazaj[0] += 1
                    if zgo[1] == IGRALEC_Y:
                        koliko_nazaj[1] = True
                        break
                if koliko_nazaj[1]:
                    novo_stanje = self.igra.razveljavi(koliko_nazaj[0])
                else:
                    return
        elif isinstance(self.igralec_y, Racunalnik):
            if self.igra.na_potezi == IGRALEC_Y:
                # Na potezi računalnik, ne naredi ničesar
                return
            elif self.igra.na_potezi == IGRALEC_R and not isinstance(self.igra, Powerup_logika) and not isinstance(self.igra, Pop10_logika):
                # Gremo 2 potezi nazaj, ker imata oba igralca na voljo le 'eno-potezne poteze'
                # Torej bo igralec vedno na vrsti, če gremo 2 potezi nazaj
                novo_stanje = self.igra.razveljavi(2)
            else:
                # Želimo iti toliko korakov nazaj, da bo na potezi ponovno človek
                koliko_nazaj = [0, False] # Nam pove, koliko potez nazaj moramo it in če je že sploh bil človek na potezi
                zgodovina = self.igra.zgodovina[:self.igra.stevec] # Omejimo se na zgodovino glede na trenutni položaj
                for zgo in zgodovina[::-1]:
                    koliko_nazaj[0] += 1
                    if zgo[1] == IGRALEC_R:
                        koliko_nazaj[1] = True
                        break
                if koliko_nazaj[1]:
                    novo_stanje = self.igra.razveljavi(koliko_nazaj[0])
                else:
                    return
        else:
            # Igrata dva človeka, torej razveljavimo samo 1 potezo nazaj
            novo_stanje = self.igra.razveljavi()

        if novo_stanje:
            # Uspešno smo razveljavili potezo

            # Narišemo novi (trenutni) položaj
            self.narisi_polozaj()

            # Posodobimo stanje gumbov za powerupe
            self.stanje_gumbov()

            # Popravimo napis nad igralno površino
            self.narisi_platno_menu()

            # Naročimo naslednjemu igralcu, da igra
            if self.igra.na_potezi == IGRALEC_R:
                self.igralec_r.igraj()
            elif self.igra.na_potezi == IGRALEC_Y:
                self.igralec_y.igraj()
        else:
            # Smo na začetku 'zgodovine' (igre) oz. nismo uspeli razveljaviti
            return

    def platno_uveljavi(self, event=None):
        '''Uveljavimo zadnjo razveljavljeno potezo in se vrnemo v njeno stanje.'''

        # Uveljavimo prejšnjo potezo
        if isinstance(self.igralec_r, Racunalnik):
            if isinstance(self.igralec_y, Racunalnik):
                # Oba igralca sta računalnik, ne naredi ničesar
                return
            elif self.igra.na_potezi == IGRALEC_R:
                # Na potezi računalnik, ne naredi ničesar
                return
            else:
                # Lahko, da je naslednja računalnikova poteza bila dvojna, ali pa igre več ni
                koliko_naprej = 0 # Pove, koliko potez moramo iti naprej, da bo ponovno na potezi človek, ali pa bo konec igre
                # Najprej pa nas zanima, kje v zgodovini se sploh nahajamo
                prihodnost = self.igra.zgodovina[self.igra.stevec+1:] + [self.igra.zadnja_poteza]
                for prih in prihodnost:
                    koliko_naprej += 1
                    if prih[1] == IGRALEC_Y:
                        break
                novo_stanje = self.igra.uveljavi(koliko_naprej)
        elif isinstance(self.igralec_y, Racunalnik):
            if self.igra.na_potezi == IGRALEC_Y:
                # Na potezi računalnik, ne naredi ničesar
                return
            else:
                # Lahko, da je naslednja računalnikova poteza bila dvojna, ali pa igre več ni
                koliko_naprej = 0 # Pove, koliko potez moramo iti naprej, da bo ponovno na potezi človek, ali pa bo konec igre
                # Najprej pa nas zanima, kje v zgodovini se sploh nahajamo
                prihodnost = self.igra.zgodovina[self.igra.stevec+1:] + [self.igra.zadnja_poteza]
                for prih in prihodnost:
                    koliko_naprej += 1
                    if prih[1] == IGRALEC_Y:
                        break
                novo_stanje = self.igra.uveljavi(koliko_naprej)
        else:
            # Igrata dva človeka, torej uveljavimo samo 1 potezo
            novo_stanje = self.igra.uveljavi()


        if novo_stanje:
            # Uspešno smo uveljavili potezo

            # Narišemo novi (trenutni) položaj
            self.narisi_polozaj()

            # Posodobimo stanje gumbov za powerupe
            self.stanje_gumbov()

            # Uredimo grafični prikaz
            if self.igra.na_potezi == IGRALEC_R:
                self.narisi_platno_menu()
                self.igralec_r.igraj()
            elif self.igra.na_potezi == IGRALEC_Y:
                self.narisi_platno_menu()
                self.igralec_y.igraj()
            else:
                (zmagovalec, stirka) = self.igra.stanje_igre()
                self.koncaj_igro(zmagovalec, stirka)
        else:
            # Smo na koncu 'zgodovine' (igre) oz. nismo uspeli uveljaviti poteze
            return
    
    def povleci_potezo(self, p):
        '''Povleče potezo p na igralni površini.'''
        igralec = self.igra.na_potezi
        if isinstance(p, list):
            # Imamo dvojno potezo, ki jo je povlekel računalnik
            t1 = self.igra.povleci_potezo(p[0], True)
            t2 = self.igra.povleci_potezo(p[1], True)
            if (t1 is None) or (t2 is None):
                # Imamo neveljavno potezo
                # To se sicer računalniku ne bi smelo nikoli zgoditi
                return
            else:
                (zmagovalec1, stirka1, p1, osvezi1) = t1
                (zmagovalec2, stirka2, p2, osvezi2) = t2
                if osvezi1 or osvezi2:
                    # Pri prvi ali drugi potezi se je brisalo žetone, zato je potrebno
                    # grafični prikaz igralne površine osvežiti.
                    # S tem pravilno prikažemo tudi še potencialno ne-narisane žetone
                    self.narisi_polozaj()
                elif igralec == IGRALEC_R:
                    # Obe potezi moramo narisati
                    self.narisi_R(p1)
                    self.narisi_R(p2)
                elif igralec == IGRALEC_Y:
                    # Obe potezi moramo narisati
                    self.narisi_Y(p1)
                    self.narisi_Y(p2)

                # Uredimo stanje gumbov
                self.stanje_gumbov()
                
                # Preverimo, kako se bo igra nadaljevala
                if zmagovalec2 == NI_KONEC:
                    # Igre še ni konec
                    self.narisi_platno_menu()
                    if self.igra.na_potezi == IGRALEC_R:
                        self.igralec_r.igraj()
                    elif self.igra.na_potezi == IGRALEC_Y:
                        self.igralec_y.igraj()
                else:
                    # Igra se je končala
                    self.koncaj_igro(zmagovalec2, stirka2)
        else:
            # Shranimo v 'je_rac' True, če potezo vleče računalnik in False sicer
            if igralec == IGRALEC_R:
                je_rac = isinstance(self.igralec_r, Racunalnik)
            elif igralec == IGRALEC_Y:
                je_rac = isinstance(self.igralec_y, Racunalnik)
            t = self.igra.povleci_potezo(p, je_rac)
            if t is None:
                # Poteza ni bila veljavna
                pass
            else:
                if self.pup.get() > 0:
                    # Če imamo izbran kak power up, ga po tem,
                    # ko povlečemo potezo, unselectamo
                    self.odznaci_gumb()
                self.stanje_gumbov()
                (zmagovalec, stirka, p1, osvezi) = t # Tukaj je p1 položaj na platnu
                if osvezi:
                    self.narisi_polozaj()
                elif isinstance(self.igra, Pop10_logika) and (self.igra.faza == 0 or self.igra.zgodovina[-1][2] == 0):
                    if igralec == IGRALEC_R:
                        self.narisi_Y(p1)
                    elif igralec == IGRALEC_Y:
                        self.narisi_R(p1)
                else:
                    if igralec == IGRALEC_R:
                        self.narisi_R(p1)
                    elif igralec == IGRALEC_Y:
                        self.narisi_Y(p1)

                # Sedaj pa preverimo, kako se bo igra nadaljevala
                if zmagovalec == NI_KONEC:
                    # Igre še ni konec
                    self.narisi_platno_menu()
                    if self.igra.na_potezi == IGRALEC_R:
                        self.igralec_r.igraj()
                    elif self.igra.na_potezi == IGRALEC_Y:
                        self.igralec_y.igraj()
                else:
                    # Igra se je končala
                    self.koncaj_igro(zmagovalec, stirka)
    
    def prekini_igralce(self):
        '''Sporoči igralcem, da morajo nehati razmišljati.'''
        if self.igralec_r:
            self.igralec_r.prekini()
        if self.igralec_y:
            self.igralec_y.prekini()

    def spremeni_velikost(self, event):
        '''Ta funkcija nam prilagaja velikost polja igralnega območja
            glede na velikost celotnega okna.'''
        # Spraznimo platno
        self.platno.delete('all')
        # Poračunamo nove dimenzije
        (w,h) = (event.width, event.height)
        self.velikost_polja = min(w / 8, h / 7)
        self.velikost_gap = self.velikost_polja / 20
        # Popravimo velikost platna
        self.platno.config(width=w-0.9*MIN_SIRINA, height=h-200)
        # Narišemo novo igralno površino
        self.narisi_okvir()
        self.narisi_polozaj()
        if self.igra.na_potezi is None:
            (zmagovalec, stirka) = self.igra.stanje_igre()
            self.koncaj_igro(zmagovalec, stirka)

    def stanje_gumbov(self):
        '''Vklopi gumbe za power upe, če smo v pravi igri, sicer jih izklopi.'''
        tip = self.tip_igre.get()
        if tip == 3:
            # Imamo power up igro, vklopi gumbe
            if (self.igra.na_potezi is not None) and ((self.igra.na_potezi == IGRALEC_R and isinstance(self.igralec_r, Clovek)) or (self.igra.na_potezi == IGRALEC_Y and isinstance(self.igralec_y, Clovek))):
                # Nekdo je na potezi in ta nekdo je človek
                kateri_igr = 0 if self.igra.na_potezi == IGRALEC_R else 1 # Nam pove, kateri seznam powerupov gledamo
                if self.igra.powerups[kateri_igr][POWER_STOLPEC]:
                    self.gumb_pup1.config(state=tkinter.NORMAL)
                else:
                    self.gumb_pup1.config(state=tkinter.DISABLED)
                if self.igra.powerups[kateri_igr][POWER_ZETON]:
                    self.gumb_pup2.config(state=tkinter.NORMAL)
                else:
                    self.gumb_pup2.config(state=tkinter.DISABLED)
                if self.igra.powerups[kateri_igr][POWER_2X_NW]:
                    self.gumb_pup3.config(state=tkinter.NORMAL)
                else:
                    self.gumb_pup3.config(state=tkinter.DISABLED)
                if self.igra.powerups[kateri_igr][POWER_2X_W]:
                    self.gumb_pup4.config(state=tkinter.NORMAL)
                else:
                    self.gumb_pup4.config(state=tkinter.DISABLED)
            else:
                self.gumb_pup1.config(state=tkinter.DISABLED)
                self.gumb_pup2.config(state=tkinter.DISABLED)
                self.gumb_pup3.config(state=tkinter.DISABLED)
                self.gumb_pup4.config(state=tkinter.DISABLED)
        else:
            # Nismo v power up igri, izklopi gumbe
            self.gumb_pup1.config(state=tkinter.DISABLED)
            self.gumb_pup2.config(state=tkinter.DISABLED)
            self.gumb_pup3.config(state=tkinter.DISABLED)
            self.gumb_pup4.config(state=tkinter.DISABLED)

    def uredi_ime(self, ime):
        '''Metoda nam omeji dolžino imena igralca.'''
        text = ime.get()
        dolzina = 7 - min(2, max(text.lower().count('w'), min(1, text.lower().count('m'))))
        if len(text) > dolzina:
            ime.set(text[:dolzina])

    def zacni_igro(self, nova=False):
        '''Zacne novo/naslednjo igro. Nastavi igralce, tip igre, rezultat itd.'''
        self.prekini_igralce()
        
        # Preverimo, če želimo novo igro, v tem primeru rezultat
        # nastavimo na 0-0
        if nova:
            self.rezultat = [0, 0]

        # Dodamo igralce
        self.igralec_r = self.tipi_igralcev[self.tip_rdeci.get()]()
        self.igralec_y = self.tipi_igralcev[self.tip_rumeni.get()]()

        # Pobrišemo vse figure iz igralne površine        
        self.platno.delete(Gui.TAG_FIGURA)

        # Ustvarimo novo igro
        self.igra = self.tipi_iger[self.tip_igre.get()]()

        # Nastavimo aktivnost gumbov za 'power up'-e
        self.stanje_gumbov()

        if isinstance(self.igra, Five_logika):
            self.narisi_crtice()

        # Dodamo spremenljive elemente v platno_menu
        self.narisi_platno_menu()
        
        # Preverimo, kdo je na potezi
        if self.igra.na_potezi == IGRALEC_R:
            self.igralec_r.igraj()
        elif self.igra.na_potezi == IGRALEC_Y:
            self.igralec_y.igraj()

    def zapri_okno(self, master):
        '''Ta metoda se pokliče, ko uporabnik zapre aplikacijo.'''
        # Igralce najprej ustavimo
        self.prekini_igralce()

        # Zapremo okno
        master.destroy()


######################################################################
## Glavni program

# Glavnemu oknu rečemo "root" (koren), ker so grafični elementi
# organizirani v drevo, glavno okno pa je koren tega drevesa

# Ta pogojni stavek preveri, ali smo datoteko pognali kot glavni program in v tem primeru
# izvede kodo. (Načeloma bi lahko datoteko naložili z "import" iz kakšne druge in v tem
# primeru ne bi želeli pognati glavne kode. To je standardni idiom v Pythonu.)

if __name__ == '__main__':
    # Naredimo glavno okno in nastavimo ime
    root = tkinter.Tk()
    root.title('Stiri v vrsto')
    # Nastavimo najmanjšo velikost okna
    root.minsize(int(MIN_SIRINA), int(MIN_VISINA))
    # Nastavimo začetno velikost okna
    root.geometry('{0}x{1}'.format(int(0.9*MIN_SIRINA + 8*ZVP),
                                   int(7*ZVP)))

    # Naredimo objekt razreda Gui in ga spravimo v spremenljivko,
    # sicer bo Python mislil, da je objekt neuporabljen in ga bo pobrisal
    # iz pomnilnika.
    aplikacija = Gui(root)

    # Kontrolo prepustimo glavnemu oknu. Funkcija mainloop neha
    # delovati, ko okno zapremo.
    root.mainloop()
