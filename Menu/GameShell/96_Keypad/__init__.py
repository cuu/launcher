# -*- coding: utf-8 -*- 
import pygame
import validators
import commands
import pyudev

from UI.constants import Width,Height,ICON_TYPES
from UI.simple_name_space import SimpleNamespace
from UI.page  import Page
from UI.label  import Label
from UI.icon_item import IconItem
from UI.icon_pool import MyIconPool
from UI.keys_def  import CurKeys, IsKeyMenuOrB
from UI.skin_manager import MySkinManager
from UI.lang_manager import MyLangManager

class KeypadLabel(Label):
    _padding = 3 
    def Draw(self,bold=False):
        self._FontObj.set_bold(bold)
        my_text = self._FontObj.render(self._Text,True,self._Color)
        self._CanvasHWND.blit(my_text,(self._PosX,self._PosY,self._Width,self._Height))
        pygame.draw.rect(self._CanvasHWND,self._Color,(self._PosX-self._padding,self._PosY-self._padding,self._Width+self._padding*2,self._Height+self._padding*2),1)
 

class KeypadPage(Page):
    _FootMsg =  ["Nav","","","Back",""]
    _MyList = []
    
    _ListFontObj = MyLangManager.TrFont("varela15")
    
    _AList = {}
    _Labels = {}

    _Coords = {}
    
    _URLColor  = MySkinManager.GiveColor('URL')
    _TextColor = MySkinManager.GiveColor('Text')

    _KeyColors = [ MySkinManager.GiveColor('Text'),MySkinManager.GiveColor('URL')]

    _Scrolled = 0
    
    _PngSize = {}
    
    _DrawOnce = False
    _Scroller = None
    _Scrolled = 0
    _LastKey = CurKeys["Menu"]
    _TestKeys= {}
    _Quit  = 0

    def __init__(self):
        Page.__init__(self)
        self._Icons = {}

    def OnLoadCb(self):
        self._Scrolled = 0
        self._PosY = 0
        self.ResetTestKeys()

    def HandleUdev(self,action,device):
        if self._Screen._CurrentPage != self:
            return

        if action == "remove":
            if "ID_VENDOR_FROM_DATABASE" in device:
                if device["ID_VENDOR_FROM_DATABASE"].startswith("USB Design by Example"):
                    self._dev_state_info = "USB:0"
                    self.ResetTestKeys()
                    
                    self._Screen.Draw()
                    self._Screen.SwapAndShow()
        if action == "add":
            if "ID_VENDOR_FROM_DATABASE" in device:
                if device["ID_VENDOR_FROM_DATABASE"].startswith("USB Design by Example"):
                    self._dev_state_info = "USB:1"
                    self.ResetTestKeys()
                    self._Screen.Draw()
                    self._Screen.SwapAndShow()

    def Init(self):

        if self._Screen != None:
            if self._Screen._CanvasHWND != None and self._CanvasHWND == None:
                self._HWND = self._Screen._CanvasHWND
                self._CanvasHWND = pygame.Surface( (self._Screen._Width,self._Screen._Height) )
        
        self._PosX = self._Index*self._Screen._Width 
        self._Width = self._Screen._Width ## equal to screen width
        self._Height = self._Screen._Height
        
        self._dev_state_info = "USB:0"

        l = Label()
        l.SetCanvasHWND(self._CanvasHWND)

        l.Init(self._dev_state_info,self._ListFontObj)
        l.SetColor(self._TextColor)

        self._Labels["dev_state"] = l
        
        self._keylabels = \
                [#["Menu","1",self._ListFontObj,self._TextColor,[10,40]],
                 ["Up",  "4",self._ListFontObj,self._TextColor,[60,100]],
                 ["Down","5",self._ListFontObj,self._TextColor,[60,160]],
                 ["Left","6",self._ListFontObj,self._TextColor,[10,130]],
                 ["Right","7",self._ListFontObj,self._TextColor,[100,130]],
                 ["Backspace","1",self._ListFontObj,self._TextColor,[50,40]],
                 #["PLUS", "2",self._ListFontObj,self._TextColor,[135,40]],
                 #["MINUS","3",self._ListFontObj,self._TextColor,[170,40]],
                 ["Select","2",self._ListFontObj,self._TextColor,[222,40]],
                 ["Start", "3",self._ListFontObj,self._TextColor,[268,40]],
                 ["Y"    , "8",self._ListFontObj,self._TextColor,[230,100]],
                 ["A",     "9",self._ListFontObj,self._TextColor,[230,160]],
                 ["X",     "10",self._ListFontObj,self._TextColor,[180,130]],
                 ["B",     "11",self._ListFontObj,self._TextColor,[270,130]]
                ]
        
        for i in self._keylabels:
            l = KeypadLabel()
            l.SetCanvasHWND(self._CanvasHWND)
            l.Init(i[1],i[2])
            l.SetColor(i[3])
            l.NewCoord(i[4][0],i[4][1])
            self._Labels[ i[0] ] = l

        self._PyudevContext = pyudev.Context()

        for device in self._PyudevContext.list_devices(subsystem="usb"):
            if "ID_VENDOR_FROM_DATABASE" in device:
                if device["ID_VENDOR_FROM_DATABASE"].startswith("USB Design by Example"):
                    self._dev_state_info = "USB:1"


        monitor = pyudev.Monitor.from_netlink(self._PyudevContext)
        monitor.filter_by("usb")
        observer = pyudev.MonitorObserver(monitor,self.HandleUdev)
        observer.start()
        
        self.ResetTestKeys()

    def ResetTestKeys(self):
        self._TestKeys["Up"] = 0
        self._TestKeys["Down"] = 0
        self._TestKeys["Left"] = 0
        self._TestKeys["Right"] = 0
        #self._TestKeys["Menu"] = 0   ##ESC
        self._TestKeys["Select"] = 0
        self._TestKeys["Start"] = 0
        self._TestKeys["X"] = 0
        self._TestKeys["Y"] = 0
        self._TestKeys["A"] = 0
        self._TestKeys["B"] = 0
        #self._TestKeys["PLUS"] = 0 # shift+select
        #self._TestKeys["MINUS"] = 0 # shift + enter
        self._TestKeys["Backspace"] = 0 #shift+Menu
        
        self._Quit = 0
        self._LastKey = CurKeys["Menu"]

    def KeyDown(self,event):
        if event.key == CurKeys["Menu"]:
            if self._LastKey == event.key:
                self._Quit +=1
            else:
                self._Quit = 0

            if self._Quit > 4:
                self.ReturnToUpLevelPage()
                self._Screen.Draw()
                self._Screen.SwapAndShow()
            
            self._TestKeys["Menu"] = 1

        if event.key == CurKeys["X"]:
            self._TestKeys["X"] = 1
        if event.key == CurKeys["Y"]:
            self._TestKeys["Y"] = 1
        if event.key == CurKeys["A"]:
            self._TestKeys["A"] = 1

        if event.key == CurKeys["B"]:
            self._TestKeys["B"] = 1

        if event.key == CurKeys["Select"]:
            self._TestKeys["Select"] = 1

        if event.key == CurKeys["Start"]:
            self._TestKeys["Start"] = 1
    

        if event.key == pygame.K_KP_PLUS:
            self._TestKeys["PLUS"] = 1

        if event.key == pygame.K_KP_MINUS:
            self._TestKeys["MINUS"] = 1

        if event.key == pygame.K_BACKSPACE:
            self._TestKeys["Backspace"] = 1

        if event.key == CurKeys["Up"]:
            self._TestKeys["Up"] = 1

        if event.key == CurKeys["Down"]:
            self._TestKeys["Down"] = 1

        if event.key == CurKeys["Left"]:
            self._TestKeys["Left"] = 1

        if event.key == CurKeys["Right"]:
            self._TestKeys["Right"] = 1


        self._Screen.Draw()
        self._Screen.SwapAndShow()
        
        AllKeys = True

        for i in self._TestKeys:
            if self._TestKeys[i] == 0:
                AllKeys = False
                break

        if AllKeys == True:
            self._Screen._MsgBox.SetText("Keypad is OK")
            self._Screen._MsgBox.Draw()
            self._Screen.SwapAndShow()
        

        self._LastKey = event.key

    def DrawTestKeys(self):
        
        for i in self._Labels:
            if i in self._TestKeys:
                self._Labels[i].SetColor( self._KeyColors[self._TestKeys[i]] )

            self._Labels[i].Draw()
            
        #pygame.draw.rect(self._CanvasHWND,self._KeyColors[self._TestKeys["Menu"]],(18,40),15)

        #pygame.draw.circle(self._CanvasHWND,self._KeyColors[self._TestKeys[""]],(18,40),15)


        #pygame.draw.ellipse(self._CanvasHWND,self._URLColor,(10,50,50,20))

    def Draw(self):
        self.ClearCanvas()
        self._Labels["dev_state"].SetText(self._dev_state_info)
        self._Labels["dev_state"].NewCoord(10,10)
        self._Labels["dev_state"].Draw()

        self.DrawTestKeys()

        if self._HWND != None:
            self._HWND.fill(MySkinManager.GiveColor("White"))
            self._HWND.blit(self._CanvasHWND,(self._PosX,self._PosY,self._Width,self._Height))

        
class APIOBJ(object):

    _Page = None
    def __init__(self):
        pass
    def Init(self,main_screen):
        self._Page = KeypadPage()
        self._Page._Screen = main_screen
        self._Page._Name ="Keypad Tester"
        self._Page.Init()
        
    def API(self,main_screen):
        if main_screen !=None:
            main_screen.PushPage(self._Page)
            main_screen.Draw()
            main_screen.SwapAndShow()

OBJ = APIOBJ()
def Init(main_screen):    
    OBJ.Init(main_screen)
def API(main_screen):
    OBJ.API(main_screen)
    
        

