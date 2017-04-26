import tkinter # Uvozimo tkinter za uporabniški vmesnik
from math import sqrt
import random

from logika import *
from pop_logika import Pop_logika
from five_logika import Five_logika
from powerup_logika import Powerup_logika
from pop10_logika import Pop10_logika
from clovek import *
from racunalnik import *
from rand_algoritem import Rand_alg
from alphabeta import AlphaBeta

#########################
## UPORABNIŠKI VMESNIK ##
#########################

# Najboljše, če se ne spreminja preveč, ker izgleda najlepše pri teh številkah
# Če že spreminjaš, povečaj, ne zmanjšaj
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

    # Background barva za platno_menu
    BG_BARVA = 'black'

    # Visina in sirina platna z rezultatom itd.
    # ODSVETUJEM SPREMINJANJE
    VISINA_PLATNO_MENU = 0.55 * MIN_VISINA
    SIRINA_PLATNO_MENU = 0.8 * MIN_SIRINA - 3 * OKVIR

    def __init__(self, master):
        self.igralec_r = None # Objekt, ki igra rdeče krogce
        self.igralec_y = None # Objekt, ki igra rumene krogce
        self.igra = None # Objekt, ki predstavlja igro
        self.velikost_polja = ZVP # Velikost polja
        self.velikost_gap = self.velikost_polja / 20 # Razdalja med okvirjem in figuro
        self.rezultat = [0, 0] # Trenutni rezultat

        self.tip_rdeci = tkinter.IntVar() # Kakšen je rdeči, 0='človek',1='rac-rand',2='rac-easy',3='rac-med',4='rac-hard'
        self.tip_rumeni = tkinter.IntVar() # Kot pri rdečem

        self.tip = tkinter.IntVar() # Katero igro igramo - 0='4inarow',1='5inarow',2='popout',3='powerup'

        self.pup = tkinter.IntVar() # Kateri power up imamo izbran
        self.pup.set(0)
        self.pup_pomozni = 0 # Pomožni števec, ki bo povedal, kaj je bilo izbrano predhodno in bo omogočil 'odzbrati'

        # Slovar 'tipov' igralcev
        self.tip_igralca = {0: lambda: Clovek(self),
                               1: lambda: Racunalnik(self, Rand_alg()),
                               2: lambda: Racunalnik(self, AlphaBeta(2)),
                               3: lambda: Racunalnik(self, AlphaBeta(4)),
                               4: lambda: Racunalnik(self, AlphaBeta(6)),
                               5: lambda: Racunalnik(self, AlphaBeta(8))}

        # Slovar 'tipov' igre
        self.tip_igre = {0: lambda: Logika(),
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

        # Dodajmo slike za igro Power Up
        # OPOZORILO:
        # Pri spreminjanju velikosti menuja, je potrebno primerno prilagoditi tudi
        # velikost slik. Dimenziji sta izračunani po formuli:
        # dim ~ 0.125 * (0.8 * MIN_SIRINA - 3 * OKVIR)
        self.slika_pup_2x_nw = tkinter.PhotoImage(file='slike/2x-nw-icon.gif')
        self.slika_pup_2x_w = tkinter.PhotoImage(file='slike/2x-w-icon.gif')
        self.slika_pup_cross = tkinter.PhotoImage(file='slike/cross-icon.gif')
        self.slika_pup_stolpec = tkinter.PhotoImage(file='slike/stolpec-icon.gif')
        
        # Če uporabnik zapre okno, naj se pokliče self.zapri_okno
        master.protocol('WM_DELETE_WINDOW', lambda: self.zapri_okno(master))

        # Glavni menu
        menu = tkinter.Menu(master)
        master.config(menu=menu)

        # Podmenu "Igra"
        menu_igra = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Igra', menu=menu_igra)
        menu_igra.add_command(label='Nova igra',
                              command=lambda: self.zacni_igro(nova=True))
        menu_igra.add_command(label='Naslednja igra', command=self.naslednja_igra)
        menu_igra.add_separator()
        menu_igra.add_radiobutton(label='Štiri v vrsto',
                                  variable=self.tip, value=0,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_radiobutton(label='Pet v vrsto',
                                  variable=self.tip, value=1,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_radiobutton(label='Pop Out',
                                  variable=self.tip, value=2,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_radiobutton(label='Power Up',
                                  variable=self.tip, value=3,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_radiobutton(label='Pop 10',
                                  variable=self.tip, value=4,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_separator()
        menu_igra.add_command(label='Izhod',
                              command=lambda: self.zapri_okno(master))

        # Podmenu "Uredi"
        menu_uredi = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Uredi', menu=menu_uredi)
        menu_uredi.add_command(label='Razveljavi', command=self.platno_razveljavi)
        menu_uredi.add_command(label='Uveljavi', command=self.platno_uveljavi)

        # Podmenu "Rdeči"
        menu_rdeci = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Rdeči', menu=menu_rdeci)
        menu_rdeci.add_radiobutton(label='Človek',
                                   variable=self.tip_rdeci, value=0,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_separator()
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
        menu_rumeni.add_radiobutton(label='Človek',
                                   variable=self.tip_rumeni, value=0,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_separator()
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
        self.frame1 = tkinter.Frame(master,
                                    width=0.8 * MIN_SIRINA,
                                    height=MIN_VISINA,
                                    relief=tkinter.GROOVE,
                                    borderwidth=Gui.OKVIR,
                                    bg=Gui.BG_BARVA)
        self.frame1.pack(side=tkinter.LEFT, anchor=tkinter.NW)
        self.frame1.grid_propagate(0)

        # Narišemo platno
        self.platno_menu = tkinter.Canvas(self.frame1,
                                          width=Gui.SIRINA_PLATNO_MENU,
                                          height=Gui.VISINA_PLATNO_MENU)
        self.platno_menu.config(bg=Gui.BG_BARVA)
        self.platno_menu.grid(row=0, column=0, columnspan=4, sticky=tkinter.NW)

        # Dodamo možnosti
        self.gumb_nova_igra = tkinter.Button(self.frame1, text='Nova igra',
                                             width=int(0.4*MIN_SIRINA/7.25),
                                             command=lambda: self.zacni_igro(nova=True))
        self.gumb_nova_igra.grid(row=1, column=0, columnspan=4, pady=5)
        self.gumb_naslednja_igra = tkinter.Button(self.frame1, text='Naslednja igra',
                                                  width=int(0.4*MIN_SIRINA/7.25),
                                                  command=self.naslednja_igra)
        self.gumb_naslednja_igra.grid(row=2, column=0, columnspan=4, pady=(0,5))
        self.gumb_razveljavi = tkinter.Button(self.frame1, text='Razveljavi',
                                              width=int(0.4*MIN_SIRINA/7.25),
                                              command=self.platno_razveljavi)
        self.gumb_razveljavi.grid(row=3, column=0, columnspan=4, pady=5)
        self.gumb_uveljavi = tkinter.Button(self.frame1, text='Uveljavi',
                                            width=int(0.4*MIN_SIRINA/7.25),
                                            command=self.platno_uveljavi)
        self.gumb_uveljavi.grid(row=4, column=0, columnspan=4, pady=(0,5))
        # Ti gumbi so aktivni samo v primeru, da imamo 'Power Up' igro
        self.gumb_pup1 = tkinter.Radiobutton(self.frame1, text='Stolpec',
                                             variable=self.pup, value=1,
                                             command=self.odznaci_gumb)
        self.gumb_pup1.grid(row=5,column=0, pady=15)
        self.gumb_pup2 = tkinter.Radiobutton(self.frame1, text='Žeton',
                                             variable=self.pup, value=2,
                                             command=self.odznaci_gumb)
        self.gumb_pup2.grid(row=5,column=1, pady=15)
        self.gumb_pup3 = tkinter.Radiobutton(self.frame1, text='2x-NW',
                                             variable=self.pup, value=3,
                                             command=self.odznaci_gumb)
        self.gumb_pup3.grid(row=5,column=2,pady=15)
        self.gumb_pup4 = tkinter.Radiobutton(self.frame1, text='2x-W',
                                             variable=self.pup, value=4,
                                             command=self.odznaci_gumb)
        self.gumb_pup4.grid(row=5,column=3,pady=15)

        # Vsi ti gumbi za power upe na začetku niso aktivni, saj pričnemo z navadno 4 v vrsto
        self.gumb_pup1.config(state=tkinter.DISABLED)
        self.gumb_pup2.config(state=tkinter.DISABLED)
        self.gumb_pup3.config(state=tkinter.DISABLED)
        self.gumb_pup4.config(state=tkinter.DISABLED)

        # Gumb za izhod
        self.gumb_izhod = tkinter.Button(self.frame1, text='Izhod',
                                         width=int(0.3*0.8*MIN_SIRINA/7.25),
                                         command=lambda: self.zapri_okno(master))
        self.gumb_izhod.grid(row=6, column=0, columnspan=4, pady=(15,5))

        # Narišemo figure za platno_menu
        # Najprej nespremenljiv del
        dx = 0.15 * Gui.VISINA_PLATNO_MENU

        self.platno_ime_r = tkinter.Entry(master, fg='red', bg=Gui.BG_BARVA,
                                font=('Helvetica', '{0}'.format(int(Gui.VISINA_PLATNO_MENU/12)),
                                           'bold'),
                                width='10', borderwidth='0', justify='center',
                                textvariable=self.ime_r)
                                    
        self.platno_ime_y = tkinter.Entry(master, fg='yellow', bg=Gui.BG_BARVA,
                                font=('Helvetica', '{0}'.format(int(Gui.VISINA_PLATNO_MENU/12)),
                                           'bold'),
                                width='10', borderwidth='0', justify='center',
                                textvariable=self.ime_y)
        
        self.platno_menu.create_window(50+dx, 10, anchor=tkinter.N, window=self.platno_ime_r)
        
        self.platno_menu.create_window(Gui.SIRINA_PLATNO_MENU-50-dx, 10,
                                       anchor=tkinter.N, window=self.platno_ime_y)
        
        # Pričnemo igro
        self.zacni_igro(nova=True)

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
        self.platno_menu.delete(Gui.TAG_SPREMENLJIVI)
        dy = 5 * Gui.VISINA_PLATNO_MENU / 30
        dx = 0.15 * Gui.VISINA_PLATNO_MENU
        self.platno_menu.create_text(50+dx, 10+dy,
                                     text='{0}'.format(self.rezultat[0]),
                                     fill='white', anchor=tkinter.N,
                                     font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                           'bold'),
                                     tag=Gui.TAG_SPREMENLJIVI)
        self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU-50-dx, 10+dy,
                                     text='{0}'.format(self.rezultat[1]),
                                     fill='white', anchor=tkinter.N,
                                     font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                           'bold'),
                                     tag=Gui.TAG_SPREMENLJIVI)
        if zmagovalec==NEODLOCENO:
            # Izid je neodločen
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 2.5*dy,
                                         text='Konec igre!',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 3.5*dy,
                                         text='Izid je:',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 4.5*dy,
                                         text='NEODLOČEN',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
        elif zmagovalec:
            # Imamo zmagovalca
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 2.5*dy,
                                         text='Konec igre!',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 3.5*dy,
                                         text='Zmagovalec je:',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 4.5*dy,
                                         text='{0}'.format('RDEČI' if zmagovalec==IGRALEC_R else 'RUMENI'),
                                         fill='{0}'.format('red' if zmagovalec==IGRALEC_R else 'yellow'), anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
        else:
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 2.5*dy,
                                         text='Na potezi je',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_oval(Gui.SIRINA_PLATNO_MENU / 2 - 0.75*dy, 10 + 3.75*dy,
                                         Gui.SIRINA_PLATNO_MENU / 2 + 0.75*dy, 10 + 5.25*dy,
                                         fill='{0}'.format('red' if self.igra.na_potezi==IGRALEC_R else 'yellow'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            if isinstance(self.igra, Powerup_logika):
                # Dodati moramo power upe
                pup_r = self.igra.powerups[0] # Power ups za rdečega
                pup_y = self.igra.powerups[1] # Power ups za rumenega
                stranica = Gui.SIRINA_PLATNO_MENU * 0.75 / 6
                # Za rdečega igralca
                if pup_r[0] > 0:
                    self.platno_menu.create_image(10, Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_stolpec,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)
                if pup_r[1] > 0:
                    self.platno_menu.create_oval(10, Gui.VISINA_PLATNO_MENU / 2,
                                                      10 + stranica,
                                                      Gui.VISINA_PLATNO_MENU / 2 + stranica,
                                                      fill='yellow', tag=Gui.TAG_SPREMENLJIVI)
                    self.platno_menu.create_image(10, Gui.VISINA_PLATNO_MENU / 2,
                                                  image=self.slika_pup_cross,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)
                if pup_r[2] > 0:
                    self.platno_menu.create_image(10, 2 * Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_2x_nw,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)
                if pup_r[3] > 0:
                    self.platno_menu.create_image(10, 5 * Gui.VISINA_PLATNO_MENU / 6,
                                                  image=self.slika_pup_2x_w,
                                                  anchor=tkinter.NW, tag=Gui.TAG_SPREMENLJIVI)

                # Za rumenega igralca
                if pup_y[0] > 0:
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - 10, Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_stolpec,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
                if pup_y[1] > 0:
                    self.platno_menu.create_oval(Gui.SIRINA_PLATNO_MENU - 10, Gui.VISINA_PLATNO_MENU / 2,
                                                      Gui.SIRINA_PLATNO_MENU - 10 - stranica,
                                                      Gui.VISINA_PLATNO_MENU / 2 + stranica,
                                                      fill='red', tag=Gui.TAG_SPREMENLJIVI)
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - 10, Gui.VISINA_PLATNO_MENU / 2,
                                                  image=self.slika_pup_cross,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
                if pup_y[2] > 0:
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - 10, 2 * Gui.VISINA_PLATNO_MENU / 3,
                                                  image=self.slika_pup_2x_nw,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
                if pup_y[3] > 0:
                    self.platno_menu.create_image(Gui.SIRINA_PLATNO_MENU - 10, 5 * Gui.VISINA_PLATNO_MENU / 6,
                                                  image=self.slika_pup_2x_w,
                                                  anchor=tkinter.NE, tag=Gui.TAG_SPREMENLJIVI)
            elif isinstance(self.igra, Pop10_logika):
                # Dodajmo grafični prikaz odstranjenih žetonov
                premer = Gui.SIRINA_PLATNO_MENU * 0.7 / 6
                # Za rdečega igralca
                self.platno_menu.create_oval(20, 15 + 2.5*dy,
                                             20 + premer, 15 + 2.5*dy + premer,
                                             fill='red', tag=Gui.TAG_SPREMENLJIVI)
                self.platno_menu.create_text(20 + premer / 2, 15 + 2.5*dy + premer / 2,
                                             text='{0}'.format(self.igra.odstranjeni[0]),
                                             fill='white', anchor=tkinter.CENTER,
                                             font=('Helvetica', '{0}'.format(int(Gui.VISINA_PLATNO_MENU/15)),
                                                   'bold'),
                                             tag=Gui.TAG_SPREMENLJIVI)

                # Za rumenega igralca
                self.platno_menu.create_oval(Gui.SIRINA_PLATNO_MENU - 20, 15 + 2.5*dy,
                                             Gui.SIRINA_PLATNO_MENU - 20 - premer, 15 + 2.5*dy + premer,
                                             fill='yellow', tag=Gui.TAG_SPREMENLJIVI)
                self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU - 20 - premer / 2,
                                             15 + 2.5*dy + premer / 2,
                                             text='{0}'.format(self.igra.odstranjeni[1]),
                                             fill='black', anchor=tkinter.CENTER,
                                             font=('Helvetica', '{0}'.format(int(Gui.VISINA_PLATNO_MENU/15)),
                                                   'bold'),
                                             tag=Gui.TAG_SPREMENLJIVI)
                if self.igra.faza == 1:
                    self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.VISINA_PLATNO_MENU,
                                                 text='Odstranite žeton!', fill='white',
                                                 anchor=tkinter.S,
                                                 font=('Helvetica',
                                                       '{0}'.format(int(Gui.VISINA_PLATNO_MENU/20)),
                                                       'bold'),
                                                 tag=Gui.TAG_SPREMENLJIVI)
                elif self.igra.faza == 2:
                    self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, Gui.VISINA_PLATNO_MENU,
                                                 text='Vstavite žeton!', fill='white',
                                                 anchor=tkinter.S,
                                                 font=('Helvetica',
                                                       '{0}'.format(int(Gui.VISINA_PLATNO_MENU/20)),
                                                       'bold'),
                                                 tag=Gui.TAG_SPREMENLJIVI)
                                             

    def narisi_polozaj(self, polozaj): # Premisli, če rabiš polozaj
        for (i, a) in enumerate(polozaj):
            for (j, b) in enumerate(a):
                if b == IGRALEC_R:
                    self.narisi_R((i,j))
                elif b == IGRALEC_Y:
                    self.narisi_Y((i,j))

        if isinstance(self.igra, Five_logika):
            self.narisi_crtice()

    def narisi_crtice(self):
        # Pomožne črte za 5 v vrsto
        d = self.velikost_polja
        for i in range(6):
            barva1 = 'yellow' if i%2 == 0 else 'red'
            barva2 = 'red' if i%2 == 0 else 'yellow'
            self.platno.create_line(d/4, d/2 + d/4 + i*d,
                                    d/4, d/2 + 3*d/4 + i*d,
                                    tag=Gui.TAG_FIGURA,
                                    fill=barva1,
                                    width=5)
            self.platno.create_line(8*d - d/4, d/2 + d/4 + i*d,
                                    8*d - d/4, d/2 + 3*d/4 + i*d,
                                    tag=Gui.TAG_FIGURA,
                                    fill=barva2,
                                    width=5)

    def narisi_Y(self, p):
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

    def nova_igra(self):
        self.rezultat = [0, 0]
        self.zacni_igro()

    def obkrozi(self, stirke):
        d = self.velikost_polja
        w = 5 # Odsvetujem spreminjanje (namenoma je fiksna vrednost)
        for stirka in stirke: # Gremo po vseh štirkah
            (i1,j1) = stirka[0]
            (i2,j2) = stirka[-1]
            if (i1 == i2) or (j1 == j2):
                x1 = d/2 + i1*d
                y1 = 13*d/2 - j1*d
                x2 = d/2 + (i2+1)*d
                y2 = 13*d/2 - (j2+1)*d
                self.platno.create_rectangle(x1, y1, x2, y2,
                                             width=w,
                                             tag=Gui.TAG_FIGURA)
            else: # Diagonalni - popravi jih še v kotih
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
        (x,y) = (event.x, event.y)
        d = self.velikost_polja
        if (x < d/2) or (x >= 15*d/2) or (y < d/2) or (y >= 13*d/2):
            # V tem primeru smo zunaj igralnega območja
            pass
        else:
            i = int((x - d/2) // d) + 1
            j = 5 - int((y - d/2) // d)
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
                    i = i + j*7
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
                # Gremo 2 potezi nazaj
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
                # Gremo 2 potezi nazaj
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
            novo_stanje = self.igra.razveljavi()

        if novo_stanje: # Uspešno smo razveljavili potezo
            # Pobrišemo vse figure iz igralne površine        
            self.platno.delete(Gui.TAG_FIGURA)

            # Narišemo novi (trenutni) položaj
            self.narisi_polozaj(novo_stanje[0])

            # Posodobimo stanje gumbov za powerupe
            self.stanje_gumbov()

            # Popravimo napis nad igralno površino
            self.narisi_platno_menu()
            if self.igra.na_potezi == IGRALEC_R:
                self.igralec_r.igraj()
            elif self.igra.na_potezi == IGRALEC_Y:
                self.igralec_y.igraj()
        else:
            # Smo na začetku 'zgodovine' (igre)
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
                prihodnost = self.igra.zgodovina[self.igra.stevec+1:] + [self.igra.zadnja]
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
                prihodnost = self.igra.zgodovina[self.igra.stevec+1:] + [self.igra.zadnja]
                for prih in prihodnost:
                    koliko_naprej += 1
                    if prih[1] == IGRALEC_Y:
                        break
                novo_stanje = self.igra.uveljavi(koliko_naprej)
        else:
            novo_stanje = self.igra.uveljavi()


        if novo_stanje: # Uspešno smo uveljavili potezo
            # Pobrišemo vse figure iz igralne površine
            self.platno.delete(Gui.TAG_FIGURA)

            # Narišemo novi (trenutni) položaj
            self.narisi_polozaj(novo_stanje[0])

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
            # Smo na koncu 'zgodovine' (igre)
            pass
    
    def povleci_potezo(self, p):
        igralec = self.igra.na_potezi
        if isinstance(p, list):
            # Imamo dvojno potezo, ki jo je povlekel računalnik
            t1 = self.igra.povleci_potezo(p[0])
            t2 = self.igra.povleci_potezo(p[1])
            if (t1 is None) or (t2 is None):
                # Imamo neveljavno potezo
                # To se sicer računalniku ne bi smelo nikoli zgoditi
                pass
            else:
                (zmagovalec1, stirka1, p1, osvezi1) = t1
                (zmagovalec2, stirka2, p2, osvezi2) = t2
                if osvezi1 or osvezi2:
                    # Pri prvi ali drugi potezi se je brisalo žetone, zato je potrebno
                    # grafični prikaz igralne površine osvežiti.
                    # S tem pravilno prikažemo tudi še potencialno ne-narisane žetone
                    self.platno.delete(Gui.TAG_FIGURA)
                    self.narisi_polozaj(self.igra.polozaj)
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
            t = self.igra.povleci_potezo(p)
            if t is None:
                # Poteza ni bila veljavna
                pass
            else:
                if self.pup.get() > 0:
                    # Če imamo izbran kak power up, ga po tem,
                    # ko povlečemo potezo, unselectamo
                    self.pup.set(0)
                    self.pup_pomozni = 0
                self.stanje_gumbov()
                (zmagovalec, stirka, p1, osvezi) = t # Tukaj je p1 položaj na platnu
                if osvezi:
                    self.platno.delete(Gui.TAG_FIGURA)
                    self.narisi_polozaj(self.igra.polozaj)
                elif isinstance(self.igra, Pop10_logika) and self.igra.faza == 0:
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
        self.platno.delete('all')
        (w,h) = (event.width, event.height)
        self.velikost_polja = min(w / 8, h / 7)
        self.velikost_gap = self.velikost_polja / 20
        self.platno.config(width=w-0.9*MIN_SIRINA, height=h-200)
        self.narisi_okvir()
        self.narisi_polozaj(self.igra.polozaj)
        if self.igra.na_potezi is None:
            (zmagovalec, stirka) = self.igra.stanje_igre()
            self.koncaj_igro(zmagovalec, stirka)

    def stanje_gumbov(self, indikator=0):
        '''Vklopi gumbe za power upe, če smo v pravi igri, sicer jih izklopi.'''
        # Če je indikator = 1, smo v igro prišli preko trace metode, torej se je zamenjal tip igre
        # To se uporablja, ker bi drugače želeli dobiti self.igra.powerups, še preden bi bili v pravilni igri
        tip = self.tip.get()
        if tip == 3:
            # Imamo power up igro, vklopi gumbe
            if self.igra.na_potezi is not None:
                if indikator == 0:
                    kateri_igr = 0 if self.igra.na_potezi == IGRALEC_R else 1 # Nam pove, kateri seznam powerupov gledamo
                    if self.igra.powerups[kateri_igr][0]:
                        self.gumb_pup1.config(state=tkinter.NORMAL)
                    else:
                        self.gumb_pup1.config(state=tkinter.DISABLED)
                    if self.igra.powerups[kateri_igr][1]:
                        self.gumb_pup2.config(state=tkinter.NORMAL)
                    else:
                        self.gumb_pup2.config(state=tkinter.DISABLED)
                    if self.igra.powerups[kateri_igr][2]:
                        self.gumb_pup3.config(state=tkinter.NORMAL)
                    else:
                        self.gumb_pup3.config(state=tkinter.DISABLED)
                    if self.igra.powerups[kateri_igr][3]:
                        self.gumb_pup4.config(state=tkinter.NORMAL)
                    else:
                        self.gumb_pup4.config(state=tkinter.DISABLED)
                else:
                    self.gumb_pup1.config(state=tkinter.NORMAL)
                    self.gumb_pup2.config(state=tkinter.NORMAL)
                    self.gumb_pup3.config(state=tkinter.NORMAL)
                    self.gumb_pup4.config(state=tkinter.NORMAL)
            else:
                self.gumb_pup1.config(state=tkinter.DISABLED)
                self.gumb_pup2.config(state=tkinter.DISABLED)
                self.gumb_pup3.config(state=tkinter.DISABLED)
                self.gumb_pup4.config(state=tkinter.DISABLED)
        else:
            # Izklopi gumbe
            self.gumb_pup1.config(state=tkinter.DISABLED)
            self.gumb_pup2.config(state=tkinter.DISABLED)
            self.gumb_pup3.config(state=tkinter.DISABLED)
            self.gumb_pup4.config(state=tkinter.DISABLED)

    def uredi_ime(self, ime):
        text = ime.get()
        dolzina = 7 - min(2, max(text.lower().count('w'), min(1, text.lower().count('m'))))
        if len(text) > dolzina:
            ime.set(text[:dolzina])

    def zacni_igro(self, nova=False):
        '''Zacne novo igro. Torej zaenkrat le pobriše vse dosedanje poteze.'''
        self.prekini_igralce()
        
        # Preverimo, če želimo novo igro, v tem primeru rezultat
        # nastavimo na 0-0
        if nova:
            self.rezultat = [0, 0]

        # Dodamo igralce
        self.igralec_r = self.tip_igralca[self.tip_rdeci.get()]()
        self.igralec_y = self.tip_igralca[self.tip_rumeni.get()]()

        # Pobrišemo vse figure iz igralne površine        
        self.platno.delete(Gui.TAG_FIGURA)

        # Ustvarimo novo igro
        self.igra = self.tip_igre[self.tip.get()]()

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
    root.minsize(int(MIN_SIRINA), MIN_VISINA)
    root.geometry('{0}x{1}'.format(int(0.9*MIN_SIRINA + 8*ZVP),
                                   int(7*ZVP)))

    # Naredimo objekt razreda Gui in ga spravimo v spremenljivko,
    # sicer bo Python mislil, da je objekt neuporabljen in ga bo pobrisal
    # iz pomnilnika.
    aplikacija = Gui(root)

    # Kontrolo prepustimo glavnemu oknu. Funkcija mainloop neha
    # delovati, ko okno zapremo.
    root.mainloop()
