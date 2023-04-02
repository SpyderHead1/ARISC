from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', False)

import threading
import os
import zipfile
import json
import random
import gc
import tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import filedialog
from win32api import GetSystemMetrics

import kivy
kivy.require('2.1.0')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.core.window import Window

import Custom

ARISConfigurator_version = '3.01'

MainBgColor = '#202020FF' # RGBA color code
MainLabelTextSize = 16
MainLabelHeight = 25
MainLabelHalign = 'left'
MainLabelValign = 'middle'
MainButtonHeight = 50
MainConfigLayoutGridWidth = 210 # Default width of the grid layout used in the config section
MainConfigLayoutGridHeight = 50 # Default height of the grid layout used in the config section
MainGridPadding = 20 # Default grid padding
DashboardWidth = 960 # Width of the dashboard (for the preview)
DashboardHeight = 544 # Height of the dashboard (for the preview)
PreviewSize = 75 # Preview size in %
ErrorColor = '#FF3030FF' # RGBA color code
WarningColor = '#FFA000FF' # RGBA color code
OkColor = '#00A000FF' # RGBA color code
MessageColor = '#FFFFFFFF' # RGBA color code

DevelopMode = False
DebugMode = False
VisualDesignHints = False

# Define Window size
Window.size = (int((3 * MainConfigLayoutGridWidth) + (5 * MainGridPadding) + ((DashboardWidth / 100) * PreviewSize)), 950)
Window.minimum_width, Window.minimum_height = Window.size
Window.maximum_width, Window.maximum_height = Window.size
if (GetSystemMetrics(0) >= Window.size[0]) and (GetSystemMetrics(1) >= Window.size[1]):
    # if screen resolution is higher than the size of the window place it in the middle of the screen
    Window.left = (GetSystemMetrics(0) / 2) - (Window.size[0] / 2)
    Window.top = (GetSystemMetrics(1) / 2) - (Window.size[1] / 2)
else:
    # otherwise place it on top left corner
    Window.left = 20
    Window.top = 50

if not DevelopMode:
    # if development mode is off take current work directory as ARIS folder
    DebugMode = False
    VisualDesignHints = False
    ARIS_folder = os.path.abspath(os.path.join(os.path.dirname(os.getcwd())))
else:
    # otherwise set fix path
    ARIS_folder = 'V:\\Daten\Documents\\Python\\ARIS V3\\Develop'
    Custom.DebugPrint(DebugMode, 'Window size: ' + str(Window.size[0]) + 'x' + str(Window.size[1]))

Custom.DebugPrint(DebugMode, 'Startup - ARIS folder: ' + str(ARIS_folder))


class ArisConfiguratorApp(App):
    
    def __init__(self, **kwargs):
        super(ArisConfiguratorApp, self).__init__(**kwargs)
        # other init things here


    def build(self):
        # set icon for main kivy window
        # make a tkinter object, set the icon and destroy the object
        #   --> the tkinter object is just temporarily needed to set an individual icon for the filedialog (as this is the only tkinter class used)
        root = tk.Tk()
        if not DevelopMode:
            self.icon = 'logo.png'
            root.iconbitmap(default='icon.ico')
        else:
            self.icon = ARIS_folder + '\\logo.png'
            root.iconbitmap(default= ARIS_folder + '\\icon.ico')
        root.destroy()

        # init variables
        self.Page = 1
        self.ButtonsBlockedRestore = False
        self.ButtonsBlockedBackup = False
        self.UnsavedChanges = False
        self.RestoringBackup = False
        self.LoadingDefaults = False
        self.MainStatusUpdateCounter = 0
        self.PreviewStatusUpdateCounter = 0
        self.PreviewUpdateBackgroundCounter = 0
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewUpdateRpmCounter = 0
        self.PreviewUpdateLapDeltaCounter = 0
        self.PreviewUpdateTcCounter = 0
        self.PreviewUpdateAbsCounter = 0
        self.PreviewRpmColor1 = '#00000000'
        self.PreviewRpmColor2 = '#00000000'
        self.PreviewRpmColor3 = '#00000000'
        self.PreviewRpmColor4 = '#00000000'
        self.PreviewRpmColor5 = '#00000000'
        self.PreviewRpmColor6 = '#00000000'
        self.PreviewRpmColor7 = '#00000000'
        self.PreviewRpmColor8 = '#00000000'
        self.PreviewRpmColor9 = '#00000000'
        self.PreviewRpmColor10 = '#00000000'
        self.PreviewRpmColorLinearGauge = '#00000000'
        self.PreviewBackgroundBlink = 0 # 0 = do not show background flag, 1 = no blinking, 2 = slow blinking, 3 = fast blinking
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        # read config files
        self.Config = ConfigFile
        self.Config.read(self.Config)

        # set window title
        self.title = 'ARIS Configurator v' + ARISConfigurator_version
        ##########################################################################################
        #                                                                                        #
        # Main layout                                                                            #
        #                                                                                        #
        ##########################################################################################
        # define main layout and put a (colored) background on it
        self.Main_Layout = FloatLayout(size = Window.size)
        self.MainBackground = Custom.ColoredCanvas()
        self.Main_Layout.add_widget(self.MainBackground)
        self.MainBackground.DrawRectangle(Color=get_color_from_hex(MainBgColor))
        
        self.MainTitle_Label = Label(   text = 'ARIS Configurator',
                                        font_size = 24,
                                        bold = True,
                                        size_hint_y = None,
                                        height = '48dp')
        self.MainTitle_Label.pos[1] = Window.size[1] - self.MainTitle_Label.height

        self.MainFooter_Label = Label(  text = 'ARIS Configurator v' + ARISConfigurator_version + ' - 2022 SpyderHead',
                                        font_size = 14,
                                        bold = False,
                                        halign = 'center',
                                        size_hint_y = None,
                                        height = 30)

        self.AcMain_Layout = GridLayout(    cols = 2,
                                            padding = [MainGridPadding, MainGridPadding, MainGridPadding, MainGridPadding])
        self.AcMain_Layout.pos[1] = 0 - self.MainTitle_Label.height
        
        self.LeftSideMain_Layout = GridLayout(  cols = 1)

        self.LeftSidePageButtons_Layout = GridLayout(   cols = 4,
                                                        size_hint_y = None,
                                                        height = MainButtonHeight + 20,
                                                        spacing = [10, 0],
                                                        padding = [20, 0])

        self.LeftSide_Layout = GridLayout(  cols = 1)

        self.RightSide_Layout = GridLayout( cols = 1,
                                            size_hint_x = None,
                                            width = ((DashboardWidth / 100 ) * PreviewSize))

        self.ConfigPageDesign1_Layout = GridLayout(  cols = 3,
                                                    spacing = [20, 25],
                                                    size_hint_y = None)
        self.ConfigPageDesign1_Layout.height = (4 * MainConfigLayoutGridHeight) + (4.5 * self.ConfigPageDesign1_Layout.spacing[1])
        self.ConfigPageDesign1_Layout.width = Window.size[0] - self.RightSide_Layout.width - (2 * MainGridPadding)
        self.ConfigPageDesign1_Layout.pos[1] = Window.size[1] - self.ConfigPageDesign1_Layout.height

        self.ConfigPageDesign2_Layout = GridLayout( cols = 1,
                                                    spacing = [20, 25],
                                                    size_hint_y = None)
        self.ConfigPageDesign1_Layout.width = Window.size[0] - self.RightSide_Layout.width - (2 * MainGridPadding)
        self.ConfigPageDesign1_Layout.pos[1] = Window.size[1] - self.ConfigPageDesign1_Layout.height

        self.ConfigPageFunctions1_Layout = GridLayout(  cols = 1,
                                                        spacing = [20, 0])

        ##########################################################################################
        #                                                                                        #
        # Page switch buttons                                                                    #
        #                                                                                        #
        ##########################################################################################

        self.Page1_Button = Button( text = 'Look',
                                    height = MainButtonHeight / 1.4,
                                    width = 150,
                                    halign = 'center',
                                    size_hint = [None, None],
                                    markup = True,
                                    background_color = (0.55, 0.55, 0.95, 1.0))
        self.Page1_Button.bind(on_press = self.Page1ButtonClicked)
        self.LeftSidePageButtons_Layout.add_widget(self.Page1_Button)

        self.Page2_Button = Button( text = 'Functionality',
                                    height = MainButtonHeight / 1.4,
                                    width = 150,
                                    halign = 'center',
                                    size_hint = [None, None],
                                    markup = True,
                                    background_color = (0.55, 0.55, 0.55, 1.0))
        self.Page2_Button.bind(on_press = self.Page2ButtonClicked)
        self.LeftSidePageButtons_Layout.add_widget(self.Page2_Button)

        self.Page3_Button = Button( text = 'N/A',
                                    height = MainButtonHeight / 1.4,
                                    width = 150,
                                    halign = 'center',
                                    size_hint = [None, None],
                                    markup = True,
                                    background_color = (0.55, 0.55, 0.55, 1.0))
        self.Page3_Button.bind(on_press = self.Page3ButtonClicked)
        # not needed at the moment -- self.LeftSidePageButtons_Layout.add_widget(self.Page3_Button)

        self.Page4_Button = Button( text = 'N/A',
                                    height = MainButtonHeight / 1.4,
                                    width = 150,
                                    halign = 'center',
                                    size_hint = [None, None],
                                    markup = True,
                                    background_color = (0.55, 0.55, 0.55, 1.0))
        self.Page4_Button.bind(on_press = self.Page4ButtonClicked)
        # not needed at the moment -- self.LeftSidePageButtons_Layout.add_widget(self.Page4_Button)

        ##########################################################################################
        #                                                                                        #
        # Spinner for RPM setting                                                                #
        #                                                                                        #
        ##########################################################################################
        
        self.RpmType_Layout = GridLayout(   cols = 1,
                                            height = MainConfigLayoutGridHeight,
                                            width = MainConfigLayoutGridWidth,
                                            size_hint = [None, None])
                                                
        self.RpmType_Label = Label( text = 'RPM display type',
                                    halign = MainLabelHalign,
                                    valign = MainLabelValign,
                                    height = MainLabelHeight,
                                    font_size = MainLabelTextSize,
                                    size_hint_y = None)
        self.RpmType_Label.bind(size = self.RpmType_Label.setter('text_size'))
        self.RpmType_Spinner = Spinner( text = self.Config.ActRpmType,
                                        values = self.Config.ActRpmTypeElements,
                                        height = MainButtonHeight,
                                        bold = True,
                                        font_size = 17,
                                        size_hint_y = None,
                                        halign = 'center')
        self.RpmType_Layout.add_widget(self.RpmType_Label)
        self.RpmType_Layout.add_widget(self.RpmType_Spinner)
        self.RpmType_Spinner.bind(text = self.RpmTypeDropdownClicked)

        self.RpmDirection_Layout = GridLayout(  cols = 1,
                                                height = MainConfigLayoutGridHeight,
                                                width = MainConfigLayoutGridWidth,
                                                size_hint = [None, None])
        self.RpmDirection_Label = Label(    text = 'Direction of RPM elements',
                                            halign = MainLabelHalign,
                                            valign = MainLabelValign,
                                            height = MainLabelHeight,
                                            font_size = MainLabelTextSize,
                                            size_hint_y = None)
        self.RpmDirection_Label.bind(size = self.RpmDirection_Label.setter('text_size'))
        self.RpmDefaultDirection_Spinner = Spinner( text = self.Config.ActRpmDirectionDefault,
                                                    values = self.Config.ActRpmDirectionElementsDefault,
                                                    height = MainButtonHeight,
                                                    bold = True,
                                                    font_size = 17,
                                                    size_hint_y = None,
                                                    halign = 'center',
                                                    text_autoupdate = True)
        self.RpmGaugeDirection_Spinner = Spinner(   text = self.Config.ActRpmDirectionGauge,
                                                    values = self.Config.ActRpmDirectionElementsGauge,
                                                    height = MainButtonHeight,
                                                    bold = True,
                                                    font_size = 17,
                                                    size_hint_y = None,
                                                    halign = 'center',
                                                    text_autoupdate = True)
        self.RpmDirection_Layout.add_widget(self.RpmDirection_Label)
        if ((self.Config.ActRpmType == 'angular elements') or (self.Config.ActRpmType == 'round elements')):
            self.RpmDirection_Layout.add_widget(self.RpmDefaultDirection_Spinner)
            self.RpmDefaultDirection_Spinner.bind(text = self.RpmDirectionDropdownClicked)
        else:
            self.RpmDirection_Layout.add_widget(self.RpmGaugeDirection_Spinner)
            self.RpmGaugeDirection_Spinner.bind(text = self.RpmDirectionDropdownClicked)
        

        self.RedlineType_Layout = GridLayout(   cols = 1,
                                                height = MainConfigLayoutGridHeight,
                                                width = MainConfigLayoutGridWidth,
                                                size_hint = [None, None])
        self.RedlineType_Label = Label( text = 'Redline indicator type',
                                        halign = MainLabelHalign,
                                        valign = MainLabelValign,
                                        height = MainLabelHeight,
                                        font_size = MainLabelTextSize,
                                        size_hint_y = None)
        self.RedlineType_Label.bind(size = self.RedlineType_Label.setter('text_size'))
        self.RedlineType_Spinner = Spinner( text = self.Config.ActRedlineType,
                                            values = self.Config.ActRedlineTypeElements,
                                            height = MainButtonHeight,
                                            bold = True,
                                            font_size = 17,
                                            size_hint_y = None,
                                            halign = 'center')
        self.RedlineType_Layout.add_widget(self.RedlineType_Label)
        self.RedlineType_Layout.add_widget(self.RedlineType_Spinner)
        self.RedlineType_Spinner.bind(text = self.RedlineTypeDropdownClicked)

        
        self.ConfigPageDesign1_Layout.add_widget(self.RpmType_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.RpmDirection_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.RedlineType_Layout)

        ##########################################################################################
        #                                                                                        #
        # Colors                                                                                 #
        #                                                                                        #
        ##########################################################################################
        
        # define layouts for the color chooser object
        # color chooser object is then placed in Reload() method
        self.MainBgColor_Layout = GridLayout(   cols = 1,
                                                height = MainConfigLayoutGridHeight,
                                                width = MainConfigLayoutGridWidth,
                                                size_hint = [None, None])

        self.SeperatorColor_Layout = GridLayout(    cols = 1,
                                                    height = MainConfigLayoutGridHeight,
                                                    width = MainConfigLayoutGridWidth,
                                                    size_hint = [None, None])

        self.MainTextColor_Layout = GridLayout(     cols = 1,
                                                    height = MainConfigLayoutGridHeight,
                                                    width = MainConfigLayoutGridWidth,
                                                    size_hint = [None, None])

        self.TitleTextColor_Layout = GridLayout(    cols = 1,
                                                    height = MainConfigLayoutGridHeight,
                                                    width = MainConfigLayoutGridWidth,
                                                    size_hint = [None, None])

        self.GearTextColor_Layout = GridLayout( cols = 1,
                                                height = MainConfigLayoutGridHeight,
                                                width = MainConfigLayoutGridWidth,
                                                size_hint = [None, None])

        self.TcColor_Layout = GridLayout(   cols = 1,
                                            height = MainConfigLayoutGridHeight,
                                            width = MainConfigLayoutGridWidth,
                                            size_hint = [None, None])

        self.AbsColor_Layout = GridLayout(  cols = 1,
                                            height = MainConfigLayoutGridHeight,
                                            width = MainConfigLayoutGridWidth,
                                            size_hint = [None, None])
        
        self.PersonalBestColor_Layout = GridLayout( cols = 1,
                                                    height = MainConfigLayoutGridHeight,
                                                    width = MainConfigLayoutGridWidth,
                                                    size_hint = [None, None])

        self.SessionBestColor_Layout = GridLayout(  cols = 1,
                                                    height = MainConfigLayoutGridHeight,
                                                    width = MainConfigLayoutGridWidth,
                                                    size_hint = [None, None])

        ##########################################################################################

        self.ConfigPageDesign1_Layout.add_widget(self.MainBgColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.SeperatorColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.MainTextColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.TitleTextColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.GearTextColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.PersonalBestColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.TcColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.AbsColor_Layout)
        self.ConfigPageDesign1_Layout.add_widget(self.SessionBestColor_Layout)
        
        ##########################################################################################
        #                                                                                        #
        # Border radius slider                                                                   #
        #                                                                                        #
        ##########################################################################################
        
        self.BorderRadius_Layout = GridLayout(  cols = 2,
                                                padding = [0, 0],
                                                height = MainConfigLayoutGridHeight / 2,
                                                width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                size_hint = [None, None])

        self.BorderRadiusSlider_Layout = GridLayout(    cols = 1,
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        width = (2 * MainConfigLayoutGridWidth),
                                                        size_hint = [None, None])
        
        self.BorderRadiusDescription_Label = Label( text = 'Corner radius for borders: ' + str(self.Config.ActBorderRadius),
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    font_size = MainLabelTextSize,
                                                    size_hint_y = None)
        self.BorderRadiusDescription_Label.bind(size = self.BorderRadiusDescription_Label.setter('text_size'))
        
        self.BorderRadius_Slider = Slider(  min = 0,
                                            max = 20,
                                            step = 1,
                                            height = MainConfigLayoutGridHeight / 2,
                                            width =  (2 * MainConfigLayoutGridWidth) + (1 * MainGridPadding),
                                            size_hint = [None, None],
                                            value = self.Config.ActBorderRadius)
        self.BorderRadius_Slider.bind(value = self.BorderRadiusSliderChange)

        ##########################################################################################
        
        self.BorderRadius_Layout.add_widget(self.BorderRadiusDescription_Label)
        self.BorderRadius_Layout.add_widget(self.BorderRadius_Slider)

        self.ConfigPageDesign2_Layout.add_widget(self.BorderRadius_Layout)

        ##########################################################################################
        #                                                                                        #
        # Background image                                                                       #
        #                                                                                        #
        ##########################################################################################
        
        self.BackgroundImageActive_Layout = GridLayout( cols = 3,
                                                        padding = [-5, -20],
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                        size_hint = [None, None])
        
        self.BackgroundImageActive_ChkBox = CheckBox(   active = self.Config.ActBackgroundImageActive,
                                                        width = 30,
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        size_hint = [None, None])
        self.BackgroundImageActive_ChkBox.bind(active = self.BackgroundImageActiveChkBoxActive)

        self.BackgroundImageActive_Label = Custom.LabelButton(  text = 'Use background image',
                                                                halign = 'left',
                                                                valign = MainLabelValign,
                                                                height = MainConfigLayoutGridHeight / 2,
                                                                font_size = MainLabelTextSize,
                                                                size_hint_x = 0.37,
                                                                size_hint_y = None)
        self.BackgroundImageActive_Label.bind(  size = self.BackgroundImageActive_Label.setter('text_size'),
                                                on_release = self.BackgroundImageActiveLabelActive)

        # put a spare widget behind the description, just to be sure that only the description label is clickable and not the whole line
        self.BackgroundImageActiveSpare_ColoredCanvas = Custom.ColoredCanvas(   height = MainConfigLayoutGridHeight / 2,
                                                                                size_hint_y = None)

        ##########################################################################################

        self.BackgroundImageActive_Layout.add_widget(self.BackgroundImageActive_ChkBox)
        self.BackgroundImageActive_Layout.add_widget(self.BackgroundImageActive_Label)
        self.BackgroundImageActive_Layout.add_widget(self.BackgroundImageActiveSpare_ColoredCanvas)

        self.ConfigPageDesign2_Layout.add_widget(self.BackgroundImageActive_Layout)

        ##########################################################################################
        #                                                                                        #
        # Welcome message                                                                        #
        #                                                                                        #
        ##########################################################################################
                
        self.WelcomeMsg1_Layout = GridLayout(   cols = 3,
                                                padding = [0, -5],
                                                height = MainConfigLayoutGridHeight / 2,
                                                width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                size_hint = [None, None])
        
        self.WelcomeMsg2_Layout = GridLayout(   cols = 2,
                                                padding = [0, -10],
                                                height = MainConfigLayoutGridHeight / 2,
                                                width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                size_hint = [None, None])

        self.WelcomeMsgSlider_Layout = GridLayout(  cols = 1,
                                                    padding = [0, 5],
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = (3 * MainConfigLayoutGridWidth),
                                                    size_hint = [None, None])

        if (self.Config.ActWelcomeMsgDuration > 0):
            tmpChkBoxActive = True
        else:
            tmpChkBoxActive = False
        self.WelcomeMsg_ChkBox = CheckBox(  active = tmpChkBoxActive,
                                            width = 30,
                                            height = MainConfigLayoutGridHeight / 2,
                                            size_hint = [None, None])
        self.WelcomeMsg_ChkBox.bind(active = self.WelcomeMsgChkBoxActive)

        self.WelcomeMsg_Label = Custom.LabelButton( text = 'Display welcome message',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    font_size = MainLabelTextSize,
                                                    size_hint_x = 0.45,
                                                    size_hint_y = None)
        self.WelcomeMsg_Label.bind( size = self.WelcomeMsg_Label.setter('text_size'),
                                    on_release = self.WelcomeMsgLabelActive)

        # put a spare widget behind the description, just to be sure that only the description label is clickable and not the whole line
        self.WelcomeMsgSpare_ColoredCanvas = Custom.ColoredCanvas(  height = MainConfigLayoutGridHeight / 2,
                                                                    size_hint_y = None)

        self.WelcomeMsgSpare1_Label = Label(    text = ' ',
                                                halign = 'left',
                                                valign = MainLabelValign,
                                                height = MainConfigLayoutGridHeight / 2,
                                                width = 30,
                                                font_size = MainLabelTextSize,
                                                size_hint = [None, None])
        self.WelcomeMsgSpare1_Label.bind(size = self.WelcomeMsgSpare1_Label.setter('text_size'))

        self.WelcomeMsgDescription_Label = Label(   text = 'Show welcome message after starting the dashboard for ' + str(self.Config.ActWelcomeMsgDuration) + ' seconds',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    font_size = MainLabelTextSize,
                                                    size_hint_y = None)
        self.WelcomeMsgDescription_Label.bind(size = self.WelcomeMsgDescription_Label.setter('text_size'))

        self.WelcomeMsgSpare2_Label = Label(    text = ' ',
                                                halign = 'left',
                                                valign = MainLabelValign,
                                                height = MainConfigLayoutGridHeight / 2,
                                                width = 30,
                                                font_size = MainLabelTextSize,
                                                size_hint = [None, None])
        self.WelcomeMsgSpare2_Label.bind(size = self.WelcomeMsgSpare2_Label.setter('text_size'))

        self.WelcomeMsg_Slider = Slider(    min = 1.0,
                                            max = 10.0,
                                            step = 0.5,
                                            height = MainConfigLayoutGridHeight / 2,
                                            width =  2 * MainConfigLayoutGridWidth,
                                            size_hint = [None, None],
                                            value = self.Config.ActWelcomeMsgDuration)
        self.WelcomeMsg_Slider.bind(value = self.WelcomMsgSliderChange)
        
        self.WelcomeMsgSlider_Layout.add_widget(self.WelcomeMsg_Slider)

        ##########################################################################################

        self.WelcomeMsg1_Layout.add_widget(self.WelcomeMsg_ChkBox)
        self.WelcomeMsg1_Layout.add_widget(self.WelcomeMsg_Label)
        self.WelcomeMsg1_Layout.add_widget(self.WelcomeMsgSpare_ColoredCanvas)
        if (self.Config.ActWelcomeMsgDuration > 0):
            # only show the slider for the welcome message, if welcome message is enabled
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgSpare1_Label)
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgDescription_Label)
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgSpare2_Label)
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgSlider_Layout)

        self.ConfigPageFunctions1_Layout.add_widget(self.WelcomeMsg1_Layout)
        self.ConfigPageFunctions1_Layout.add_widget(self.WelcomeMsg2_Layout)

        ##########################################################################################
        #                                                                                        #
        # Faster car behind                                                                      #
        #                                                                                        #
        ##########################################################################################
        
        self.FasterCarBehind1_Layout = GridLayout(  cols = 3,
                                                    padding = [0, 25],
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                    size_hint = [None, None])
        
        self.FasterCarBehind2_Layout = GridLayout(  cols = 2,
                                                    padding = [0, 20],
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                    size_hint = [None, None])

        self.FasterCarBehindSlider_Layout = GridLayout( cols = 1,
                                                        padding = [0, 5],
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        width = (3 * MainConfigLayoutGridWidth),
                                                        size_hint = [None, None])

        self.FasterCarBehind_ChkBox = CheckBox( active = self.Config.ActShowFasterCarBehind,
                                                width = 30,
                                                height = MainConfigLayoutGridHeight / 2,
                                                size_hint = [None, None])
        self.FasterCarBehind_ChkBox.bind(active = self.FasterCarBehindChkBoxActive)

        self.FasterCarBehind_Label = Custom.LabelButton(    text = 'Show if a faster car is behind',
                                                            halign = 'left',
                                                            valign = MainLabelValign,
                                                            height = MainConfigLayoutGridHeight / 2,
                                                            font_size = MainLabelTextSize,
                                                            size_hint_x = 0.52,
                                                            size_hint_y = None)
        self.FasterCarBehind_Label.bind(    size = self.FasterCarBehind_Label.setter('text_size'),
                                            on_release = self.FasterCarBehindLabelActive)

        # put a spare widget the description, just to be sure that only the description label is clickable and not the whole line
        self.FasterCarBehindSpare_ColoredCanvas = Custom.ColoredCanvas( height = MainConfigLayoutGridHeight / 2,
                                                                        size_hint_y = None)

        self.FasterCarBehindSpare1_Label = Label(   text = ' ',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = 30,
                                                    font_size = MainLabelTextSize,
                                                    size_hint = [None, None])
        self.FasterCarBehindSpare1_Label.bind(size = self.FasterCarBehindSpare1_Label.setter('text_size'))

        self.FasterCarBehindDescription_Label = Label(  text = 'Show faster car behind if his fastest lap is more than 1/' + str(self.Config.ActFasterCarBehindThreshold) + ' faster than your own',
                                                        halign = 'left',
                                                        valign = MainLabelValign,
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        font_size = MainLabelTextSize,
                                                        size_hint_y = None)
        self.FasterCarBehindDescription_Label.bind(size = self.FasterCarBehindDescription_Label.setter('text_size'))

        self.FasterCarBehindSpare2_Label = Label(   text = ' ',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = 30,
                                                    font_size = MainLabelTextSize,
                                                    size_hint = [None, None])
        self.FasterCarBehindSpare2_Label.bind(size = self.FasterCarBehindSpare2_Label.setter('text_size'))

        self.FasterCarBehind_Slider = Slider(   min = 2.0,
                                                max = 90.0,
                                                step = 0.5,
                                                height = MainConfigLayoutGridHeight / 2,
                                                width =  2 * MainConfigLayoutGridWidth,
                                                size_hint = [None, None],
                                                value = self.Config.ActFasterCarBehindThreshold)
        self.FasterCarBehind_Slider.bind(value = self.FasterCarBehindSliderChange)

        self.FasterCarBehindSlider_Layout.add_widget(self.FasterCarBehind_Slider)

        ##########################################################################################

        self.FasterCarBehind1_Layout.add_widget(self.FasterCarBehind_ChkBox)
        self.FasterCarBehind1_Layout.add_widget(self.FasterCarBehind_Label)
        self.FasterCarBehind1_Layout.add_widget(self.FasterCarBehindSpare_ColoredCanvas)
        if (self.Config.ActShowFasterCarBehind):
            # only show the slider for the faster car behind threshold if function is enabled
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindSpare1_Label)
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindDescription_Label)
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindSpare2_Label)
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindSlider_Layout)

        self.ConfigPageFunctions1_Layout.add_widget(self.FasterCarBehind1_Layout)
        self.ConfigPageFunctions1_Layout.add_widget(self.FasterCarBehind2_Layout)
        
        ##########################################################################################
        #                                                                                        #
        # Last lap time diplay duration                                                          #
        #                                                                                        #
        ##########################################################################################
                
        self.LastLapDisplay1_Layout = GridLayout(   cols = 3,
                                                    padding = [0, 55],
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                    size_hint = [None, None])
        
        self.LastLapDisplay2_Layout = GridLayout(   cols = 2,
                                                    padding = [0, 50],
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                    size_hint = [None, None])

        self.LastLapDisplaySlider_Layout = GridLayout(  cols = 1,
                                                        padding = [0, 5],
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        width = (3 * MainConfigLayoutGridWidth),
                                                        size_hint = [None, None])

        if (self.Config.ActLastLapTimeDisplayDuration > 0):
            tmpChkBoxActive = True
        else:
            tmpChkBoxActive = False
        self.LastLapDisplay_ChkBox = CheckBox(  active = tmpChkBoxActive,
                                                width = 30,
                                                height = MainConfigLayoutGridHeight / 2,
                                                size_hint = [None, None])
        self.LastLapDisplay_ChkBox.bind(active = self.LastLapDisplayChkBoxActive)

        self.LastLapDisplay_Label = Custom.LabelButton( text = 'Show last lap time',
                                                        halign = 'left',
                                                        valign = MainLabelValign,
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        font_size = MainLabelTextSize,
                                                        size_hint_x = 0.3,
                                                        size_hint_y = None)
        self.LastLapDisplay_Label.bind( size = self.LastLapDisplay_Label.setter('text_size'),
                                        on_release = self.LastLapDisplayLabelActive)

        # put a spare widget the description, just to be sure that only the description label is clickable and not the whole line
        self.LastLapDisplaySpare_ColoredCanvas = Custom.ColoredCanvas(  height = MainConfigLayoutGridHeight / 2,
                                                                        size_hint_y = None)

        self.LastLapDisplaySpare1_Label = Label(    text = ' ',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = 30,
                                                    font_size = MainLabelTextSize,
                                                    size_hint = [None, None])
        self.LastLapDisplaySpare1_Label.bind(size = self.LastLapDisplaySpare1_Label.setter('text_size'))

        self.LastLapDisplayDescription_Label = Label(    text = 'Show last lap time at the beginning of a new lap for ' + str(self.Config.ActLastLapTimeDisplayDuration) + ' seconds',
                                                        halign = 'left',
                                                        valign = MainLabelValign,
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        font_size = MainLabelTextSize,
                                                        size_hint_y = None)
        self.LastLapDisplayDescription_Label.bind(size = self.LastLapDisplayDescription_Label.setter('text_size'))

        self.LastLapDisplaySpare2_Label = Label(    text = ' ',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    width = 30,
                                                    font_size = MainLabelTextSize,
                                                    size_hint = [None, None])
        self.LastLapDisplaySpare2_Label.bind(size = self.LastLapDisplaySpare2_Label.setter('text_size'))

        self.LastLapDisplay_Slider = Slider(    min = 1.0,
                                                max = 20.0,
                                                step = 0.5,
                                                height = MainConfigLayoutGridHeight / 2,
                                                width =  2 * MainConfigLayoutGridWidth,
                                                size_hint = [None, None],
                                                value = self.Config.ActLastLapTimeDisplayDuration)
        self.LastLapDisplay_Slider.bind(value = self.LastLapDisplaySliderChange)
        
        self.LastLapDisplaySlider_Layout.add_widget(self.LastLapDisplay_Slider)

        ##########################################################################################

        self.LastLapDisplay1_Layout.add_widget(self.LastLapDisplay_ChkBox)
        self.LastLapDisplay1_Layout.add_widget(self.LastLapDisplay_Label)
        self.LastLapDisplay1_Layout.add_widget(self.LastLapDisplaySpare_ColoredCanvas)
        if (self.Config.ActLastLapTimeDisplayDuration > 0):
            # only show the slider for the welcome message, if welcome message is enabled
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplaySpare1_Label)
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplayDescription_Label)
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplaySpare2_Label)
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplaySlider_Layout)

        self.ConfigPageFunctions1_Layout.add_widget(self.LastLapDisplay1_Layout)
        self.ConfigPageFunctions1_Layout.add_widget(self.LastLapDisplay2_Layout)

        ##########################################################################################
        #                                                                                        #
        # Show Flags                                                                             #
        #                                                                                        #
        ##########################################################################################
        
        self.ShowFlags_Layout = GridLayout( cols = 3,
                                            padding = [0, 85],
                                            height = MainConfigLayoutGridHeight / 2,
                                            width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                            size_hint = [None, None])
        
        self.ShowFlags_ChkBox = CheckBox(   active = self.Config.ActShowFlags,
                                            width = 30,
                                            height = MainConfigLayoutGridHeight / 2,
                                            size_hint = [None, None])
        self.ShowFlags_ChkBox.bind(active = self.ShowFlagsChkBoxActive)

        self.ShowFlags_Label = Custom.LabelButton(  text = 'Show flags',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    font_size = MainLabelTextSize,
                                                    size_hint_x = 0.17,
                                                    size_hint_y = None)
        self.ShowFlags_Label.bind(  size = self.ShowFlags_Label.setter('text_size'),
                                    on_release = self.ShowFlagsLabelActive)

        # put a spare widget behind the description, just to be sure that only the description label is clickable and not the whole line
        self.ShowFlagsSpare_ColoredCanvas = Custom.ColoredCanvas(   height = MainConfigLayoutGridHeight / 2,
                                                                    size_hint_y = None)

        ##########################################################################################

        self.ShowFlags_Layout.add_widget(self.ShowFlags_ChkBox)
        self.ShowFlags_Layout.add_widget(self.ShowFlags_Label)
        self.ShowFlags_Layout.add_widget(self.ShowFlagsSpare_ColoredCanvas)

        self.ConfigPageFunctions1_Layout.add_widget(self.ShowFlags_Layout)

        ##########################################################################################
        #                                                                                        #
        # Background blinking                                                                         #
        #                                                                                        #
        ##########################################################################################

        self.FlagsBlinking_Layout = GridLayout( cols = 3,
                                                padding = [0, 85],
                                                height = MainConfigLayoutGridHeight / 2,
                                                width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                size_hint = [None, None])
        
        self.FlagsBlinking_ChkBox = CheckBox(   active = self.Config.ActFlagsBlinking,
                                                width = 30,
                                                height = MainConfigLayoutGridHeight / 2,
                                                size_hint = [None, None])
        self.FlagsBlinking_ChkBox.bind(active = self.FlagsBlinkingChkBoxActive)

        self.FlagsBlinking_Label = Custom.LabelButton(  text = 'Background images blinking (low fuel could be permanently overlayed if disabled!)',
                                                        halign = 'left',
                                                        valign = MainLabelValign,
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        font_size = MainLabelTextSize,
                                                        size_hint_x = 12.0,
                                                        size_hint_y = None)
        self.FlagsBlinking_Label.bind(  size = self.FlagsBlinking_Label.setter('text_size'),
                                        on_release = self.FlagsBlinkingLabelActive)

        # put a spare widget behind the description, just to be sure that only the description label is clickable and not the whole line
        self.FlagsBlinkingSpare_ColoredWidget = Custom.ColoredCanvas(   height = MainConfigLayoutGridHeight / 2,
                                                                        size_hint_y = None)

        ##########################################################################################

        self.FlagsBlinking_Layout.add_widget(self.FlagsBlinking_ChkBox)
        self.FlagsBlinking_Layout.add_widget(self.FlagsBlinking_Label)
        self.FlagsBlinking_Layout.add_widget(self.FlagsBlinkingSpare_ColoredWidget)

        self.ConfigPageFunctions1_Layout.add_widget(self.FlagsBlinking_Layout)

        ##########################################################################################
        #                                                                                        #
        # RPM Limit                                                                              #
        #                                                                                        #
        ##########################################################################################
        
        self.RpmLimit_Layout = GridLayout(  cols = 3,
                                            padding = [0, 85],
                                            height = MainConfigLayoutGridHeight / 2,
                                            width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                            size_hint = [None, None])
        
        self.RpmLimit_ChkBox = CheckBox(    active = self.Config.ActShowRpmLimit,
                                            width = 30,
                                            height = MainConfigLayoutGridHeight / 2,
                                            size_hint = [None, None])
        self.RpmLimit_ChkBox.bind(active = self.RpmLimitChkBoxActive)

        self.RpmLimit_Label = Custom.LabelButton(   text = 'Show "RPM too high" background if RPM limit is near (RPM >98.5%)',
                                                    halign = 'left',
                                                    valign = MainLabelValign,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    font_size = MainLabelTextSize,
                                                    size_hint_x = 3.2,
                                                    size_hint_y = None)
        self.RpmLimit_Label.bind(   size = self.RpmLimit_Label.setter('text_size'),
                                    on_release = self.RpmLimitLabelActive)

        # put a spare widget behind the description, just to be sure that only the description label is clickable and not the whole line
        self.RpmLimitSpare_ColoredCanvas = Custom.ColoredCanvas(    height = MainConfigLayoutGridHeight / 2,
                                                                    size_hint_y = None)

        ##########################################################################################

        self.RpmLimit_Layout.add_widget(self.RpmLimit_ChkBox)
        self.RpmLimit_Layout.add_widget(self.RpmLimit_Label)
        self.RpmLimit_Layout.add_widget(self.RpmLimitSpare_ColoredCanvas)

        self.ConfigPageFunctions1_Layout.add_widget(self.RpmLimit_Layout)

        ##########################################################################################
        #                                                                                        #
        # DRS                                                                                    #
        #                                                                                        #
        ##########################################################################################
        
        self.Drs_Layout = GridLayout(   cols = 3,
                                        padding = [0, 85],
                                        height = MainConfigLayoutGridHeight / 2,
                                        width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                        size_hint = [None, None])
        
        self.Drs_ChkBox = CheckBox( active = self.Config.ActShowDrs,
                                    width = 30,
                                    height = MainConfigLayoutGridHeight / 2,
                                    size_hint = [None, None])
        self.Drs_ChkBox.bind(active = self.DrsChkBoxActive)

        self.Drs_Label = Custom.LabelButton(    text = 'Show DRS information',
                                                halign = 'left',
                                                valign = MainLabelValign,
                                                height = MainConfigLayoutGridHeight / 2,
                                                font_size = MainLabelTextSize,
                                                size_hint_x = 0.37,
                                                size_hint_y = None)
        self.Drs_Label.bind(    size = self.Drs_Label.setter('text_size'),
                                on_release = self.DrsLabelActive)

        # put a spare widget behind the description, just to be sure that only the description label is clickable and not the whole line
        self.DrsSpare_ColoredCanvas = Custom.ColoredCanvas( height = MainConfigLayoutGridHeight / 2,
                                                            size_hint_y = None)

        ##########################################################################################

        self.Drs_Layout.add_widget(self.Drs_ChkBox)
        self.Drs_Layout.add_widget(self.Drs_Label)
        self.Drs_Layout.add_widget(self.DrsSpare_ColoredCanvas)

        self.ConfigPageFunctions1_Layout.add_widget(self.Drs_Layout)

        ##########################################################################################
        #                                                                                        #
        # Fuel / refill required                                                                 #
        #                                                                                        #
        ##########################################################################################
        
        self.ShowRefillRequired_Layout = GridLayout(    cols = 3,
                                                        padding = [0, 85],
                                                        height = MainConfigLayoutGridHeight / 2,
                                                        width = (3 * MainConfigLayoutGridWidth) + (2 * MainGridPadding),
                                                        size_hint = [None, None])
        
        self.ShowRefillRequired_ChkBox = CheckBox(  active = self.Config.ActShowRefillRequired,
                                                    width = 30,
                                                    height = MainConfigLayoutGridHeight / 2,
                                                    size_hint = [None, None])
        self.ShowRefillRequired_ChkBox.bind(active = self.ShowRefillRequiredChkBoxActive)

        self.ShowRefillRequired_Label = Custom.LabelButton( text = 'Show est. refill required',
                                                            halign = 'left',
                                                            valign = MainLabelValign,
                                                            height = MainConfigLayoutGridHeight / 2,
                                                            font_size = MainLabelTextSize,
                                                            size_hint_x = 0.37,
                                                            size_hint_y = None)
        self.ShowRefillRequired_Label.bind( size = self.ShowRefillRequired_Label.setter('text_size'),
                                            on_release = self.ShowRefillRequiredLabelActive)

        # put a spare widget behind the description, just to be sure that only the description label is clickable and not the whole line
        self.ShowRefillRequiredSpare_ColoredCanvas = Custom.ColoredCanvas(  height = MainConfigLayoutGridHeight / 2,
                                                                            size_hint_y = None)

        ##########################################################################################

        self.ShowRefillRequired_Layout.add_widget(self.ShowRefillRequired_ChkBox)
        self.ShowRefillRequired_Layout.add_widget(self.ShowRefillRequired_Label)
        self.ShowRefillRequired_Layout.add_widget(self.ShowRefillRequiredSpare_ColoredCanvas)

        self.ConfigPageFunctions1_Layout.add_widget(self.ShowRefillRequired_Layout)

        ##################################################################################################
        ##################################################################################################
        ##################################################################################################
        #####                                                                                        #####
        ##### Preview                                                                                #####
        #####                                                                                        #####
        ##################################################################################################
        ##################################################################################################
        ##################################################################################################

        self.Preview_Layout = FloatLayout(  width = ((DashboardWidth / 100 ) * PreviewSize),
                                            height = ((DashboardHeight / 100 ) * PreviewSize),
                                            size_hint = [None, None])
        
        self.PreviewBackground_ColoredCanvas = Custom.ColoredCanvas(    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewBackgroundImage_Layout = RelativeLayout(    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                                height = ((DashboardHeight / 100 ) * PreviewSize),
                                                                size_hint = [None, None],
                                                                pos_hint = {'x': 0, 'y': 0})
        self.PreviewBackgroundImage_Image = Image(  source = ARIS_folder + '\\background\\Background.png')
        if not self.Config.ActBackgroundImageActive:
            self.PreviewBackgroundImage_Image.opacity = 0.0
        self.PreviewBackgroundImage_Layout.add_widget(self.PreviewBackgroundImage_Image)

        self.PreviewBackgroundFlag_Layout = RelativeLayout( width = ((DashboardWidth / 100 ) * PreviewSize),
                                                            height = ((DashboardHeight / 100 ) * PreviewSize),
                                                            size_hint = [None, None],
                                                            pos_hint = {'x': 0, 'y': 0})
        self.PreviewBackgroundFlag_Image = Image(  source = ARIS_folder + '\\background\\BlueFlag.png')
        self.PreviewBackgroundFlag_Image.opacity = 0.0
        self.PreviewBackgroundFlag_Layout.add_widget(self.PreviewBackgroundFlag_Image)

        ##########################################################################################
        # RPM                                                                                    #
        ##########################################################################################

        self.PreviewRpm_Layout = RelativeLayout(    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewRpmBorder_ColoredCanvas = Custom.ColoredCanvas( width = ((DashboardWidth / 100 ) * PreviewSize),
                                                                    height = ((54 / 100 ) * PreviewSize),
                                                                    size_hint = [None,None])
        self.PreviewRpmBorder_ColoredCanvas.pos = [0, self.PreviewRpm_Layout.height - self.PreviewRpmBorder_ColoredCanvas.height]

        self.PreviewRpm1_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm2_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm3_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm4_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm5_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm6_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm7_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm8_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm9_ColoredCanvas = Custom.ColoredCanvas(  width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm10_ColoredCanvas = Custom.ColoredCanvas( width = int(80 / 100 * PreviewSize),
                                                                height = int(42 / 100 * PreviewSize),
                                                                size_hint = [None,None])
        self.PreviewRpm1_ColoredCanvas.pos = [int(34 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm1_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm2_ColoredCanvas.pos = [int(124 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm2_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm3_ColoredCanvas.pos = [int(214 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm3_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm4_ColoredCanvas.pos = [int(304 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm4_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm5_ColoredCanvas.pos = [int(394 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm5_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm6_ColoredCanvas.pos = [int(484 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm6_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm7_ColoredCanvas.pos = [int(574 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm7_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm8_ColoredCanvas.pos = [int(664 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm8_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm9_ColoredCanvas.pos = [int(754 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm9_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpm10_ColoredCanvas.pos = [int(844 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpm10_ColoredCanvas.height - int(6 / 100 * PreviewSize)]

        self.PreviewRpm_Layout.add_widget(self.PreviewRpmBorder_ColoredCanvas)

        self.PreviewRpm_Layout.add_widget(self.PreviewRpm1_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm2_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm3_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm4_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm5_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm6_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm7_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm8_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm9_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpm10_ColoredCanvas)

        self.PreviewRpmLinearGaugeSep1_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep2_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep3_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep4_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep5_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep6_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep7_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep8_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep9_ColoredCanvas = Custom.ColoredCanvas(    width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep10_ColoredCanvas = Custom.ColoredCanvas(   width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep11_ColoredCanvas = Custom.ColoredCanvas(   width = 2,
                                                                                height = int(42 / 100 * PreviewSize),
                                                                                size_hint = [None,None])
        self.PreviewRpmLinearGaugeSep1_ColoredCanvas.pos = [int(34 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep1_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep2_ColoredCanvas.pos = [int(116 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep2_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep3_ColoredCanvas.pos = [int(206 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep3_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep4_ColoredCanvas.pos = [int(296 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep4_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep5_ColoredCanvas.pos = [int(386 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep5_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep6_ColoredCanvas.pos = [int(476 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep6_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep7_ColoredCanvas.pos = [int(566 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep7_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep8_ColoredCanvas.pos = [int(656 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep8_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep9_ColoredCanvas.pos = [int(746 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep9_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep10_ColoredCanvas.pos = [int(836 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep10_ColoredCanvas.height - int(6 / 100 * PreviewSize)]
        self.PreviewRpmLinearGaugeSep11_ColoredCanvas.pos = [int(920 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGaugeSep11_ColoredCanvas.height - int(6 / 100 * PreviewSize)]

        self.PreviewRpmLinearGauge_Label = Custom.ColoredCanvas(    width = int(80 / 100 * PreviewSize),
                                                                    height = int(26 / 100 * PreviewSize),
                                                                    size_hint = [None,None])
        self.PreviewRpmLinearGauge_Label.pos = [int(34 / 100 * PreviewSize), self.PreviewRpm_Layout.height - self.PreviewRpmLinearGauge_Label.height - int(14 / 100 * PreviewSize)]

        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep1_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep2_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep3_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep4_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep5_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep6_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep7_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep8_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep9_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep10_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGaugeSep11_ColoredCanvas)
        self.PreviewRpm_Layout.add_widget(self.PreviewRpmLinearGauge_Label)

        ##########################################################################################
        # Fuel left                                                                              #
        ##########################################################################################

        self.PreviewFuelLeft_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewFuelLeftBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(374 / 100 * PreviewSize),
                                                                            height = int(96 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewFuelLeftBorder_ColoredCanvas.pos = [0, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewFuelLeftBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelLeftText_Label = Label( text = '00:43:49 (5.0)',
                                                width = int(374 / 100 * PreviewSize),
                                                height = int(96 / 100 * PreviewSize),
                                                font_size = int(50 / 100 * PreviewSize),
                                                valign = 'top',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewFuelLeftText_Label.text_size = self.PreviewFuelLeftText_Label.size
        self.PreviewFuelLeftText_Label.pos = [0, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewFuelLeftText_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelLeftTitle_Label = Label(    text = 'Fuel Left',
                                                    width = int(374 / 100 * PreviewSize),
                                                    height = int(90 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewFuelLeftTitle_Label.text_size = self.PreviewFuelLeftTitle_Label.size
        self.PreviewFuelLeftTitle_Label.pos = [0, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewFuelLeftTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelLeft_Layout.add_widget(self.PreviewFuelLeftBorder_ColoredCanvas)
        self.PreviewFuelLeft_Layout.add_widget(self.PreviewFuelLeftText_Label)
        self.PreviewFuelLeft_Layout.add_widget(self.PreviewFuelLeftTitle_Label)

        ##########################################################################################
        # Fuel                                                                                   #
        ##########################################################################################

        self.PreviewFuel_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewFuelBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(186 / 100 * PreviewSize),
                                                                        height = int(96 / 100 * PreviewSize),
                                                                        size_hint = [None, None])
        self.PreviewFuelBorder_ColoredCanvas.pos = [0, self.PreviewFuelLeftBorder_ColoredCanvas.pos[1] - self.PreviewFuelBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelText_Label = Label( text = '78.2',
                                            width = int(186 / 100 * PreviewSize),
                                            height = int(96 / 100 * PreviewSize),
                                            font_size = int(50 / 100 * PreviewSize),
                                            valign = 'top',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewFuelText_Label.text_size = self.PreviewFuelText_Label.size
        self.PreviewFuelText_Label.pos = [0, self.PreviewFuelLeftBorder_ColoredCanvas.pos[1] - self.PreviewFuelText_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelTitle_Label = Label(    text = 'Fuel',
                                                width = int(186 / 100 * PreviewSize),
                                                height = int(90 / 100 * PreviewSize),
                                                font_size = int(23 / 100 * PreviewSize),
                                                valign = 'bottom',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewFuelTitle_Label.text_size = self.PreviewFuelTitle_Label.size
        self.PreviewFuelTitle_Label.pos = [0, self.PreviewFuelLeftBorder_ColoredCanvas.pos[1] - self.PreviewFuelTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewFuel_Layout.add_widget(self.PreviewFuelBorder_ColoredCanvas)
        self.PreviewFuel_Layout.add_widget(self.PreviewFuelText_Label)
        self.PreviewFuel_Layout.add_widget(self.PreviewFuelTitle_Label)

        ##########################################################################################
        # Fuel / Lap                                                                             #
        ##########################################################################################

        self.PreviewFuelPerLap_Layout = RelativeLayout( width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewFuelPerLapBorder_ColoredCanvas = Custom.ColoredCanvas(  width = int(186 / 100 * PreviewSize),
                                                                            height = int(96 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewFuelPerLapBorder_ColoredCanvas.pos = [self.PreviewFuelBorder_ColoredCanvas.pos[0] + self.PreviewFuelBorder_ColoredCanvas.width + 2, self.PreviewFuelLeftBorder_ColoredCanvas.pos[1] - self.PreviewFuelPerLapBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelPerLapText_Label = Label(   text = '15.61',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(96 / 100 * PreviewSize),
                                                    font_size = int(50 / 100 * PreviewSize),
                                                    valign = 'top',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewFuelPerLapText_Label.text_size = self.PreviewFuelPerLapText_Label.size
        self.PreviewFuelPerLapText_Label.pos = [self.PreviewFuelBorder_ColoredCanvas.pos[0] + self.PreviewFuelBorder_ColoredCanvas.width + 2, self.PreviewFuelLeftBorder_ColoredCanvas.pos[1] - self.PreviewFuelPerLapText_Label.height + (5 / 100 * PreviewSize) ]

        self.PreviewFuelLastLapText_Label = Label(   text = '(15.68)',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(96 / 100 * PreviewSize),
                                                    font_size = int(24 / 100 * PreviewSize),
                                                    valign = 'middle',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewFuelLastLapText_Label.text_size = self.PreviewFuelLastLapText_Label.size
        self.PreviewFuelLastLapText_Label.pos = [self.PreviewFuelBorder_ColoredCanvas.pos[0] + self.PreviewFuelBorder_ColoredCanvas.width + 2, self.PreviewFuelLeftBorder_ColoredCanvas.pos[1] - self.PreviewFuelLastLapText_Label.height - (7 / 100 * PreviewSize)]

        self.PreviewFuelPerLapTitle_Label = Label(  text = 'Fuel / Lap',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(90 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewFuelPerLapTitle_Label.text_size = self.PreviewFuelPerLapTitle_Label.size
        self.PreviewFuelPerLapTitle_Label.pos = [self.PreviewFuelBorder_ColoredCanvas.pos[0] + self.PreviewFuelBorder_ColoredCanvas.width + 2, self.PreviewFuelLeftBorder_ColoredCanvas.pos[1] - self.PreviewFuelPerLapTitle_Label.height - 1]

        self.PreviewFuelPerLap_Layout.add_widget(self.PreviewFuelPerLapBorder_ColoredCanvas)
        self.PreviewFuelPerLap_Layout.add_widget(self.PreviewFuelPerLapText_Label)
        self.PreviewFuelPerLap_Layout.add_widget(self.PreviewFuelLastLapText_Label)
        self.PreviewFuelPerLap_Layout.add_widget(self.PreviewFuelPerLapTitle_Label)

        ##########################################################################################
        # Lap delta                                                                              #
        ##########################################################################################

        self.PreviewLapDelta_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewLapDeltaBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(186 / 100 * PreviewSize),
                                                                            height = int(96 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewLapDeltaBorder_ColoredCanvas.pos = [0, self.PreviewFuelBorder_ColoredCanvas.pos[1] - self.PreviewLapDeltaBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewLapDeltaText_Label = Label( text = '+0.13',
                                                width = int(186 / 100 * PreviewSize),
                                                height = int(96 / 100 * PreviewSize),
                                                font_size = int(50 / 100 * PreviewSize),
                                                valign = 'top',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewLapDeltaText_Label.text_size = self.PreviewLapDeltaText_Label.size
        self.PreviewLapDeltaText_Label.pos = [0, self.PreviewFuelBorder_ColoredCanvas.pos[1] - self.PreviewLapDeltaText_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewLapDeltaTitle_Label = Label(    text = 'Lap Delta',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(90 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewLapDeltaTitle_Label.text_size = self.PreviewLapDeltaTitle_Label.size
        self.PreviewLapDeltaTitle_Label.pos = [0, self.PreviewFuelBorder_ColoredCanvas.pos[1] - self.PreviewLapDeltaTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewLapDelta_Layout.add_widget(self.PreviewLapDeltaBorder_ColoredCanvas)
        self.PreviewLapDelta_Layout.add_widget(self.PreviewLapDeltaText_Label)
        self.PreviewLapDelta_Layout.add_widget(self.PreviewLapDeltaTitle_Label)

        ##########################################################################################
        # Fuel / refill required                                                                 #
        ##########################################################################################

        self.PreviewFuelRequired_Layout = RelativeLayout( width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewFuelRequiredBorder_ColoredCanvas = Custom.ColoredCanvas(  width = int(186 / 100 * PreviewSize),
                                                                            height = int(96 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewFuelRequiredBorder_ColoredCanvas.pos = [self.PreviewLapDeltaBorder_ColoredCanvas.pos[0] + self.PreviewLapDeltaBorder_ColoredCanvas.width + 2, self.PreviewFuelPerLapBorder_ColoredCanvas.pos[1] - self.PreviewFuelRequiredBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelRequiredText_Label = Label(   text = '',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(96 / 100 * PreviewSize),
                                                    font_size = int(50 / 100 * PreviewSize),
                                                    valign = 'top',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewFuelRequiredText_Label.text_size = self.PreviewFuelRequiredText_Label.size
        self.PreviewFuelRequiredText_Label.pos = [self.PreviewLapDeltaBorder_ColoredCanvas.pos[0] + self.PreviewLapDeltaBorder_ColoredCanvas.width + 2, self.PreviewFuelPerLapBorder_ColoredCanvas.pos[1] - self.PreviewFuelRequiredText_Label.height - (2 / 100 * PreviewSize)]
        
        self.PreviewFuelRequiredTitle_Label = Label(    text = '',
                                                        width = int(186 / 100 * PreviewSize),
                                                        height = int(90 / 100 * PreviewSize),
                                                        font_size = int(23 / 100 * PreviewSize),
                                                        valign = 'bottom',
                                                        halign = 'center',
                                                        size_hint = [None, None],
                                                        color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        if self.Config.ActShowRefillRequired:
            self.PreviewFuelRequiredText_Label.text = '335.9'
            self.PreviewFuelRequiredTitle_Label.text = 'Refill Required'
        else:
            self.PreviewFuelRequiredText_Label.text = '414.1'
            self.PreviewFuelRequiredTitle_Label.text = 'Fuel Required'
        self.PreviewFuelRequiredTitle_Label.text_size = self.PreviewFuelRequiredTitle_Label.size
        self.PreviewFuelRequiredTitle_Label.pos = [self.PreviewLapDeltaBorder_ColoredCanvas.pos[0] + self.PreviewLapDeltaBorder_ColoredCanvas.width + 2, self.PreviewFuelPerLapBorder_ColoredCanvas.pos[1] - self.PreviewFuelRequiredTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewFuelRequired_Layout.add_widget(self.PreviewFuelRequiredBorder_ColoredCanvas)
        self.PreviewFuelRequired_Layout.add_widget(self.PreviewFuelRequiredText_Label)
        self.PreviewFuelRequired_Layout.add_widget(self.PreviewFuelRequiredTitle_Label)

        ##########################################################################################
        # Lap time                                                                               #
        ##########################################################################################

        self.PreviewLapTime_Layout = RelativeLayout(    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewLapTimeBorder_ColoredCanvas = Custom.ColoredCanvas( width = int(374 / 100 * PreviewSize),
                                                                        height = int(96 / 100 * PreviewSize),
                                                                        size_hint = [None, None])
        self.PreviewLapTimeBorder_ColoredCanvas.pos = [0, self.PreviewLapDeltaBorder_ColoredCanvas.pos[1] - self.PreviewLapTimeBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewLapTimeText1_Label = Label( text = '03m ',
                                                width = int(130 / 100 * PreviewSize),
                                                height = int(54 / 100 * PreviewSize),
                                                font_size = int(35 / 100 * PreviewSize),
                                                valign = 'bottom',
                                                halign = 'right',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewLapTimeText1_Label.text_size = self.PreviewLapTimeText1_Label.size
        self.PreviewLapTimeText1_Label.pos = [0, self.PreviewLapDeltaBorder_ColoredCanvas.pos[1] - self.PreviewLapTimeText1_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewLapTimeText2_Label = Label( text = '08.868 s',
                                                width = int(244 / 100 * PreviewSize),
                                                height = int(96 / 100 * PreviewSize),
                                                font_size = int(50 / 100 * PreviewSize),
                                                valign = 'top',
                                                halign = 'left',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewLapTimeText2_Label.text_size = self.PreviewLapTimeText2_Label.size
        self.PreviewLapTimeText2_Label.pos = [self.PreviewLapTimeText1_Label.pos[0] + self.PreviewLapTimeText1_Label.width, self.PreviewLapDeltaBorder_ColoredCanvas.pos[1] - self.PreviewLapTimeText2_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewLapTimeTitle_Label = Label(     text = 'Lap Time',
                                                    width = int(374 / 100 * PreviewSize),
                                                    height = int(90 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewLapTimeTitle_Label.text_size = self.PreviewLapTimeTitle_Label.size
        self.PreviewLapTimeTitle_Label.pos = [0, self.PreviewLapDeltaBorder_ColoredCanvas.pos[1] - self.PreviewLapTimeTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewLapTime_Layout.add_widget(self.PreviewLapTimeBorder_ColoredCanvas)
        self.PreviewLapTime_Layout.add_widget(self.PreviewLapTimeText1_Label)
        self.PreviewLapTime_Layout.add_widget(self.PreviewLapTimeText2_Label)
        self.PreviewLapTime_Layout.add_widget(self.PreviewLapTimeTitle_Label)

        ##########################################################################################
        # Actual stint                                                                           #
        ##########################################################################################

        self.PreviewActualStint_Layout = RelativeLayout(    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                            height = ((DashboardHeight / 100 ) * PreviewSize),
                                                            size_hint = [None, None],
                                                            pos_hint = {'x': 0, 'y': 0})

        self.PreviewActualStintBorder_ColoredCanvas = Custom.ColoredCanvas( width = int(374 / 100 * PreviewSize),
                                                                            height = int(96 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewActualStintBorder_ColoredCanvas.pos = [0, self.PreviewLapTimeBorder_ColoredCanvas.pos[1] - self.PreviewActualStintBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewActualStintText_Label = Label(  text = '00:19:50 (002)',
                                                    width = int(374 / 100 * PreviewSize),
                                                    height = int(96 / 100 * PreviewSize),
                                                    font_size = int(50 / 100 * PreviewSize),
                                                    valign = 'top',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewActualStintText_Label.text_size = self.PreviewActualStintText_Label.size
        self.PreviewActualStintText_Label.pos = [0, self.PreviewLapTimeBorder_ColoredCanvas.pos[1] - self.PreviewActualStintText_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewActualStintTitle_Label = Label( text = 'Actual Stint',
                                                    width = int(374 / 100 * PreviewSize),
                                                    height = int(90 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewActualStintTitle_Label.text_size = self.PreviewActualStintTitle_Label.size
        self.PreviewActualStintTitle_Label.pos = [0, self.PreviewLapTimeBorder_ColoredCanvas.pos[1] - self.PreviewActualStintTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewActualStint_Layout.add_widget(self.PreviewActualStintBorder_ColoredCanvas)
        self.PreviewActualStint_Layout.add_widget(self.PreviewActualStintText_Label)
        self.PreviewActualStint_Layout.add_widget(self.PreviewActualStintTitle_Label)

        ##########################################################################################
        # Gear                                                                                   #
        ##########################################################################################

        self.PreviewGear_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewGearBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(208 / 100 * PreviewSize),
                                                                        height = int(128 / 100 * PreviewSize),
                                                                        size_hint = [None, None])
        self.PreviewGearBorder_ColoredCanvas.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewGearBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewGearText_Label = Label( text = '2',
                                            width = int(208 / 100 * PreviewSize),
                                            height = int(128 / 100 * PreviewSize),
                                            font_size = int(150 / 100 * PreviewSize),
                                            valign = 'middle',
                                            halign = 'center',
                                            bold = True,
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActGearTextColor['Color']))
        self.PreviewGearText_Label.text_size = self.PreviewGearText_Label.size
        self.PreviewGearText_Label.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewGearText_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewGear_Layout.add_widget(self.PreviewGearBorder_ColoredCanvas)
        self.PreviewGear_Layout.add_widget(self.PreviewGearText_Label)

        ##########################################################################################
        # Speed                                                                                  #
        ##########################################################################################

        self.PreviewSpeed_Layout = RelativeLayout(  width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewSpeedBorder_ColoredCanvas = Custom.ColoredCanvas(   width = int(208 / 100 * PreviewSize),
                                                                        height = int(104 / 100 * PreviewSize),
                                                                        size_hint = [None, None])
        self.PreviewSpeedBorder_ColoredCanvas.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewGearBorder_ColoredCanvas.pos[1] - self.PreviewSpeedBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewSpeedText_Label = Label(    text = '99',
                                                width = int(208 / 100 * PreviewSize),
                                                height = int(104 / 100 * PreviewSize),
                                                font_size = int(86 / 100 * PreviewSize),
                                                valign = 'middle',
                                                halign = 'center',
                                                bold = True,
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewSpeedText_Label.text_size = self.PreviewSpeedText_Label.size
        self.PreviewSpeedText_Label.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewGearBorder_ColoredCanvas.pos[1] - self.PreviewSpeedText_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewSpeed_Layout.add_widget(self.PreviewSpeedBorder_ColoredCanvas)
        self.PreviewSpeed_Layout.add_widget(self.PreviewSpeedText_Label)

        ##########################################################################################
        # Position                                                                               #
        ##########################################################################################

        self.PreviewPosition_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewPositionBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(208 / 100 * PreviewSize),
                                                                            height = int(104 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewPositionBorder_ColoredCanvas.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewSpeedBorder_ColoredCanvas.pos[1] - self.PreviewPositionBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewPositionText_Label = Label( text = '3/37',
                                                width = int(208 / 100 * PreviewSize),
                                                height = int(104 / 100 * PreviewSize),
                                                font_size = int(50 / 100 * PreviewSize),
                                                valign = 'middle',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewPositionText_Label.text_size = self.PreviewPositionText_Label.size
        self.PreviewPositionText_Label.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewSpeedBorder_ColoredCanvas.pos[1] - self.PreviewPositionText_Label.height + (14 / 100 * PreviewSize)]

        self.PreviewPositionTitle_Label = Label(    text = 'Position',
                                                    width = int(208 / 100 * PreviewSize),
                                                    height = int(104 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewPositionTitle_Label.text_size = self.PreviewPositionTitle_Label.size
        self.PreviewPositionTitle_Label.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewSpeedBorder_ColoredCanvas.pos[1] - self.PreviewPositionText_Label.height + (6 / 100 * PreviewSize)]

        self.PreviewPosition_Layout.add_widget(self.PreviewPositionBorder_ColoredCanvas)
        self.PreviewPosition_Layout.add_widget(self.PreviewPositionText_Label)
        self.PreviewPosition_Layout.add_widget(self.PreviewPositionTitle_Label)

        ##########################################################################################
        # Gap                                                                                    #
        ##########################################################################################

        self.PreviewGap_Layout = RelativeLayout(    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewGapBorder_ColoredCanvas = Custom.ColoredCanvas( width = int(208 / 100 * PreviewSize),
                                                                    height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                                    size_hint = [None, None])
        self.PreviewGapBorder_ColoredCanvas.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewPositionBorder_ColoredCanvas.pos[1] - self.PreviewGapBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewGapText1_Label = Label( text = '-24.19',
                                            width = int(208 / 100 * PreviewSize),
                                            height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                            font_size = int(50 / 100 * PreviewSize),
                                            valign = 'top',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewGapText1_Label.text_size = self.PreviewGapText1_Label.size
        self.PreviewGapText1_Label.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewPositionBorder_ColoredCanvas.pos[1] - self.PreviewGapText1_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewGapText2_Label = Label( text = '+36.90',
                                            width = int(208 / 100 * PreviewSize),
                                            height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                            font_size = int(50 / 100 * PreviewSize),
                                            valign = 'bottom',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewGapText2_Label.text_size = self.PreviewGapText2_Label.size
        self.PreviewGapText2_Label.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewPositionBorder_ColoredCanvas.pos[1] - self.PreviewGapText2_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewGapTitle_Label = Label( text = 'Gap',
                                            width = int(208 / 100 * PreviewSize),
                                            height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                            font_size = int(23 / 100 * PreviewSize),
                                            valign = 'middle',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewGapTitle_Label.text_size = self.PreviewGapTitle_Label.size
        self.PreviewGapTitle_Label.pos = [self.PreviewFuelLeftBorder_ColoredCanvas.pos[0] + self.PreviewFuelLeftBorder_ColoredCanvas.width + 2, self.PreviewPositionBorder_ColoredCanvas.pos[1] - self.PreviewGapTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewGap_Layout.add_widget(self.PreviewGapBorder_ColoredCanvas)
        self.PreviewGap_Layout.add_widget(self.PreviewGapText1_Label)
        self.PreviewGap_Layout.add_widget(self.PreviewGapText2_Label)
        self.PreviewGap_Layout.add_widget(self.PreviewGapTitle_Label)

        ##########################################################################################
        # Oil temperature                                                                        #
        ##########################################################################################

        self.PreviewOil_Layout = RelativeLayout(    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewOilBorder_ColoredCanvas = Custom.ColoredCanvas( width = int(186 / 100 * PreviewSize),
                                                                    height = int(96 / 100 * PreviewSize),
                                                                    size_hint = [None, None])
        self.PreviewOilBorder_ColoredCanvas.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewOilBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewOilText_Label = Label(  text = '100',
                                            width = int(186 / 100 * PreviewSize),
                                            height = int(96 / 100 * PreviewSize),
                                            font_size = int(50 / 100 * PreviewSize),
                                            valign = 'top',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewOilText_Label.text_size = self.PreviewOilText_Label.size
        self.PreviewOilText_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewOilText_Label.height - (2 / 100 * PreviewSize)]
        
        self.PreviewOilTitle_Label = Label( text = 'Oil (°C)',
                                            width = int(186 / 100 * PreviewSize),
                                            height = int(90 / 100 * PreviewSize),
                                            font_size = int(23 / 100 * PreviewSize),
                                            valign = 'bottom',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewOilTitle_Label.text_size = self.PreviewOilTitle_Label.size
        self.PreviewOilTitle_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewOilTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewOil_Layout.add_widget(self.PreviewOilBorder_ColoredCanvas)
        self.PreviewOil_Layout.add_widget(self.PreviewOilText_Label)
        self.PreviewOil_Layout.add_widget(self.PreviewOilTitle_Label)

        ##########################################################################################
        # TC                                                                                     #
        ##########################################################################################

        self.PreviewTc_Layout = RelativeLayout( width = ((DashboardWidth / 100 ) * PreviewSize),
                                                height = ((DashboardHeight / 100 ) * PreviewSize),
                                                size_hint = [None, None],
                                                pos_hint = {'x': 0, 'y': 0})

        self.PreviewTcBorder_ColoredCanvas = Custom.ColoredCanvas(  width = int(186 / 100 * PreviewSize),
                                                                    height = int(96 / 100 * PreviewSize),
                                                                    size_hint = [None, None])
        self.PreviewTcBorder_ColoredCanvas.pos = [self.PreviewOilBorder_ColoredCanvas.pos[0] + self.PreviewOilBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewTcBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewTcText_Label = Label(   text = '3',
                                            width = int(186 / 100 * PreviewSize),
                                            height = int(96 / 100 * PreviewSize),
                                            font_size = int(50 / 100 * PreviewSize),
                                            valign = 'top',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTcText_Label.text_size = self.PreviewTcText_Label.size
        self.PreviewTcText_Label.pos = [self.PreviewOilBorder_ColoredCanvas.pos[0] + self.PreviewOilBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewTcText_Label.height - (2 / 100 * PreviewSize)]
        
        self.PreviewTcTitle_Label = Label(  text = 'TC',
                                            width = int(186 / 100 * PreviewSize),
                                            height = int(90 / 100 * PreviewSize),
                                            font_size = int(23 / 100 * PreviewSize),
                                            valign = 'bottom',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewTcTitle_Label.text_size = self.PreviewTcTitle_Label.size
        self.PreviewTcTitle_Label.pos = [self.PreviewOilBorder_ColoredCanvas.pos[0] + self.PreviewOilBorder_ColoredCanvas.width + 2, self.PreviewRpmBorder_ColoredCanvas.pos[1] - self.PreviewTcTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewTc_Layout.add_widget(self.PreviewTcBorder_ColoredCanvas)
        self.PreviewTc_Layout.add_widget(self.PreviewTcText_Label)
        self.PreviewTc_Layout.add_widget(self.PreviewTcTitle_Label)

        ##########################################################################################
        # Water temperature                                                                      #
        ##########################################################################################

        self.PreviewWater_Layout = RelativeLayout(  width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewWaterBorder_ColoredCanvas = Custom.ColoredCanvas(   width = int(186 / 100 * PreviewSize),
                                                                        height = int(96 / 100 * PreviewSize),
                                                                        size_hint = [None, None])
        self.PreviewWaterBorder_ColoredCanvas.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewOilBorder_ColoredCanvas.pos[1] - self.PreviewWaterBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewWaterText_Label = Label(    text = '91',
                                                width = int(186 / 100 * PreviewSize),
                                                height = int(96 / 100 * PreviewSize),
                                                font_size = int(50 / 100 * PreviewSize),
                                                valign = 'top',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewWaterText_Label.text_size = self.PreviewWaterText_Label.size
        self.PreviewWaterText_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewOilBorder_ColoredCanvas.pos[1] - self.PreviewWaterText_Label.height - (2 / 100 * PreviewSize)]
        
        self.PreviewWaterTitle_Label = Label(   text = 'Water (°C)',
                                                width = int(186 / 100 * PreviewSize),
                                                height = int(90 / 100 * PreviewSize),
                                                font_size = int(23 / 100 * PreviewSize),
                                                valign = 'bottom',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewWaterTitle_Label.text_size = self.PreviewWaterTitle_Label.size
        self.PreviewWaterTitle_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewOilBorder_ColoredCanvas.pos[1] - self.PreviewWaterTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewWater_Layout.add_widget(self.PreviewWaterBorder_ColoredCanvas)
        self.PreviewWater_Layout.add_widget(self.PreviewWaterText_Label)
        self.PreviewWater_Layout.add_widget(self.PreviewWaterTitle_Label)

        ##########################################################################################
        # ABS                                                                                    #
        ##########################################################################################

        self.PreviewAbs_Layout = RelativeLayout( width = ((DashboardWidth / 100 ) * PreviewSize),
                                                height = ((DashboardHeight / 100 ) * PreviewSize),
                                                size_hint = [None, None],
                                                pos_hint = {'x': 0, 'y': 0})

        self.PreviewAbsBorder_ColoredCanvas = Custom.ColoredCanvas( width = int(186 / 100 * PreviewSize),
                                                                    height = int(96 / 100 * PreviewSize),
                                                                    size_hint = [None, None])
        self.PreviewAbsBorder_ColoredCanvas.pos = [self.PreviewWaterBorder_ColoredCanvas.pos[0] + self.PreviewWaterBorder_ColoredCanvas.width + 2, self.PreviewTcBorder_ColoredCanvas.pos[1] - self.PreviewAbsBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewAbsText_Label = Label(  text = '1',
                                            width = int(186 / 100 * PreviewSize),
                                            height = int(96 / 100 * PreviewSize),
                                            font_size = int(50 / 100 * PreviewSize),
                                            valign = 'top',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewAbsText_Label.text_size = self.PreviewAbsText_Label.size
        self.PreviewAbsText_Label.pos = [self.PreviewWaterBorder_ColoredCanvas.pos[0] + self.PreviewWaterBorder_ColoredCanvas.width + 2, self.PreviewTcBorder_ColoredCanvas.pos[1] - self.PreviewAbsText_Label.height - (2 / 100 * PreviewSize)]
        
        self.PreviewAbsTitle_Label = Label( text = 'ABS',
                                            width = int(186 / 100 * PreviewSize),
                                            height = int(90 / 100 * PreviewSize),
                                            font_size = int(23 / 100 * PreviewSize),
                                            valign = 'bottom',
                                            halign = 'center',
                                            size_hint = [None, None],
                                            color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewAbsTitle_Label.text_size = self.PreviewAbsTitle_Label.size
        self.PreviewAbsTitle_Label.pos = [self.PreviewWaterBorder_ColoredCanvas.pos[0] + self.PreviewWaterBorder_ColoredCanvas.width + 2, self.PreviewTcBorder_ColoredCanvas.pos[1] - self.PreviewAbsTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewAbs_Layout.add_widget(self.PreviewAbsBorder_ColoredCanvas)
        self.PreviewAbs_Layout.add_widget(self.PreviewAbsText_Label)
        self.PreviewAbs_Layout.add_widget(self.PreviewAbsTitle_Label)

        ##########################################################################################
        # Tyre wear                                                                              #
        ##########################################################################################

        self.PreviewTyreWear_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewTyreWearBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(186 / 100 * PreviewSize),
                                                                            height = int(144 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewTyreWearBorder_ColoredCanvas.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewWaterBorder_ColoredCanvas.pos[1] - self.PreviewTyreWearBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewTyreWearText1_Label = Label(    text = '91.0  91.8',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(144 / 100 * PreviewSize),
                                                    font_size = int(35 / 100 * PreviewSize),
                                                    valign = 'top',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTyreWearText1_Label.text_size = self.PreviewTyreWearText1_Label.size
        self.PreviewTyreWearText1_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewWaterBorder_ColoredCanvas.pos[1] - self.PreviewTyreWearText1_Label.height - (8 / 100 * PreviewSize)]

        self.PreviewTyreWearText2_Label = Label(    text = '92.7  93.4',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(144 / 100 * PreviewSize),
                                                    font_size = int(35 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTyreWearText2_Label.text_size = self.PreviewTyreWearText2_Label.size
        self.PreviewTyreWearText2_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewWaterBorder_ColoredCanvas.pos[1] - self.PreviewTyreWearText2_Label.height + (6 / 100 * PreviewSize)]

        self.PreviewTyreWearTitle_Label = Label(    text = 'Tyre Wear',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = int(144 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'middle',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewTyreWearTitle_Label.text_size = self.PreviewTyreWearTitle_Label.size
        self.PreviewTyreWearTitle_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewWaterBorder_ColoredCanvas.pos[1] - self.PreviewTyreWearTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewTyreWear_Layout.add_widget(self.PreviewTyreWearBorder_ColoredCanvas)
        self.PreviewTyreWear_Layout.add_widget(self.PreviewTyreWearText1_Label)
        self.PreviewTyreWear_Layout.add_widget(self.PreviewTyreWearText2_Label)
        self.PreviewTyreWear_Layout.add_widget(self.PreviewTyreWearTitle_Label)

        ##########################################################################################
        # Time                                                                                   #
        ##########################################################################################

        self.PreviewTime_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = ((DashboardHeight / 100 ) * PreviewSize),
                                                    size_hint = [None, None],
                                                    pos_hint = {'x': 0, 'y': 0})

        self.PreviewTimeBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(186 / 100 * PreviewSize),
                                                                        height = int(144 / 100 * PreviewSize),
                                                                        size_hint = [None, None])
        self.PreviewTimeBorder_ColoredCanvas.pos = [self.PreviewTyreWearBorder_ColoredCanvas.pos[0] + self.PreviewTyreWearBorder_ColoredCanvas.width + 2, self.PreviewAbsBorder_ColoredCanvas.pos[1] - self.PreviewTimeBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewTimeText1_Label = Label(    text = '08:42',
                                                width = int(186 / 100 * PreviewSize),
                                                height = int(144 / 100 * PreviewSize),
                                                font_size = int(35 / 100 * PreviewSize),
                                                valign = 'top',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTimeText1_Label.text_size = self.PreviewTimeText1_Label.size
        self.PreviewTimeText1_Label.pos = [self.PreviewTyreWearBorder_ColoredCanvas.pos[0] + self.PreviewTyreWearBorder_ColoredCanvas.width + 2, self.PreviewAbsBorder_ColoredCanvas.pos[1] - self.PreviewTimeText1_Label.height - (8 / 100 * PreviewSize)]

        self.PreviewTimeText2_Label = Label(    text = '03:23:23',
                                                width = int(186 / 100 * PreviewSize),
                                                height = int(144 / 100 * PreviewSize),
                                                font_size = int(35 / 100 * PreviewSize),
                                                valign = 'bottom',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTimeText2_Label.text_size = self.PreviewTimeText2_Label.size
        self.PreviewTimeText2_Label.pos = [self.PreviewTyreWearBorder_ColoredCanvas.pos[0] + self.PreviewTyreWearBorder_ColoredCanvas.width + 2, self.PreviewAbsBorder_ColoredCanvas.pos[1] - self.PreviewTimeText2_Label.height + (6 / 100 * PreviewSize)]

        self.PreviewTimeTitle_Label = Label(    text = 'Time',
                                                width = int(186 / 100 * PreviewSize),
                                                height = int(144 / 100 * PreviewSize),
                                                font_size = int(23 / 100 * PreviewSize),
                                                valign = 'middle',
                                                halign = 'center',
                                                size_hint = [None, None],
                                                color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewTimeTitle_Label.text_size = self.PreviewTimeTitle_Label.size
        self.PreviewTimeTitle_Label.pos = [self.PreviewTyreWearBorder_ColoredCanvas.pos[0] + self.PreviewTyreWearBorder_ColoredCanvas.width + 2, self.PreviewAbsBorder_ColoredCanvas.pos[1] - self.PreviewTimeTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewTime_Layout.add_widget(self.PreviewTimeBorder_ColoredCanvas)
        self.PreviewTime_Layout.add_widget(self.PreviewTimeText1_Label)
        self.PreviewTime_Layout.add_widget(self.PreviewTimeText2_Label)
        self.PreviewTime_Layout.add_widget(self.PreviewTimeTitle_Label)

        ##########################################################################################
        # Tyre temperature                                                                       #
        ##########################################################################################

        self.PreviewTyreTemp_Layout = RelativeLayout(   width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewTyreTempBorder_ColoredCanvas = Custom.ColoredCanvas(    width = int(186 / 100 * PreviewSize),
                                                                            height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewTyreTempBorder_ColoredCanvas.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewTyreWearBorder_ColoredCanvas.pos[1] - self.PreviewTyreTempBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewTyreTempText1_Label = Label(    text = '77    82',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                    font_size = int(35 / 100 * PreviewSize),
                                                    valign = 'top',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTyreTempText1_Label.text_size = self.PreviewTyreTempText1_Label.size
        self.PreviewTyreTempText1_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewTyreWearBorder_ColoredCanvas.pos[1] - self.PreviewTyreTempText1_Label.height - (8 / 100 * PreviewSize)]

        self.PreviewTyreTempText2_Label = Label(    text = '79    81',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                    font_size = int(35 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTyreTempText2_Label.text_size = self.PreviewTyreTempText2_Label.size
        self.PreviewTyreTempText2_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewTyreWearBorder_ColoredCanvas.pos[1] - self.PreviewTyreTempText2_Label.height + (6 / 100 * PreviewSize)]

        self.PreviewTyreTempTitle_Label = Label(    text = 'Tyre Temp',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'middle',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewTyreTempTitle_Label.text_size = self.PreviewTyreTempTitle_Label.size
        self.PreviewTyreTempTitle_Label.pos = [self.PreviewGearBorder_ColoredCanvas.pos[0] + self.PreviewGearBorder_ColoredCanvas.width + 2, self.PreviewTyreWearBorder_ColoredCanvas.pos[1] - self.PreviewTyreTempTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewTyreTemp_Layout.add_widget(self.PreviewTyreTempBorder_ColoredCanvas)
        self.PreviewTyreTemp_Layout.add_widget(self.PreviewTyreTempText1_Label)
        self.PreviewTyreTemp_Layout.add_widget(self.PreviewTyreTempText2_Label)
        self.PreviewTyreTemp_Layout.add_widget(self.PreviewTyreTempTitle_Label)

        ##########################################################################################
        # Tyre pressure                                                                          #
        ##########################################################################################

        self.PreviewTyrePress_Layout = RelativeLayout(  width = ((DashboardWidth / 100 ) * PreviewSize),
                                                        height = ((DashboardHeight / 100 ) * PreviewSize),
                                                        size_hint = [None, None],
                                                        pos_hint = {'x': 0, 'y': 0})

        self.PreviewTyrePressBorder_ColoredCanvas = Custom.ColoredCanvas(   width = int(186 / 100 * PreviewSize),
                                                                            height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                                            size_hint = [None, None])
        self.PreviewTyrePressBorder_ColoredCanvas.pos = [self.PreviewTyreTempBorder_ColoredCanvas.pos[0] + self.PreviewTyreTempBorder_ColoredCanvas.width + 2, self.PreviewTimeBorder_ColoredCanvas.pos[1] - self.PreviewTyrePressBorder_ColoredCanvas.height - (2 / 100 * PreviewSize)]

        self.PreviewTyrePressText1_Label = Label(   text = '26.5  26.5',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                    font_size = int(35 / 100 * PreviewSize),
                                                    valign = 'top',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTyrePressText1_Label.text_size = self.PreviewTyrePressText1_Label.size
        self.PreviewTyrePressText1_Label.pos = [self.PreviewTyreTempBorder_ColoredCanvas.pos[0] + self.PreviewTyreTempBorder_ColoredCanvas.width + 2, self.PreviewTimeBorder_ColoredCanvas.pos[1] - self.PreviewTyrePressText1_Label.height - (8 / 100 * PreviewSize)]

        self.PreviewTyrePressText2_Label = Label(   text = '28.0  28.0',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                    font_size = int(35 / 100 * PreviewSize),
                                                    valign = 'bottom',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActMainTextColor['Color']))
        self.PreviewTyrePressText2_Label.text_size = self.PreviewTyrePressText2_Label.size
        self.PreviewTyrePressText2_Label.pos = [self.PreviewTyreTempBorder_ColoredCanvas.pos[0] + self.PreviewTyreTempBorder_ColoredCanvas.width + 2, self.PreviewTimeBorder_ColoredCanvas.pos[1] - self.PreviewTyrePressText2_Label.height + (6 / 100 * PreviewSize)]

        self.PreviewTyrePressTitle_Label = Label(   text = 'Tyre Press',
                                                    width = int(186 / 100 * PreviewSize),
                                                    height = self.PreviewPositionBorder_ColoredCanvas.pos[1] - (2 / 100 * PreviewSize),
                                                    font_size = int(23 / 100 * PreviewSize),
                                                    valign = 'middle',
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    color = get_color_from_hex(self.Config.ActTitleTextColor['Color']))
        self.PreviewTyrePressTitle_Label.text_size = self.PreviewTyrePressTitle_Label.size
        self.PreviewTyrePressTitle_Label.pos = [self.PreviewTyreTempBorder_ColoredCanvas.pos[0] + self.PreviewTyreTempBorder_ColoredCanvas.width + 2, self.PreviewTimeBorder_ColoredCanvas.pos[1] - self.PreviewTyrePressTitle_Label.height - (2 / 100 * PreviewSize)]

        self.PreviewTyrePress_Layout.add_widget(self.PreviewTyrePressBorder_ColoredCanvas)
        self.PreviewTyrePress_Layout.add_widget(self.PreviewTyrePressText1_Label)
        self.PreviewTyrePress_Layout.add_widget(self.PreviewTyrePressText2_Label)
        self.PreviewTyrePress_Layout.add_widget(self.PreviewTyrePressTitle_Label)

        ##########################################################################################
        # Buttons                                                                                #
        ##########################################################################################
        
        self.PreviewButtons_Layout = GridLayout(    cols = 5,
                                                    width = ((DashboardWidth / 100 ) * PreviewSize),
                                                    height = 4.5 * MainButtonHeight,
                                                    padding = [20, 20, 20, 20],
                                                    spacing = [20, 20],
                                                    size_hint = [None, None])
        self.PreviewButtons_Layout.padding[0] = ((self.PreviewButtons_Layout.width - (self.PreviewButtons_Layout.cols * 100) - ((self.PreviewButtons_Layout.cols - 1) * self.PreviewButtons_Layout.spacing[1])) / 2)

        self.PreviewBlueFlag_Button = Button(   text = 'Blue Flag',
                                                height = MainButtonHeight,
                                                width = 100,
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewBlueFlag_Button.bind(on_press = self.PreviewBlueFlagClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewBlueFlag_Button)

        self.PreviewYellowFlag_Button = Button( text = 'Yellow Flag',
                                                height = MainButtonHeight,
                                                width = 100,
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewYellowFlag_Button.bind(on_press = self.PreviewYellowFlagClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewYellowFlag_Button)

        self.PreviewOrangeFlag_Button = Button( text = 'Orange Flag',
                                                height = MainButtonHeight,
                                                width = 100,
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewOrangeFlag_Button.bind(on_press = self.PreviewOrangeFlagClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewOrangeFlag_Button)

        self.PreviewWhiteFlag_Button = Button(  text = 'White Flag',
                                                height = MainButtonHeight,
                                                width = 100,    
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewWhiteFlag_Button.bind(on_press = self.PreviewWhiteFlagClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewWhiteFlag_Button)

        self.PreviewCheckeredFlag_Button = Button(  text = 'Checkered\nFlag',
                                                    height = MainButtonHeight,
                                                    width = 100,
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    markup = True)
        self.PreviewCheckeredFlag_Button.bind(on_press = self.PreviewCheckeredFlagClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewCheckeredFlag_Button)

        self.PreviewRpmHigh_Button = Button(    text = 'RPM too\nhigh',
                                                height = MainButtonHeight,
                                                width = 100,
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewRpmHigh_Button.bind(on_press = self.PreviewRpmHighClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewRpmHigh_Button)

        self.PreviewFasterCar_Button = Button(  text = 'Faster car\nbehind',
                                                height = MainButtonHeight,
                                                width = 100,
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewFasterCar_Button.bind(on_press = self.PreviewFasterCarClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewFasterCar_Button)

        self.PreviewFuelLow_Button = Button(    text = 'Fuel low',
                                                height = MainButtonHeight,
                                                width = 100,
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewFuelLow_Button.bind(on_press = self.PreviewFuelLowClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewFuelLow_Button)

        self.PreviewDrsAvailable_Button = Button(   text = 'DRS available',
                                                    height = MainButtonHeight,
                                                    width = 100,
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    markup = True)
        self.PreviewDrsAvailable_Button.bind(on_press = self.PreviewDrsAvailableClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewDrsAvailable_Button)

        self.PreviewDrsActive_Button = Button(  text = 'DRS active',
                                                height = MainButtonHeight,
                                                width = 100,
                                                halign = 'center',
                                                size_hint = [None, None],
                                                markup = True)
        self.PreviewDrsActive_Button.bind(on_press = self.PreviewDrsActiveClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewDrsActive_Button)

        self.PreviewAbs_Button = Button(    text = 'ABS active',
                                            halign = 'center',
                                            height = MainButtonHeight,
                                            width = 100,
                                            size_hint = [None, None],
                                            markup = True)
        self.PreviewAbs_Button.bind(on_press = self.PreviewAbsClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewAbs_Button)

        self.PreviewTc_Button = Button( text = 'TC active',
                                        height = MainButtonHeight,
                                        width = 100,
                                        halign = 'center',
                                        size_hint = [None, None],
                                        markup = True)
        self.PreviewTc_Button.bind(on_press = self.PreviewTcClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewTc_Button)

        self.PreviewPersonalBest_Button = Button(   text = 'Personal best',
                                                    halign = 'center',
                                                    height = MainButtonHeight,
                                                    width = 100,
                                                    size_hint = [None, None],
                                                    markup = True)
        self.PreviewPersonalBest_Button.bind(on_press = self.PreviewPersonalBestClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewPersonalBest_Button)

        self.PreviewSessionBest_Button = Button(    text = 'Session best',
                                                    height = MainButtonHeight,
                                                    width = 100,
                                                    halign = 'center',
                                                    size_hint = [None, None],
                                                    markup = True)
        self.PreviewSessionBest_Button.bind(on_press = self.PreviewSessionBestClicked)
        self.PreviewButtons_Layout.add_widget(self.PreviewSessionBest_Button)

        self.PreviewStatus_Layout = GridLayout(cols = 1)
        self.PreviewStatus_Label = Label(   text = '',
                                            width = ((DashboardWidth / 100 ) * PreviewSize),
                                            valign = 'top',
                                            halign = 'center',
                                            bold = True,
                                            size_hint_y = None)
        self.PreviewStatus_Label.text_size = self.PreviewStatus_Label.size
        self.PreviewStatus_Layout.add_widget(self.PreviewStatus_Label)
        
        self.Preview_Layout.add_widget(self.PreviewBackground_ColoredCanvas)
        self.Preview_Layout.add_widget(self.PreviewBackgroundImage_Layout)
        self.Preview_Layout.add_widget(self.PreviewBackgroundFlag_Layout)
        self.Preview_Layout.add_widget(self.PreviewRpm_Layout)
        self.Preview_Layout.add_widget(self.PreviewFuelLeft_Layout)
        self.Preview_Layout.add_widget(self.PreviewFuel_Layout)
        self.Preview_Layout.add_widget(self.PreviewFuelPerLap_Layout)
        self.Preview_Layout.add_widget(self.PreviewLapDelta_Layout)
        self.Preview_Layout.add_widget(self.PreviewFuelRequired_Layout)
        self.Preview_Layout.add_widget(self.PreviewLapTime_Layout)
        self.Preview_Layout.add_widget(self.PreviewActualStint_Layout)
        self.Preview_Layout.add_widget(self.PreviewGear_Layout)
        self.Preview_Layout.add_widget(self.PreviewSpeed_Layout)
        self.Preview_Layout.add_widget(self.PreviewPosition_Layout)
        self.Preview_Layout.add_widget(self.PreviewGap_Layout)
        self.Preview_Layout.add_widget(self.PreviewOil_Layout)
        self.Preview_Layout.add_widget(self.PreviewTc_Layout)
        self.Preview_Layout.add_widget(self.PreviewWater_Layout)
        self.Preview_Layout.add_widget(self.PreviewAbs_Layout)
        self.Preview_Layout.add_widget(self.PreviewTyreWear_Layout)
        self.Preview_Layout.add_widget(self.PreviewTime_Layout)
        self.Preview_Layout.add_widget(self.PreviewTyreTemp_Layout)
        self.Preview_Layout.add_widget(self.PreviewTyrePress_Layout)


        self.RightSide_Layout.add_widget(self.Preview_Layout)
        self.RightSide_Layout.add_widget(self.PreviewButtons_Layout)
        self.RightSide_Layout.add_widget(self.PreviewStatus_Layout)

        ##########################################################################################
        #                                                                                        #
        # Buttons                                                                                #
        #                                                                                        #
        ##########################################################################################

        self.AcButtons_Layout = GridLayout(    cols = 3,
                                                padding = [150, 10],
                                                width = Window.size[0],
                                                size_hint = [None, None])
        self.AcButtons_Layout.pos[1] = self.MainFooter_Label.height + 10
        
        self.Backup_Button = Button(    text = 'Create backup',
                                        height = MainButtonHeight,
                                        width = 200,
                                        halign = 'center',
                                        size_hint = [None, None],
                                        markup = True)
        # set spacing of buttons layout:
        # 1 Window, 3 buttons, 2 paddings in X (one on the left side of the window and one on the right side). 2 spaces needed (one between buttons 1 and 2 and one between buttons 2 and 3)
        # --> (Window size - (3 * button width) - (2 * layout X padding)) / 2
        self.AcButtons_Layout.spacing = [int((Window.size[0] - (3 * self.Backup_Button.width) - (2 * self.AcButtons_Layout.padding[0])) / 2),20]
        self.AcButtons_Layout.height = 2 * MainButtonHeight + 3 * self.AcButtons_Layout.padding[1]

        self.Backup_Button.bind(on_press = self.BackupClicked)
        self.AcButtons_Layout.add_widget(self.Backup_Button)

        self.Reload_Button = Button(    text = 'Reload actual\nconfiguration',
                                        height = MainButtonHeight,
                                        width = 200,
                                        halign = 'center',
                                        size_hint = [None, None],
                                        markup = True)
        self.Reload_Button.bind(on_press = self.ReloadClicked)
        self.AcButtons_Layout.add_widget(self.Reload_Button)

        self.Save_Button = Button(  text = 'Save configuration',
                                    height = MainButtonHeight,
                                    width = 200,
                                    halign = 'center',
                                    size_hint = [None, None],
                                    markup = True)
        self.Save_Button.bind(on_press = self.SaveClicked)
        self.AcButtons_Layout.add_widget(self.Save_Button)
        
        self.RestoreBackup_Button = Button( text = 'Restore backup',
                                            height = MainButtonHeight,
                                            width = 200,
                                            halign = 'center',
                                            size_hint = [None, None],
                                            markup = True)
        self.RestoreBackup_Button.bind(on_press = self.RestoreClicked)
        self.AcButtons_Layout.add_widget(self.RestoreBackup_Button)
        
        self.LoadDefaults_Button = Button(  text = 'Load default\nconfiguration',
                                            height = MainButtonHeight,
                                            width = 200,
                                            halign = 'center',
                                            size_hint = [None, None],
                                            markup = True)
        self.LoadDefaults_Button.bind(on_press = self.LoadDefaultsClicked)
        self.AcButtons_Layout.add_widget(self.LoadDefaults_Button)

        self.Quit_Button = Button(  text = 'Quit',
                                    height = MainButtonHeight,
                                    width = 200,
                                    halign = 'center',
                                    size_hint = [None, None],
                                    markup = True)
        self.Quit_Button.bind(on_press = self.QuitClicked)
        self.AcButtons_Layout.add_widget(self.Quit_Button)

        self.MainStatus_Layout = GridLayout(    cols = 1,
                                                padding = [0, 5, 0, 5],
                                                width = Window.size[0],
                                                height = MainConfigLayoutGridHeight / 2,
                                                size_hint = [None, None])
        self.MainStatus_Layout.pos[1] = self.AcButtons_Layout.height + self.MainFooter_Label.height + 10
        self.MainStatus_Label = Label(  text = 'Startup...',
                                        halign = 'center',
                                        valign = 'top',
                                        height = MainConfigLayoutGridHeight / 2,
                                        font_size = MainLabelTextSize,
                                        color = get_color_from_hex(MessageColor),
                                        bold = True,
                                        size_hint_y = None)

        self.MainStatus_Layout.add_widget(self.MainStatus_Label)

        if not self.Config.ReadOk:
            self.MainStatusUpdateCounter = -5
            if (self.Config.ReadResult != ''):
                self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                self.MainStatus_Label.text = self.Config.ReadResult
            else:
                self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                self.MainStatus_Label.text = 'Error reading config files. Is ARIS Configurator in the correct folder? Are the configuration files there?'

        self.Restore_Layout = GridLayout(   cols = 1,
                                            height = MainConfigLayoutGridHeight,
                                            width = MainConfigLayoutGridWidth,
                                            size_hint = [None, None])

        self.LeftSide_Layout.add_widget(self.ConfigPageDesign1_Layout)
        self.LeftSide_Layout.add_widget(self.ConfigPageDesign2_Layout)

        self.LeftSideMain_Layout.add_widget(self.LeftSidePageButtons_Layout)
        self.LeftSideMain_Layout.add_widget(self.LeftSide_Layout)

        self.AcMain_Layout.add_widget(self.LeftSideMain_Layout)
        self.AcMain_Layout.add_widget(self.RightSide_Layout)

        self.Main_Layout.add_widget(self.MainTitle_Label)
        self.Main_Layout.add_widget(self.AcMain_Layout)
        self.Main_Layout.add_widget(self.AcButtons_Layout)
        self.Main_Layout.add_widget(self.MainStatus_Layout)
        self.Main_Layout.add_widget(self.MainFooter_Label)

        self.AcMain_Layout.disabled = True
        self.AcButtons_Layout.disabled = True
        Clock.schedule_once(self.LoadGraphics, 0.1)
        return self.Main_Layout

    def Page1ButtonClicked(self, *args):
        # set actual page variable, clear all widgets on the left side and place widgets for selected page and highlight the button for the selected page
        self.Page = 1
        self.LeftSide_Layout.clear_widgets()
        self.Page1_Button.background_color = (0.55, 0.55, 0.95, 1.0)
        self.Page2_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page3_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page4_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.LeftSide_Layout.add_widget(self.ConfigPageDesign1_Layout)
        self.LeftSide_Layout.add_widget(self.ConfigPageDesign2_Layout)
        Custom.DebugPrint(DebugMode, 'Page switched: ' + str(self.Page))

    def Page2ButtonClicked(self, *args):
        # set actual page variable, clear all widgets on the left side and place widgets for selected page and highlight the button for the selected page
        self.Page = 2
        self.LeftSide_Layout.clear_widgets()
        self.Page1_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page2_Button.background_color = (0.55, 0.55, 0.95, 1.0)
        self.Page3_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page4_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.LeftSide_Layout.add_widget(self.ConfigPageFunctions1_Layout)
        Custom.DebugPrint(DebugMode, 'Page switched: ' + str(self.Page))

    def Page3ButtonClicked(self, *args):
        # set actual page variable, clear all widgets on the left side and place widgets for selected page and highlight the button for the selected page
        self.Page = 3
        self.LeftSide_Layout.clear_widgets()
        self.Page1_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page2_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page3_Button.background_color = (0.55, 0.55, 0.95, 1.0)
        self.Page4_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        # not present at the moment: self.LeftSide_Layout.add_widget(self.ConfigPageFunctions2_Layout)
        Custom.DebugPrint(DebugMode, 'Page switched: ' + str(self.Page))

    def Page4ButtonClicked(self, *args):
        # set actual page variable, clear all widgets on the left side and place widgets for selected page and highlight the button for the selected page
        self.Page = 4
        self.LeftSide_Layout.clear_widgets()
        self.Page1_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page2_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page3_Button.background_color = (0.55, 0.55, 0.55, 1.0)
        self.Page4_Button.background_color = (0.55, 0.55, 0.95, 1.0)
        # not present at the moment: self.LeftSide_Layout.add_widget(self.ConfigPageFunctions3_Layout)
        Custom.DebugPrint(DebugMode, 'Page switched: ' + str(self.Page))

    def LoadPreviewSchedules(self, *args):
        # reset update counters and schedule preview update to be be done
        self.PreviewUpdateRpmCounter = 0
        self.PreviewUpdateBackgroundCounter = 0
        Clock.schedule_interval(self.UpdatePreviewBackground, 0.1)
        Clock.schedule_interval(self.UpdatePreviewRpm, 0.1)
        Clock.schedule_interval(self.UpdateColors, 0.1)
    
    def UnloadPreviewSchedules(self, *args):
        Clock.unschedule(self.UpdatePreviewBackground)
        Clock.unschedule(self.UpdatePreviewRpm)
        Clock.unschedule(self.UpdateColors)

    def LoadGraphics(self, *args):
        self.PreviewBackground_ColoredCanvas.DrawRectangle( Color=get_color_from_hex(self.Config.ActBgColor['Color']))
        self.PreviewRpmBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelLeftBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelPerLapBorder_ColoredCanvas.DrawRectangle(   Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewLapDeltaBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelRequiredBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewLapTimeBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewActualStintBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewGearBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewSpeedBorder_ColoredCanvas.DrawRectangle(    Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewPositionBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewGapBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewOilBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTcBorder_ColoredCanvas.DrawRectangle(   Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewWaterBorder_ColoredCanvas.DrawRectangle(    Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewAbsBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTyreWearBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTimeBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTyreTempBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTyrePressBorder_ColoredCanvas.DrawRectangle(    Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))

        if VisualDesignHints:
            self.WelcomeMsgSpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.FasterCarBehindSpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.LastLapDisplaySpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.ShowFlagsSpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.FlagsBlinkingSpare_ColoredWidget.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.RpmLimitSpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.DrsSpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.BackgroundImageActiveSpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))
            self.ShowRefillRequiredSpare_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#FF0000FF'))

        Clock.schedule_interval(self.UpdateMainStatus, 1.0)
        Clock.schedule_interval(self.UpdatePreviewStatus, 1.0)
        self.Reload()
        if (self.Config.ReadOk):
            self.AcMain_Layout.disabled = False
            self.AcButtons_Layout.disabled = False
        else:
            self.AcMain_Layout.disabled = True
            self.AcButtons_Layout.disabled = False
            self.Backup_Button.disabled = True
            self.Save_Button.disabled = True

    def UpdateMainStatus(self, *args):
        if (self.MainStatus_Label.text != 'Select a backup file to restore...') and (self.MainStatus_Label.text != 'Select a target folder for the backup...'):
            self.MainStatusUpdateCounter += 1
            if (self.MainStatusUpdateCounter > 5):
                self.MainStatus_Label.color = get_color_from_hex(MessageColor)
                self.MainStatus_Label.text = ''
                self.MainStatusUpdateCounter = 0

    def UpdatePreviewStatus(self, *args):
        self.PreviewStatusUpdateCounter += 1
        if (self.PreviewStatusUpdateCounter > 5):
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)
            self.PreviewStatus_Label.text = ''
            self.PreviewStatusUpdateCounter = 0

    def UpdatePreviewBackground(self, *args):
        self.PreviewUpdateBackgroundCounter += 1
        self.PreviewUpdateBackgroundEndCounter += 1
        self.PreviewBackground_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.Config.ActBgColor['Color']))
        if self.PreviewShowFlagBlue:
            if (self.Config.ActFlagsBlinking):
                self.PreviewBackgroundBlink = 2
            else:
                self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\BlueFlag.png'
        elif self.PreviewShowFlagCheckered:
            if (self.Config.ActFlagsBlinking):
                self.PreviewBackgroundBlink = 2
            else:
                self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\CheckeredFlag.png'
        elif self.PreviewShowFlagFasterCar:
            if (self.Config.ActFlagsBlinking):
                self.PreviewBackgroundBlink = 2
            else:
                self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\FasterCarBehind.png'
        elif self.PreviewShowFlagFuel:
            self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\FuelLow.png'
        elif self.PreviewShowFlagOrange:
            if (self.Config.ActFlagsBlinking):
                self.PreviewBackgroundBlink = 2
            else:
                self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\OrangeFlag.png'
        elif self.PreviewShowFlagRpm:
            if (self.Config.ActFlagsBlinking):
                self.PreviewBackgroundBlink = 3
            else:
                self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\RPMTooHigh.png'
        elif (self.Config.ActRedlineType == 'blue RPM graph with background image'):
            if ((self.PreviewRpmColor1 == '#00BFFFFF') and ((self.Config.ActRpmType == 'angular elements') or (self.Config.ActRpmType == 'round elements'))):
                # show background image if rpm display is blue
                if (self.Config.ActFlagsBlinking):
                    self.PreviewBackgroundBlink = 3
                else:
                    self.PreviewBackgroundBlink = 1
                self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\RPMTooHigh.png'
            elif ((self.PreviewRpmColorLinearGauge == '#00BFFFFF') and (self.Config.ActRpmType == 'linear gauge')):
                # show background image if rpm gauge is blue
                if (self.Config.ActFlagsBlinking):
                    self.PreviewBackgroundBlink = 3
                else:
                    self.PreviewBackgroundBlink = 1
                self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\RPMTooHigh.png'
            else:
                self.PreviewBackgroundBlink = 0
        elif (self.Config.ActRedlineType == 'background image'):
            if (self.PreviewUpdateRpmCounter >= 30):
                # show background image
                if (self.Config.ActFlagsBlinking):
                    self.PreviewBackgroundBlink = 3
                else:
                    self.PreviewBackgroundBlink = 1
                self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\RPMTooHigh.png'
            else:
                self.PreviewBackgroundBlink = 0
        elif self.PreviewShowFlagWhite:
            if (self.Config.ActFlagsBlinking):
                self.PreviewBackgroundBlink = 2
            else:
                self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\WhiteFlag.png'
        elif self.PreviewShowFlagYellow:
            if (self.Config.ActFlagsBlinking):
                self.PreviewBackgroundBlink = 2
            else:
                self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\YellowFlag.png'
        elif self.PreviewShowDrsAvailable:
            self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\DRSAvailable.png'
        elif self.PreviewShowDrsActive:
            self.PreviewBackgroundBlink = 1
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\DRSActive.png'
        else:
            self.PreviewBackgroundBlink = 0
            self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\BlueFlag.png'

        if (self.PreviewBackgroundBlink == 1):
            self.PreviewBackgroundFlag_Image.opacity = 1.0
        elif (self.PreviewBackgroundBlink == 2):
            if (self.PreviewUpdateBackgroundCounter <= 1):
                self.PreviewBackgroundFlag_Image.opacity = 1.0
            elif (self.PreviewUpdateBackgroundCounter == 5):
                self.PreviewBackgroundFlag_Image.opacity = 0.0
            elif (self.PreviewUpdateBackgroundCounter >= 10):
                self.PreviewUpdateBackgroundCounter = 0
        elif (self.PreviewBackgroundBlink == 3):
            if (self.PreviewUpdateBackgroundCounter <= 1):
                self.PreviewBackgroundFlag_Image.opacity = 1.0
            elif (self.PreviewUpdateBackgroundCounter == 2):
                self.PreviewBackgroundFlag_Image.opacity = 0.0
            elif (self.PreviewUpdateBackgroundCounter >= 3):
                self.PreviewUpdateBackgroundCounter = 0
        else:
            self.PreviewUpdateBackgroundCounter = 0
            self.PreviewBackgroundFlag_Image.opacity = 0.0
        
        if self.PreviewUpdateBackgroundEndCounter >= 50:
            self.PreviewUpdateBackgroundEndCounter = 0
            self.PreviewBackgroundFlag_Image.opacity = 0.0
            self.PreviewBackgroundBlink = 0
            self.PreviewShowFlagBlue = False
            self.PreviewShowFlagCheckered = False
            self.PreviewShowFlagFasterCar = False
            self.PreviewShowFlagFuel = False
            self.PreviewShowFlagOrange = False
            self.PreviewShowFlagRpm = False
            self.PreviewShowFlagWhite = False
            self.PreviewShowFlagYellow = False
            self.PreviewShowDrsAvailable = False
            self.PreviewShowDrsActive = False

    def UpdatePreviewRpm(self, *args):
        self.PreviewUpdateRpmCounter += 1
        
        if (self.PreviewUpdateRpmCounter <= 1):
            self.PreviewRpmColor1 = '#00000000'
            self.PreviewRpmColor2 = '#00000000'
            self.PreviewRpmColor3 = '#00000000'
            self.PreviewRpmColor4 = '#00000000'
            self.PreviewRpmColor5 = '#00000000'
            self.PreviewRpmColor6 = '#00000000'
            self.PreviewRpmColor7 = '#00000000'
            self.PreviewRpmColor8 = '#00000000'
            self.PreviewRpmColor9 = '#00000000'
            self.PreviewRpmColor10 = '#00000000'
            self.PreviewRpmColorLinearGauge = '#008000FF'

        if (self.PreviewUpdateRpmCounter == 3):
            if (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#00000000'
                self.PreviewRpmColor3 = '#00000000'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 6):
            if (self.Config.ActRpmDirection == 'outer to inner') or (self.Config.ActRpmDirection == 'inner to outer'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#00000000'
                self.PreviewRpmColor3 = '#00000000'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#008000FF'
            elif (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#00000000'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 9):
            if (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 12):
            if (self.Config.ActRpmDirection == 'outer to inner') or (self.Config.ActRpmDirection == 'inner to outer'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#00000000'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#008000FF'
                self.PreviewRpmColor10 = '#008000FF'
            elif (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#008000FF'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 15):
            self.PreviewRpmColorLinearGauge = '#FFFF00FF'
            if (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#008000FF'
                self.PreviewRpmColor5 = '#FFFF00FF'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 18):
            if (self.Config.ActRpmDirection == 'outer to inner') or (self.Config.ActRpmDirection == 'inner to outer'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#FFFF00FF'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#FFFF00FF'
                self.PreviewRpmColor9 = '#008000FF'
                self.PreviewRpmColor10 = '#008000FF'
            elif (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#008000FF'
                self.PreviewRpmColor5 = '#FFFF00FF'
                self.PreviewRpmColor6 = '#FFFF00FF'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 21):
            if (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#008000FF'
                self.PreviewRpmColor5 = '#FFFF00FF'
                self.PreviewRpmColor6 = '#FFFF00FF'
                self.PreviewRpmColor7 = '#FFFF00FF'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 24):
            if (self.Config.ActRpmDirection == 'outer to inner') or (self.Config.ActRpmDirection == 'inner to outer'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#FFFF00FF'
                self.PreviewRpmColor4 = '#FFFF00FF'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#FFFF00FF'
                self.PreviewRpmColor8 = '#FFFF00FF'
                self.PreviewRpmColor9 = '#008000FF'
                self.PreviewRpmColor10 = '#008000FF'
            elif (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#008000FF'
                self.PreviewRpmColor5 = '#FFFF00FF'
                self.PreviewRpmColor6 = '#FFFF00FF'
                self.PreviewRpmColor7 = '#FFFF00FF'
                self.PreviewRpmColor8 = '#FFFF00FF'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 27):
            self.PreviewRpmColorLinearGauge = '#FF0000FF'
            if (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#008000FF'
                self.PreviewRpmColor5 = '#FFFF00FF'
                self.PreviewRpmColor6 = '#FFFF00FF'
                self.PreviewRpmColor7 = '#FFFF00FF'
                self.PreviewRpmColor8 = '#FFFF00FF'
                self.PreviewRpmColor9 = '#FF0000FF'
                self.PreviewRpmColor10 = '#00000000'

        elif (self.PreviewUpdateRpmCounter == 30):
            if (self.Config.ActRpmDirection == 'outer to inner') or (self.Config.ActRpmDirection == 'inner to outer'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#FFFF00FF'
                self.PreviewRpmColor4 = '#FFFF00FF'
                self.PreviewRpmColor5 = '#FF0000FF'
                self.PreviewRpmColor6 = '#FF0000FF'
                self.PreviewRpmColor7 = '#FFFF00FF'
                self.PreviewRpmColor8 = '#FFFF00FF'
                self.PreviewRpmColor9 = '#008000FF'
                self.PreviewRpmColor10 = '#008000FF'
            elif (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#008000FF'
                self.PreviewRpmColor2 = '#008000FF'
                self.PreviewRpmColor3 = '#008000FF'
                self.PreviewRpmColor4 = '#008000FF'
                self.PreviewRpmColor5 = '#FFFF00FF'
                self.PreviewRpmColor6 = '#FFFF00FF'
                self.PreviewRpmColor7 = '#FFFF00FF'
                self.PreviewRpmColor8 = '#FFFF00FF'
                self.PreviewRpmColor9 = '#FF0000FF'
                self.PreviewRpmColor10 = '#FF0000FF'

        elif (self.PreviewUpdateRpmCounter == 33):
            if ((self.Config.ActRedlineType == 'blue RPM graph') or (self.Config.ActRedlineType == 'blue RPM graph with background image')):
                self.PreviewRpmColorLinearGauge = '#00BFFFFF'
            if ((self.Config.ActRedlineType == 'blue RPM graph') or (self.Config.ActRedlineType == 'blue RPM graph with background image')) and (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#00BFFFFF'
                self.PreviewRpmColor2 = '#00BFFFFF'
                self.PreviewRpmColor3 = '#00BFFFFF'
                self.PreviewRpmColor4 = '#00BFFFFF'
                self.PreviewRpmColor5 = '#00BFFFFF'
                self.PreviewRpmColor6 = '#00BFFFFF'
                self.PreviewRpmColor7 = '#00BFFFFF'
                self.PreviewRpmColor8 = '#00BFFFFF'
                self.PreviewRpmColor9 = '#00BFFFFF'
                self.PreviewRpmColor10 = '#00BFFFFF'

        elif (self.PreviewUpdateRpmCounter == 36):
            if ((self.Config.ActRedlineType == 'blue RPM graph') or (self.Config.ActRedlineType == 'blue RPM graph with background image')) and (self.Config.ActRpmDirection == 'left to right'):
                pass
            elif ((self.Config.ActRedlineType == 'blue RPM graph') or (self.Config.ActRedlineType == 'blue RPM graph with background image')) and ((self.Config.ActRpmDirection == 'outer to inner') or (self.Config.ActRpmDirection == 'inner to outer')):
                self.PreviewRpmColor1 = '#00BFFFFF'
                self.PreviewRpmColor2 = '#00BFFFFF'
                self.PreviewRpmColor3 = '#00BFFFFF'
                self.PreviewRpmColor4 = '#00BFFFFF'
                self.PreviewRpmColor5 = '#00BFFFFF'
                self.PreviewRpmColor6 = '#00BFFFFF'
                self.PreviewRpmColor7 = '#00BFFFFF'
                self.PreviewRpmColor8 = '#00BFFFFF'
                self.PreviewRpmColor9 = '#00BFFFFF'
                self.PreviewRpmColor10 = '#00BFFFFF'
            else:
                self.PreviewRpmColor1 = '#00000000'
                self.PreviewRpmColor2 = '#00000000'
                self.PreviewRpmColor3 = '#00000000'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'
                self.PreviewRpmColorLinearGauge = '#008000FF'
                self.PreviewUpdateRpmCounter = 0

        elif (self.PreviewUpdateRpmCounter == 39):
            if ((self.Config.ActRedlineType == 'blue RPM graph') or (self.Config.ActRedlineType == 'blue RPM graph with background image')) and (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmColor1 = '#00000000'
                self.PreviewRpmColor2 = '#00000000'
                self.PreviewRpmColor3 = '#00000000'
                self.PreviewRpmColor4 = '#00000000'
                self.PreviewRpmColor5 = '#00000000'
                self.PreviewRpmColor6 = '#00000000'
                self.PreviewRpmColor7 = '#00000000'
                self.PreviewRpmColor8 = '#00000000'
                self.PreviewRpmColor9 = '#00000000'
                self.PreviewRpmColor10 = '#00000000'
                self.PreviewRpmColorLinearGauge = '#008000FF'
                self.PreviewUpdateRpmCounter = 0
            else:
                pass

        elif (self.PreviewUpdateRpmCounter >= 42):
            self.PreviewRpmColor1 = '#00000000'
            self.PreviewRpmColor2 = '#00000000'
            self.PreviewRpmColor3 = '#00000000'
            self.PreviewRpmColor4 = '#00000000'
            self.PreviewRpmColor5 = '#00000000'
            self.PreviewRpmColor6 = '#00000000'
            self.PreviewRpmColor7 = '#00000000'
            self.PreviewRpmColor8 = '#00000000'
            self.PreviewRpmColor9 = '#00000000'
            self.PreviewRpmColor10 = '#00000000'
            self.PreviewRpmColorLinearGauge = '#008000FF'
            self.PreviewUpdateRpmCounter = 0

        if (self.Config.ActRpmType == 'angular elements'):
            self.PreviewRpm1_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor1), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm2_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor2), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm3_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor3), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm4_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor4), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm5_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor5), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm6_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor6), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm7_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor7), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm8_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor8), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm9_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor9), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm10_ColoredCanvas.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColor10), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))

            self.PreviewRpmLinearGauge_Label.DrawRectangle(Color=get_color_from_hex('#00000000'))
        elif (self.Config.ActRpmType == 'round elements'):
            self.PreviewRpm1_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm1_ColoredCanvas.x + (self.PreviewRpm1_ColoredCanvas.width / 2), CenterY = self.PreviewRpm1_ColoredCanvas.y + (self.PreviewRpm1_ColoredCanvas.height / 2), Radius = (self.PreviewRpm1_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor1), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm2_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm2_ColoredCanvas.x + (self.PreviewRpm2_ColoredCanvas.width / 2), CenterY = self.PreviewRpm2_ColoredCanvas.y + (self.PreviewRpm2_ColoredCanvas.height / 2), Radius = (self.PreviewRpm2_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor2), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm3_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm3_ColoredCanvas.x + (self.PreviewRpm3_ColoredCanvas.width / 2), CenterY = self.PreviewRpm3_ColoredCanvas.y + (self.PreviewRpm3_ColoredCanvas.height / 2), Radius = (self.PreviewRpm3_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor3), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm4_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm4_ColoredCanvas.x + (self.PreviewRpm4_ColoredCanvas.width / 2), CenterY = self.PreviewRpm4_ColoredCanvas.y + (self.PreviewRpm4_ColoredCanvas.height / 2), Radius = (self.PreviewRpm4_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor4), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm5_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm5_ColoredCanvas.x + (self.PreviewRpm5_ColoredCanvas.width / 2), CenterY = self.PreviewRpm5_ColoredCanvas.y + (self.PreviewRpm5_ColoredCanvas.height / 2), Radius = (self.PreviewRpm5_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor5), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm6_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm6_ColoredCanvas.x + (self.PreviewRpm6_ColoredCanvas.width / 2), CenterY = self.PreviewRpm6_ColoredCanvas.y + (self.PreviewRpm6_ColoredCanvas.height / 2), Radius = (self.PreviewRpm6_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor6), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm7_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm7_ColoredCanvas.x + (self.PreviewRpm7_ColoredCanvas.width / 2), CenterY = self.PreviewRpm7_ColoredCanvas.y + (self.PreviewRpm7_ColoredCanvas.height / 2), Radius = (self.PreviewRpm7_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor7), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm8_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm8_ColoredCanvas.x + (self.PreviewRpm8_ColoredCanvas.width / 2), CenterY = self.PreviewRpm8_ColoredCanvas.y + (self.PreviewRpm8_ColoredCanvas.height / 2), Radius = (self.PreviewRpm8_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor8), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm9_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm9_ColoredCanvas.x + (self.PreviewRpm9_ColoredCanvas.width / 2), CenterY = self.PreviewRpm9_ColoredCanvas.y + (self.PreviewRpm9_ColoredCanvas.height / 2), Radius = (self.PreviewRpm9_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor9), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpm10_ColoredCanvas.DrawCircle(CenterX = self.PreviewRpm10_ColoredCanvas.x + (self.PreviewRpm10_ColoredCanvas.width / 2), CenterY = self.PreviewRpm10_ColoredCanvas.y + (self.PreviewRpm10_ColoredCanvas.height / 2), Radius = (self.PreviewRpm10_ColoredCanvas.height / 2), Color=get_color_from_hex(self.PreviewRpmColor10), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))

            self.PreviewRpmLinearGauge_Label.DrawRectangle(Color=get_color_from_hex('#00000000'))
        elif (self.Config.ActRpmType == 'linear gauge'):
            
            self.PreviewRpm1_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm2_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm3_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm4_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm5_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm6_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm7_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm8_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm9_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpm10_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))

            self.PreviewRpmLinearGauge_Label.DrawRectangle(Color=get_color_from_hex(self.PreviewRpmColorLinearGauge))

            if (self.Config.ActRpmDirection == 'left to right'):
                self.PreviewRpmLinearGauge_Label.width = int(80 / 100 * PreviewSize) + (((int(846 / 100 * PreviewSize) * self.PreviewUpdateRpmCounter) / 42))
                self.PreviewRpmLinearGauge_Label.pos[0] = int(36 / 100 * PreviewSize)
            elif (self.Config.ActRpmDirection == 'inner to outer'):
                self.PreviewRpmLinearGauge_Label.width = (int(80 / 100 * PreviewSize) / 2) + (((int(846 / 100 * PreviewSize) * self.PreviewUpdateRpmCounter) / 42))
                self.PreviewRpmLinearGauge_Label.pos[0] = ((self.PreviewRpm5_ColoredCanvas.pos[0] + self.PreviewRpm6_ColoredCanvas.pos[0]) / 2) - (self.PreviewRpmLinearGauge_Label.width / 2) + (int(80 / 100 * PreviewSize) / 2)
    
    def UpdateColors(self, *args):

        self.PreviewRpmBorder_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'), BorderWidth = 1, BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))

        if (self.Config.ActRpmType == 'angular elements') or (self.Config.ActRpmType == 'round elements'):
            self.PreviewRpmLinearGaugeSep1_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep2_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep3_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep4_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep5_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep6_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep7_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep8_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep9_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep10_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
            self.PreviewRpmLinearGaugeSep11_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'))
        elif (self.Config.ActRpmType == 'linear gauge'):
            self.PreviewRpmLinearGaugeSep1_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep2_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep3_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep4_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep5_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep6_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep7_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep8_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep9_ColoredCanvas.DrawRectangle( Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep10_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewRpmLinearGaugeSep11_ColoredCanvas.DrawRectangle(Color=get_color_from_hex('#00000000'),
                                                                        BorderWidth = 1,
                                                                        BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))



        self.PreviewRpmBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelLeftBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelPerLapBorder_ColoredCanvas.DrawRectangle(   Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewLapDeltaBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewFuelRequiredBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewLapTimeBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewActualStintBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewGearBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewSpeedBorder_ColoredCanvas.DrawRectangle(    Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewPositionBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewGapBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewOilBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTcBorder_ColoredCanvas.DrawRectangle(   Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewWaterBorder_ColoredCanvas.DrawRectangle(    Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewAbsBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTyreWearBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTimeBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                            Color=get_color_from_hex('#00000000'),
                                                            BorderWidth = 1,
                                                            BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTyreTempBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        self.PreviewTyrePressBorder_ColoredCanvas.DrawRectangle(    Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex('#00000000'),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))

        self.PreviewFuelLeftText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewFuelText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewFuelPerLapText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewFuelLastLapText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewLapDeltaText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewFuelRequiredText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewLapTimeText1_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewLapTimeText2_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewActualStintText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewGearText_Label.color = get_color_from_hex(self.Config.ActGearTextColor['Color'])
        self.PreviewSpeedText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewPositionText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewGapText1_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewGapText2_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewOilText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTcText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewWaterText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewAbsText_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTyreWearText1_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTyreWearText2_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTimeText1_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTimeText2_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTyreTempText1_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTyreTempText2_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTyrePressText1_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])
        self.PreviewTyrePressText2_Label.color = get_color_from_hex(self.Config.ActMainTextColor['Color'])

        self.PreviewFuelLeftTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewFuelTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewFuelPerLapTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewLapDeltaTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewFuelRequiredTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewLapTimeTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewActualStintTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewPositionTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewGapTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewOilTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewTcTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewWaterTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewAbsTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewTyreWearTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewTimeTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewTyreTempTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])
        self.PreviewTyrePressTitle_Label.color = get_color_from_hex(self.Config.ActTitleTextColor['Color'])

        self.PreviewUpdateLapDeltaCounter += 1
        
        if self.PreviewShowPersonalBest:
            self.PreviewLapDeltaBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex(self.Config.ActPersonalBestColor['Color']),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewLapTimeBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex(self.Config.ActPersonalBestColor['Color']),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        elif self.PreviewShowSessionBest:
            self.PreviewLapDeltaBorder_ColoredCanvas.DrawRectangle( Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex(self.Config.ActSessionBestColor['Color']),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            self.PreviewLapTimeBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                    Color=get_color_from_hex(self.Config.ActSessionBestColor['Color']),
                                                                    BorderWidth = 1,
                                                                    BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        else:
            self.PreviewUpdateLapDeltaCounter = 0
            
        if self.PreviewUpdateLapDeltaCounter >= 50:
            self.PreviewUpdateLapDeltaCounter = 0
            self.PreviewShowPersonalBest = False
            self.PreviewShowSessionBest = False

        self.PreviewUpdateTcCounter += 1
        if not self.PreviewShowTc:
            self.PreviewUpdateTcCounter = 0
            self.PreviewTcBorder_ColoredCanvas.DrawRectangle(   Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        elif  ((int((random.random()) * 1000) % 2) == 0):
            self.PreviewTcBorder_ColoredCanvas.DrawRectangle(   Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex(self.Config.ActTcColor['Color']),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
            
        
        if self.PreviewUpdateTcCounter >= 50:
            self.PreviewUpdateTcCounter = 0
            self.PreviewShowTc = False

        self.PreviewUpdateAbsCounter += 1
        if not self.PreviewShowAbs:
            self.PreviewUpdateAbsCounter = 0
            self.PreviewAbsBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex('#00000000'),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        elif  ((int((random.random()) * 1000) % 2) == 0):
            self.PreviewAbsBorder_ColoredCanvas.DrawRectangle(  Radius = self.Config.ActBorderRadius,
                                                                Color=get_color_from_hex(self.Config.ActAbsColor['Color']),
                                                                BorderWidth = 1,
                                                                BorderColor = get_color_from_hex(self.Config.ActSepColor['Color']))
        
        if self.PreviewUpdateAbsCounter >= 50:
            self.PreviewUpdateAbsCounter = 0
            self.PreviewShowAbs = False

    def PreviewBlueFlagClicked(self, *args):

        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = self.Config.ActShowFlags
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowFlags:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Flags are currently not activated. Activate them on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)

    def PreviewCheckeredFlagClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = self.Config.ActShowFlags
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowFlags:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Flags are currently not activated. Activate them on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)

    def PreviewFasterCarClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = self.Config.ActShowFlags and self.Config.ActShowFasterCarBehind
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowFlags:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Flags are currently not activated. Activate them on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        elif not self.Config.ActShowFasterCarBehind:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Showing faster car behind is currently not activated. Activate it on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)

    def PreviewFuelLowClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = True
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

    def PreviewOrangeFlagClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = self.Config.ActShowFlags
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowFlags:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Flags are currently not activated. Activate them on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)

    def PreviewRpmHighClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = self.Config.ActShowRpmLimit
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowRpmLimit:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Showing RPM limit is currently not activated. Activate it on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)

    def PreviewWhiteFlagClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = self.Config.ActShowFlags
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowFlags:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Flags are currently not activated. Activate them on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)
    
    def PreviewYellowFlagClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = self.Config.ActShowFlags
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowFlags:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Flags are currently not activated. Activate them on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)

    def PreviewDrsAvailableClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = self.Config.ActShowDrs
        self.PreviewShowDrsActive = False

        if not self.Config.ActShowDrs:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Showing DRS information is currently not activated. Activate it on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)
    
    def PreviewDrsActiveClicked(self, *args):
            
        self.PreviewUpdateBackgroundEndCounter = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = self.Config.ActShowDrs

        if not self.Config.ActShowDrs:
            self.PreviewStatusUpdateCounter = 0
            self.PreviewStatus_Label.text = 'Showing DRS information is currently not activated. Activate it on the left side first'
            self.PreviewStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.PreviewStatus_Label.text = ''
            self.PreviewStatus_Label.color = get_color_from_hex(MessageColor)
    
    def PreviewAbsClicked(self, *args):
            
        self.PreviewUpdateAbsCounter = 0
        self.PreviewShowAbs = True
        self.PreviewShowTc = False
    
    def PreviewTcClicked(self, *args):
            
        self.PreviewUpdateTcCounter = 0
        self.PreviewShowAbs = False
        self.PreviewShowTc = True
    
    def PreviewPersonalBestClicked(self, *args):
            
        self.PreviewUpdateLapDeltaCounter = 0
        self.PreviewShowPersonalBest = True
        self.PreviewShowSessionBest = False
    
    def PreviewSessionBestClicked(self, *args):
            
        self.PreviewUpdateLapDeltaCounter = 0
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = True

    def RpmTypeDropdownClicked(self, spinner, text):
            
        self.Config.ActRpmType = self.RpmType_Spinner.text.replace('\n', ' ')
        Custom.DebugPrint(DebugMode, 'RPM type selection: ' + self.Config.ActRpmType)

        self.RpmDirection_Layout.clear_widgets()
        self.RpmDirection_Layout.add_widget(self.RpmDirection_Label)
        
        if ((self.Config.ActRpmType == 'angular elements') or (self.Config.ActRpmType == 'round elements')):
            self.ActRpmDirectionElements = ['outer to inner', 'left to right']
            self.RpmDirection_Layout.add_widget(self.RpmDefaultDirection_Spinner)
            self.RpmDefaultDirection_Spinner.bind(text = self.RpmDirectionDropdownClicked)
            self.Config.ActRpmDirection = self.RpmDefaultDirection_Spinner.text.replace('\n', ' ')
        else:
            self.ActRpmDirectionElements = ['inner to outer', 'left to right']
            self.RpmDirection_Layout.add_widget(self.RpmGaugeDirection_Spinner)
            self.RpmGaugeDirection_Spinner.bind(text = self.RpmDirectionDropdownClicked)
            self.Config.ActRpmDirection = self.RpmGaugeDirection_Spinner.text.replace('\n', ' ')
        Custom.DebugPrint(DebugMode, 'RPM direction after RPM type selection: ' + self.Config.ActRpmDirection)
    
    def RpmDirectionDropdownClicked(self, spinner, text):
            
        if ((self.Config.ActRpmType == 'angular elements') or (self.Config.ActRpmType == 'round elements')):
            self.Config.ActRpmDirection = self.RpmDefaultDirection_Spinner.text.replace('\n', ' ')
        else:
            self.Config.ActRpmDirection = self.RpmGaugeDirection_Spinner.text.replace('\n', ' ')
        Custom.DebugPrint(DebugMode, 'RPM direction selection: ' + self.Config.ActRpmDirection)

    def RedlineTypeDropdownClicked(self, spinner, text):
            
        self.Config.ActRedlineType = self.RedlineType_Spinner.text.replace('\n', ' ')
        Custom.DebugPrint(DebugMode, 'Redline type selection: ' + self.Config.ActRedlineType)
    
    def WelcomeMsgChkBoxActive(self, instance, value):
            
        if value:
            if (self.Config.ActWelcomeMsgDuration <= 0):
                if (float(self.Config.WelcomeMsgDuration) > 0):
                    # check box is set, but actual value is 0 and value in config file is valid -> take value from config file
                    self.Config.ActWelcomeMsgDuration = float(self.Config.WelcomeMsgDuration)
                else:
                    # check box is set, but actual value is 0 and value in config file is invalid -> take default value
                    self.Config.ActWelcomeMsgDuration = self.Config.DefaultWelcomeMsgDuration

            # if welcome message is activated get the actual value and dislpay the slider
            self.WelcomeMsg_Slider.value = self.Config.ActWelcomeMsgDuration
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgSpare1_Label)
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgDescription_Label)
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgSpare2_Label)
            self.WelcomeMsg2_Layout.add_widget(self.WelcomeMsgSlider_Layout)
            Custom.DebugPrint(DebugMode, 'Welcome message activated')
        else:
            # if welcome message is disabled remove the slider and set the value to 0
            self.Config.ActWelcomeMsgDuration = 0.0
            self.WelcomeMsg2_Layout.clear_widgets()
            Custom.DebugPrint(DebugMode, 'Welcome message deactivated')
    
    def WelcomeMsgLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.WelcomeMsg_ChkBox.active = not self.WelcomeMsg_ChkBox.active
    
    def WelcomMsgSliderChange(self, instance, value):
        # when slider is changed take the actual slider value and copy it to the confg value
        self.Config.ActWelcomeMsgDuration = value
        self.WelcomeMsgDescription_Label.text = 'Show welcome message after starting the dashboard for ' + str(self.Config.ActWelcomeMsgDuration) + ' seconds'
        Custom.DebugPrint(DebugMode, 'Welcome message time: ' + str(self.Config.ActWelcomeMsgDuration) + ' seconds')

    def BorderRadiusSliderChange(self, instance, value):
        # when slider is changed take the actual slider value and copy it to the confg value
        self.Config.ActBorderRadius = value
        self.BorderRadiusDescription_Label.text = 'Corner radius for borders: ' + str(int(self.Config.ActBorderRadius))
        Custom.DebugPrint(DebugMode, 'Border radius: ' + str(self.Config.ActBorderRadius))
    
    def FasterCarBehindChkBoxActive(self, instance, value):
            
        if value:
            self.PreviewShowFlagFasterCar = False
            if (self.Config.ActFasterCarBehindThreshold <= 0):
                if (float(self.Config.FasterCarBehindThreshold) > 0):
                    # check box is set, but actual value is 0 and value in config file is valid -> take value from config file
                    self.Config.ActFasterCarBehindThreshold = float(self.Config.FasterCarBehindThreshold)
                else:
                    # check box is set, but actual value is 0 and value in config file is invalid -> take default value
                    self.Config.ActFasterCarBehindThreshold = self.Config.DefaultFasterCarBehindThreshold
            
            # if faster car behind is activated get the actual value and dislpay the slider
            self.Config.ActShowFasterCarBehind = True
            self.FasterCarBehind_Slider.value = self.Config.ActFasterCarBehindThreshold
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindSpare1_Label)
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindDescription_Label)
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindSpare2_Label)
            self.FasterCarBehind2_Layout.add_widget(self.FasterCarBehindSlider_Layout)
            Custom.DebugPrint(DebugMode, 'Faster car behind activated')
        else:
            self.PreviewShowFlagFasterCar = False
            # if faster car behind is disabled remove the slider and set the value to false
            self.Config.ActShowFasterCarBehind = False
            self.Config.ActFasterCarBehindThreshold = 0.0
            self.FasterCarBehind2_Layout.clear_widgets()
            Custom.DebugPrint(DebugMode, 'Faster car behind deactivated')
    
    def FasterCarBehindLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.FasterCarBehind_ChkBox.active = not self.FasterCarBehind_ChkBox.active
    
    def FasterCarBehindSliderChange(self, instance, value):
        # when slider is changed take the actual slider value and copy it to the confg value
        self.Config.ActFasterCarBehindThreshold = value
        self.FasterCarBehindDescription_Label.text = 'Show faster car behind if his fastest lap is more than 1/' + str(self.Config.ActFasterCarBehindThreshold) + ' faster than your own'
        Custom.DebugPrint(DebugMode, 'Threshold for faster car behind is 1/' + str(self.Config.ActFasterCarBehindThreshold))
    
    def LastLapDisplayChkBoxActive(self, instance, value):
            
        if value:
            if (self.Config.ActLastLapTimeDisplayDuration <= 0):
                if (float(self.Config.LastLapTimeDisplayDuration) > 0):
                    # check box is set, but actual value is 0 and value in config file is valid -> take value from config file
                    self.Config.ActLastLapTimeDisplayDuration = float(self.Config.LastLapTimeDisplayDuration)
                else:
                    # check box is set, but actual value is 0 and value in config file is invalid -> take default value
                    self.Config.ActLastLapTimeDisplayDuration = self.Config.DefaultLastLapTimeDisplayDuration

            # if last lap display time is activated get the actual value and dislpay the slider
            self.LastLapDisplay_Slider.value = self.Config.ActLastLapTimeDisplayDuration
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplaySpare1_Label)
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplayDescription_Label)
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplaySpare2_Label)
            self.LastLapDisplay2_Layout.add_widget(self.LastLapDisplaySlider_Layout)
            Custom.DebugPrint(DebugMode, 'Last lap time display activated')
        else:
            # if welcome message is disabled remove the slider and set the value to 0
            self.Config.ActLastLapTimeDisplayDuration = 0.0
            self.LastLapDisplay2_Layout.clear_widgets()
            Custom.DebugPrint(DebugMode, 'Last lap time display deactivated')
    
    def LastLapDisplayLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.LastLapDisplay_ChkBox.active = not self.LastLapDisplay_ChkBox.active
    
    def LastLapDisplaySliderChange(self, instance, value):
        # when slider is changed take the actual slider value and copy it to the confg value
        self.Config.ActLastLapTimeDisplayDuration = value
        self.LastLapDisplayDescription_Label.text = 'Show last lap time at the beginning of a new lap for ' + str(self.Config.ActLastLapTimeDisplayDuration) + ' seconds'
        Custom.DebugPrint(DebugMode, 'Last lap time display time: ' + str(self.Config.ActLastLapTimeDisplayDuration) + ' seconds')

    def ShowFlagsChkBoxActive(self, instance, value):
            
        if value:
            self.Config.ActShowFlags = True
            Custom.DebugPrint(DebugMode, 'Show flags activated')
            self.PreviewShowFlagBlue = False
            self.PreviewShowFlagCheckered = False
            self.PreviewShowFlagFasterCar = False
            self.PreviewShowFlagOrange = False
            self.PreviewShowFlagWhite = False
            self.PreviewShowFlagYellow = False
        else:
            self.Config.ActShowFlags = False
            Custom.DebugPrint(DebugMode, 'Show flags deactivated')
            self.PreviewShowFlagBlue = False
            self.PreviewShowFlagCheckered = False
            self.PreviewShowFlagFasterCar = False
            self.PreviewShowFlagOrange = False
            self.PreviewShowFlagWhite = False
            self.PreviewShowFlagYellow = False
    
    def ShowFlagsLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.ShowFlags_ChkBox.active = not self.ShowFlags_ChkBox.active
        
    def FlagsBlinkingChkBoxActive(self, instance, value):
            
        if value:
            self.Config.ActFlagsBlinking = True
            Custom.DebugPrint(DebugMode, 'Flags blinking activated')
        else:
            self.Config.ActFlagsBlinking = False
            Custom.DebugPrint(DebugMode, 'Flags blinking deactivated')
    
    def FlagsBlinkingLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.FlagsBlinking_ChkBox.active = not self.FlagsBlinking_ChkBox.active

    def RpmLimitChkBoxActive(self, instance, value):
        self.PreviewShowFlagRpm = False

        if value:
            self.Config.ActShowRpmLimit = True
            Custom.DebugPrint(DebugMode, 'Show RPM limit activated')
        else:
            self.Config.ActShowRpmLimit = False
            Custom.DebugPrint(DebugMode, 'Show RPM limit deactivated')
    
    def RpmLimitLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.RpmLimit_ChkBox.active = not self.RpmLimit_ChkBox.active

    def DrsChkBoxActive(self, instance, value):
            
        if value:
            self.PreviewShowDrsAvailable = False
            self.PreviewShowDrsActive = False
            self.Config.ActShowDrs = True
            Custom.DebugPrint(DebugMode, 'Show DRS activated')
        else:
            self.PreviewShowDrsAvailable = False
            self.PreviewShowDrsActive = False
            self.Config.ActShowDrs = False
            Custom.DebugPrint(DebugMode, 'Show DRS deactivated')
    
    def DrsLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.Drs_ChkBox.active = not self.Drs_ChkBox.active

    def BackgroundImageActiveChkBoxActive(self, instance, value):
            
        if value:
            self.Config.ActBackgroundImageActive = True
            self.PreviewBackgroundImage_Image.opacity = 1.0
            Custom.DebugPrint(DebugMode, 'Background image activated')
        else:
            self.Config.ActBackgroundImageActive= False
            self.PreviewBackgroundImage_Image.opacity = 0.0
            Custom.DebugPrint(DebugMode, 'Background image deactivated')
    
    def BackgroundImageActiveLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.BackgroundImageActive_ChkBox.active = not self.BackgroundImageActive_ChkBox.active

    def ShowRefillRequiredChkBoxActive(self, instance, value):
            
        if value:
            self.Config.ActShowRefillRequired = True
            self.PreviewFuelRequiredTitle_Label.text = 'Refill Required'
            self.PreviewFuelRequiredText_Label.text = '335.9'
            Custom.DebugPrint(DebugMode, 'Show refill required activated')
        else:
            self.Config.ActShowRefillRequired = False
            self.PreviewFuelRequiredTitle_Label.text = 'Fuel Required'
            self.PreviewFuelRequiredText_Label.text = '414.1'
            Custom.DebugPrint(DebugMode, 'Show refill required deactivated')
    
    def ShowRefillRequiredLabelActive(self, *args):
            
        # if label is clicked instead of the checkbox invert the checkbox state
        self.ShowRefillRequired_ChkBox.active = not self.ShowRefillRequired_ChkBox.active

    def CheckForChanges(self):
        self.UnsavedChanges = False
        match self.Config.RpmType:
            case '0':
                if (self.Config.ActRpmType != 'angular elements'):
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'RPM type not saved')
            case '1':
                if (self.Config.ActRpmType != 'round elements'):
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'RPM type not saved')
            case '2':
                if (self.Config.ActRpmType != 'linear gauge'):
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'RPM type not saved')
            case _:
                self.UnsavedChanges = True
                Custom.DebugPrint(DebugMode, 'RPM type (unknown) not saved')

        if ((self.Config.ActRpmType == 'angular elements') or (self.Config.ActRpmType == 'round elements')):
            match self.Config.RpmDirection:
                case '0':
                    if (self.Config.ActRpmDirection != 'outer to inner'):
                        self.UnsavedChanges = True
                        Custom.DebugPrint(DebugMode, 'RPM direction (default) not saved')
                case '1':
                    if (self.Config.ActRpmDirection != 'left to right'):
                        self.UnsavedChanges = True
                        Custom.DebugPrint(DebugMode, 'RPM direction (default) not saved')
                case _:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'RPM direction (default / unknown) not saved')
        elif ((self.Config.ActRpmType == 'linear gauge')):
            match self.Config.RpmDirection:
                case '0':
                    if (self.Config.ActRpmDirection != 'inner to outer'):
                        self.UnsavedChanges = True
                        Custom.DebugPrint(DebugMode, 'RPM direction (linear gauge) not saved')
                case '1':
                    if (self.Config.ActRpmDirection != 'left to right'):
                        self.UnsavedChanges = True
                        Custom.DebugPrint(DebugMode, 'RPM direction (linear gauge) not saved')
                case _:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'RPM direction (linear gauge / unknown) not saved')
        else:
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'RPM direction (unknown) not saved')
        
        match self.Config.RedlineType:
            case '0':
                if (self.Config.ActRedlineType != 'blue RPM graph'):
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Redline type not saved')
            case '1':
                if (self.Config.ActRedlineType != 'blue RPM graph with background image'):
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Redline type not saved')
            case '2':
                if (self.Config.ActRedlineType != 'background image'):
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Redline type not saved')
            case _:
                self.UnsavedChanges = True
                Custom.DebugPrint(DebugMode, 'Redline type (unknown) not saved')

        if (self.Config.BgColor != self.Config.ActBgColor['Color']):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Background color not saved')

        if (self.Config.SepColor != self.Config.ActSepColor['Color']):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Seperator color not saved')

        if (float(self.Config.BorderRadius) != self.Config.ActBorderRadius):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Border radius not saved')

        if (float(self.Config.WelcomeMsgDuration) != self.Config.ActWelcomeMsgDuration):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Welcome message duration not saved')

        match self.Config.ShowFasterCarBehind:
            case '0':
                if self.Config.ActShowFasterCarBehind:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Faster car behind not saved')
            case '1':
                if not self.Config.ActShowFasterCarBehind:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Faster car behind not saved')
            case _:
                Custom.DebugPrint(DebugMode, 'Faster car behind (unknown) not saved')

        match self.Config.ShowFlags:
            case '0':
                if self.Config.ActShowFlags:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show flags not saved')
            case '1':
                if not self.Config.ActShowFlags:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show flags not saved')
            case _:
                Custom.DebugPrint(DebugMode, 'Show flags (unknown) not saved')

        match self.Config.FlagsBlinking:
            case '0':
                if self.Config.ActFlagsBlinking:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Flags blinking not saved')
            case '1':
                if not self.Config.ActFlagsBlinking:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Flags blinking not saved')
            case _:
                Custom.DebugPrint(DebugMode, 'Flags blinking (unknown) not saved')

        match self.Config.ShowRpmLimit:
            case '0':
                if self.Config.ActShowRpmLimit:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show RPM limit not saved')
            case '1':
                if not self.Config.ActShowRpmLimit:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show RPM limit not saved')
            case _:
                Custom.DebugPrint(DebugMode, 'Show RPM limit (unknown) not saved')

        match self.Config.ShowDrs:
            case '0':
                if self.Config.ActShowDrs:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show DRS not saved')
            case '1':
                if not self.Config.ActShowDrs:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show DRS not saved')
            case _:
                Custom.DebugPrint(DebugMode, 'Show DRS (unknown) not saved')

        match self.Config.ShowRefillRequired:
            case '0':
                if self.Config.ActShowRefillRequired:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show refill required not saved')
            case '1':
                if not self.Config.ActShowRefillRequired:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Show refill required not saved')
            case _:
                Custom.DebugPrint(DebugMode, 'Show refill required (unknown) not saved')

        if (float(self.Config.FasterCarBehindThreshold) != self.Config.ActFasterCarBehindThreshold):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Faster car behind threshold not saved')

        if (self.Config.MainTextColor != self.Config.ActMainTextColor['Color']):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Main text color not saved')

        if (self.Config.TitleTextColor != self.Config.ActTitleTextColor['Color']):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Title text color not saved')

        if (self.Config.GearTextColor != self.Config.ActGearTextColor['Color']):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Gear text color not saved')

        if (self.Config.TcColor != self.Config.ActTcColor['Color']):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'TC color not saved')

        if (self.Config.AbsColor != self.Config.ActAbsColor['Color']):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'ABS color not saved')

        if (float(self.Config.LastLapTimeDisplayDuration) != self.Config.ActLastLapTimeDisplayDuration):
            self.UnsavedChanges = True
            Custom.DebugPrint(DebugMode, 'Display last lap time duration not saved')

        match self.Config.BackgroundImageActive:
            case '0':
                if self.Config.ActBackgroundImageActive:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Background image active not saved')
            case '1':
                if not self.Config.ActBackgroundImageActive:
                    self.UnsavedChanges = True
                    Custom.DebugPrint(DebugMode, 'Background image active not saved')
            case _:
                Custom.DebugPrint(DebugMode, 'Background image active (unknown) not saved')

        if not self.UnsavedChanges:
            Custom.DebugPrint(DebugMode, 'No unsaved changes detected')

    def BackupClicked(self, *args):

        if self.ButtonsBlockedRestore:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a file to restore.*')
                wnd.set_foreground()
                return
            except:
                return
        elif self.ButtonsBlockedBackup:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a target folder for the backup.*')
                wnd.set_foreground()
                return
            except:
                return

        self.ButtonsBlockedBackup = True
        
        self.PreviewBackgroundBlink = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False
        
        
        self.MainStatusUpdateCounter = 0
        self.MainStatus_Label.color = get_color_from_hex(MessageColor)
        self.MainStatus_Label.text = 'Select a target folder for the backup...'
        t_Backup = threading.Thread(target = self.CreateBackup)
        t_Backup.name = 'Backup'
        t_Backup.daemon = True
        t_Backup.start()

    def CreateBackup(self, *args):

        self.CheckForChanges()

        if not self.UnsavedChanges:
            target_startfolder = os.path.expanduser('~')
            Custom.DebugPrint(DebugMode, 'Default target folder: ' + str(target_startfolder))
            
            #################################################
            # fix folder for backup not used anymore
            #target_folder = os.environ.get('LOCALAPPDATA')
            
            #if (target_folder != ''):
            #    target_folder = Path(target_folder + '\\ARIS\\Backup')
            #    target_folder.mkdir(parents = True, exist_ok = True)
            #################################################

            target_folder = filedialog.askdirectory(initialdir = target_startfolder, title = 'ARIS Configurator: Select a target folder for the backup')
            target_folder = Path(target_folder)
            
            try:
                if (target_folder.is_dir() and (target_folder != '') and (len(str(target_folder)) > 2)):
                    ARIS_version = self.CheckARIS()
                    if (ARIS_version == '0'):
                        # return if ARIS not found correctly
                        self.ButtonsBlockedBackup = False
                        return
                    Custom.DebugPrint(DebugMode, 'Selected backup target folder: ' + str(target_folder))
                    version_info = '_ARIS' + ARIS_version + '_ARISC' + ARISConfigurator_version
                    version_info = version_info.replace('.', '')
                    version_info = version_info.replace(' ', '')
                    full_targetpath = str(target_folder) + '\\' + datetime.now().strftime('%Y%m%d_%H%M%S') + version_info + '.zip'
                    
                    self.AcMain_Layout.disabled = True
                    self.AcButtons_Layout.disabled = True

                    Custom.Zip.CreateZIP(ARIS_folder + '\\config', full_targetpath)
                    Custom.Zip.AddToZIP(ARIS_folder + '\\background', full_targetpath)

                    CheckZIP_Return = self.CheckZIP(full_targetpath)
                    Custom.DebugPrint(DebugMode, 'Return value for CheckZIP method: ' + str(CheckZIP_Return))

                    if (CheckZIP_Return == 0):
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(OkColor)
                        self.MainStatus_Label.text = 'Backup finished'
                        Custom.DebugPrint(DebugMode, 'Backup finished: ' + full_targetpath)
                    elif (CheckZIP_Return == 1):
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error: Created ZIP file is no valid ARIS backup file'
                    elif (CheckZIP_Return == 2):
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error: Could not open or read ZIP file after backup. Maybe selected file is no valid ZIP file?!'
                    else:
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error: Could not open or read created ZIP file'
                else:
                    self.MainStatusUpdateCounter = 0
                    self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                    self.MainStatus_Label.text = 'Error: Backup folder not found'
                    Custom.DebugPrint(DebugMode, 'Backup aborted or Backup folder not found: ' + target_folder)
            except:
                self.MainStatusUpdateCounter = 0
                self.MainStatus_Label.color = get_color_from_hex(MessageColor)
                self.MainStatus_Label.text = ''
                Custom.DebugPrint(DebugMode, 'Backup aborted or no valid element selected')
        else:
            self.MainStatusUpdateCounter = 0
            self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
            self.MainStatus_Label.text = 'Error: Unsaved changes detected. Please save or reload configuration first'
            Custom.DebugPrint(DebugMode, 'Unsaved changes detected. Please save or reload the settings first')
        
        self.ButtonsBlockedBackup = False
        self.AcMain_Layout.disabled = False
        self.AcButtons_Layout.disabled = False

    def RestoreClicked(self, *args):

        if self.ButtonsBlockedRestore:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a file to restore.*')
                wnd.set_foreground()
                return
            except:
                return
        elif self.ButtonsBlockedBackup:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a target folder for the backup.*')
                wnd.set_foreground()
                return
            except:
                return
        
        self.PreviewBackgroundBlink = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False
        
        self.ButtonsBlockedRestore = True
        self.MainStatusUpdateCounter = 0
        self.MainStatus_Label.color = get_color_from_hex(MessageColor)
        self.MainStatus_Label.text = 'Select a backup file to restore...'
        t_Restore = threading.Thread(target = self.RestoreBackup)
        t_Restore.name = 'Restore'
        t_Restore.daemon = True
        t_Restore.start()

    def RestoreBackup(self, *args):
        source_folder = os.path.expanduser('~')
        source_folder = Path(source_folder)
        #################################################
        # fix folder for backup not used anymore
        #source_folder = os.environ.get('LOCALAPPDATA')
        #if (source_folder != ''):
        #    source_folder = Path(source_folder + '\\ARIS\\Backup')
        #    source_folder.mkdir(parents = True, exist_ok = True)
        #################################################
        Custom.DebugPrint(DebugMode, 'Default source folder: ' + str(source_folder))

        source_file = ''
        source_file = filedialog.askopenfilename(initialdir = source_folder, title = 'ARIS Configurator: Select a file to restore', filetypes = (('ZIP files', '*.zip'), ('all files', '*.*')))
        source_file_ok = False

        try:
            if (source_folder.is_dir()) and (source_file != '') and (len(str(source_file)) > 2):
                ARIS_version = self.CheckARIS()
                if (ARIS_version == '0'):
                    # return if ARIS not found correctly
                    self.ButtonsBlockedRestore = False
                    return

                filename_len = len(source_file)
                if (filename_len > 4):
                    file_ending_slice = slice(filename_len - 4, filename_len)
                    file_ending = source_file[file_ending_slice]
                    if (file_ending.lower() == '.zip'):
                        source_file_ok = True
                    else:
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error restoring configuration: file ending is not .zip'
                else:
                    self.MainStatusUpdateCounter = 0
                    self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                    self.MainStatus_Label.text = 'Error restoring configuration: file ending is not .zip'

                if (source_file_ok):

                    CheckZIP_Return = self.CheckZIP(source_file)
                    Custom.DebugPrint(DebugMode, 'Return value for CheckZIP method: ' + str(CheckZIP_Return))

                    if (CheckZIP_Return == 0):

                        file_path = Path(source_file)
                        if (file_path.is_file()):
                            self.AcMain_Layout.disabled = True
                            self.AcButtons_Layout.disabled = True
                            with zipfile.ZipFile(source_file, 'r') as zip_source:
                                self.MainStatus_Label.color = get_color_from_hex(MessageColor)
                                self.MainStatus_Label.text = 'Restoring backup...'
                                self.RestoringBackup = True
                                zip_source.extractall(ARIS_folder)
                                Custom.DebugPrint(DebugMode, 'Restore complete for file: ' + str(source_file))
                            zip_source.close()
                            Clock.schedule_once(self.Reload)
                        else:
                            self.MainStatusUpdateCounter = 0
                            self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                            self.MainStatus_Label.text = 'Error: Selected file is no ZIP file'
                            Custom.DebugPrint(DebugMode, 'Selected file is no ZIP file: ' + str(source_file))
                    elif (CheckZIP_Return == 1):
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error: Selected ZIP file is no valid ARIS backup file'
                    elif (CheckZIP_Return == 2):
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error: Could not open or read ZIP file. Maybe selected file is no valid ZIP file?!'
                    else:
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error: Could not open or read selected ZIP file'
            else:
                self.MainStatusUpdateCounter = 0
                self.MainStatus_Label.color = get_color_from_hex(MessageColor)
                self.MainStatus_Label.text = ''
                Custom.DebugPrint(DebugMode, 'Restoring aborted or no valid element selected')
        except:
            self.MainStatusUpdateCounter = 0
            self.MainStatus_Label.color = get_color_from_hex(MessageColor)
            self.MainStatus_Label.text = ''
        
        self.ButtonsBlockedRestore = False
        self.AcMain_Layout.disabled = False
        self.AcButtons_Layout.disabled = False

    def CheckZIP(self, file):
        ErrorCode = 0

        file_path = Path(file)
        if (file_path.is_file()):
            try:
                with zipfile.ZipFile(file, 'r') as zip_source:
                    zip_content = zip_source.namelist()
                    zip_content_ok = True
                    if (len(zip_content) > 0):
                        try:
                            if not any('config/design' in Searchstring for Searchstring in zip_content):
                                Custom.DebugPrint(DebugMode, 'config/design not found')
                                zip_content_ok = False
                            if not any('config/functional' in Searchstring for Searchstring in zip_content):
                                Custom.DebugPrint(DebugMode, 'config/functional not found')
                                zip_content_ok = False
                            if not any('background' in Searchstring for Searchstring in zip_content):
                                Custom.DebugPrint(DebugMode, 'config/background not found')
                                zip_content_ok = False
                        except:
                            Custom.DebugPrint(DebugMode, 'Error searching namelist of ZIP file')
                            zip_content_ok = False
                    else:
                        Custom.DebugPrint(DebugMode, 'Length of ZIP file <= 0')
                        zip_content_ok = False
                zip_source.close()

                if (zip_content_ok):
                    ErrorCode = 0
                else:
                    Custom.DebugPrint(DebugMode, 'ZIP file no valid ARIS backup')
                    ErrorCode = 1
            except:
                ErrorCode = 2
                Custom.DebugPrint(DebugMode, 'File is no ZIP file')
        else:
            Custom.DebugPrint(DebugMode, 'Selected object is no file')
            ErrorCode = 99

        return ErrorCode

    def QuitClicked(self, *args):

        if self.ButtonsBlockedRestore:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a file to restore.*')
                wnd.set_foreground()
                return
            except:
                return
        elif self.ButtonsBlockedBackup:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a target folder for the backup.*')
                wnd.set_foreground()
                return
            except:
                return
        
        self.PreviewBackgroundBlink = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False
        
        self.CheckForChanges()
        if self.UnsavedChanges:
            self.UnsavedQuitPopup_Layout = GridLayout(  cols = 1,
                                                        spacing = [10])
            
            self.UnsavedQuitPopupButton_Layout = GridLayout(    cols = 2,
                                                    spacing = [250])
            self.UnsavedQuit_Label = Label( text = 'There are unsaved changes. Really quit?')
            self.UnsavedQuitOk_Button = Button( text = 'OK',
                                                height = MainButtonHeight,
                                                size_hint_y = None)
            self.UnsavedQuitCancel_Button = Button( text = 'Cancel',
                                                    height = MainButtonHeight,
                                                    size_hint_y = None)
            self.UnsavedQuitPopupButton_Layout.add_widget(self.UnsavedQuitOk_Button)
            self.UnsavedQuitPopupButton_Layout.add_widget(self.UnsavedQuitCancel_Button)
            self.UnsavedQuitPopup_Layout.add_widget(self.UnsavedQuit_Label)
            self.UnsavedQuitPopup_Layout.add_widget(self.UnsavedQuitPopupButton_Layout)
            self.UnsavedQuit_Popup = Popup( title = 'Quit ARIS Configurator?',
                                            size_hint = [None, None],
                                            size = [575, 300],
                                            content = self.UnsavedQuitPopup_Layout,
                                            auto_dismiss = True)
            
            self.UnsavedQuitOk_Button.bind(on_release = lambda x:self.Quit())
            self.UnsavedQuitCancel_Button.bind(on_release = lambda x:self.UnsavedQuit_Popup.dismiss())
            self.UnsavedQuit_Popup.open()
        else:
            self.Quit()
    
    def Quit(self, *args):
        self.MainStatus_Label.color = get_color_from_hex(MessageColor)
        self.MainStatus_Label.text = 'Good bye and have a nice race'
        self.MainStatusUpdateCounter = 0
        Clock.schedule_once(self.stop, 0.5)
    
    def SaveClicked(self, *args):

        if self.ButtonsBlockedRestore:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a file to restore.*')
                wnd.set_foreground()
                return
            except:
                return
        elif self.ButtonsBlockedBackup:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a target folder for the backup.*')
                wnd.set_foreground()
                return
            except:
                return

        self.PreviewBackgroundBlink = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False
            
        self.MainStatusUpdateCounter = 0
        self.MainStatus_Label.color = get_color_from_hex(MessageColor)
        self.MainStatus_Label.text = 'Saving...'

        ARIS_version = self.CheckARIS()
        if (ARIS_version == '0'):
            # return if ARIS not found correctly
            return
        else:
            self.AcMain_Layout.disabled = True
            self.AcButtons_Layout.disabled = True

        self.Config.save(self.Config)
        self.MainStatusUpdateCounter = 0
        if ('Error' in self.Config.SaveResult):
            self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
        elif ('Nothing to save' in self.Config.SaveResult):
            self.MainStatus_Label.color = get_color_from_hex(WarningColor)
        else:
            self.MainStatus_Label.color = get_color_from_hex(OkColor)
        self.MainStatus_Label.text = self.Config.SaveResult

        self.AcMain_Layout.disabled = False
        self.AcButtons_Layout.disabled = False

    def ReloadClicked(self, *args):

        if self.ButtonsBlockedRestore:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a file to restore.*')
                wnd.set_foreground()
                return
            except:
                return
        elif self.ButtonsBlockedBackup:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a target folder for the backup.*')
                wnd.set_foreground()
                return
            except:
                return
        
        self.PreviewBackgroundBlink = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False
        
        ARIS_version = self.CheckARIS()
        if (ARIS_version == '0'):
            # return if ARIS not found correctly
            return
        else:
            self.AcMain_Layout.disabled = True
            self.AcButtons_Layout.disabled = True

        self.MainStatusUpdateCounter = 0
        self.MainStatus_Label.color = get_color_from_hex(MessageColor)
        self.MainStatus_Label.text = 'Reloading...'
        Clock.schedule_once(self.Reload)
    
    def Reload(self, *args):
        self.UnloadPreviewSchedules()

        if not self.LoadingDefaults:
            # only read and set values from config file if loading defaults is not requested (relaoding is requested)

            self.Config.read(self.Config)
            if not self.Config.ReadOk:
                self.AcButtons_Layout.disabled = False
                self.MainStatusUpdateCounter = -5
                self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                self.MainStatus_Label.text = self.Config.ReadResult
                return

        # set RPM type
        self.RpmType_Spinner.text = self.Config.ActRpmType
        self.RpmType_Spinner.values = self.Config.ActRpmTypeElements

        # garbage collect
        self.RpmDirection_Layout.clear_widgets()
        self.BorderRadius_Layout.clear_widgets()
        self.WelcomeMsg1_Layout.clear_widgets()
        if not self.WelcomeMsg_ChkBox.active:
            self.WelcomeMsg2_Layout.clear_widgets()
        self.FasterCarBehind1_Layout.clear_widgets()
        if not self.FasterCarBehind_ChkBox.active:
            self.FasterCarBehind2_Layout.clear_widgets()
        self.LastLapDisplay1_Layout.clear_widgets()
        if not self.LastLapDisplay_ChkBox.active:
            self.LastLapDisplay2_Layout.clear_widgets()
        gc.collect()

        # rebuild RPM direction
        self.RpmDefaultDirection_Spinner.text = self.Config.ActRpmDirectionDefault
        self.RpmDefaultDirection_Spinner.values = self.Config.ActRpmDirectionElementsDefault
        self.RpmGaugeDirection_Spinner.text = self.Config.ActRpmDirectionGauge
        self.RpmGaugeDirection_Spinner.values = self.Config.ActRpmDirectionElementsGauge
        self.RpmDirection_Layout.add_widget(self.RpmDirection_Label)
        if ((self.Config.ActRpmType == 'angular elements') or (self.Config.ActRpmType == 'round elements')):
            self.RpmDirection_Layout.add_widget(self.RpmDefaultDirection_Spinner)
            self.RpmDefaultDirection_Spinner.bind(text = self.RpmDirectionDropdownClicked)
        else:
            self.RpmDirection_Layout.add_widget(self.RpmGaugeDirection_Spinner)
            self.RpmGaugeDirection_Spinner.bind(text = self.RpmDirectionDropdownClicked)
        
        # set redline type
        self.RedlineType_Spinner.text = self.Config.ActRedlineType
        self.RedlineType_Spinner.values = self.Config.ActRedlineTypeElements

        # rebuild border radius
        self.BorderRadius_Slider.value = self.Config.ActBorderRadius

        self.BorderRadius_Layout.add_widget(self.BorderRadiusDescription_Label)
        self.BorderRadius_Layout.add_widget(self.BorderRadius_Slider)

        # rebuild welcome message
        self.WelcomeMsg1_Layout.add_widget(self.WelcomeMsg_ChkBox)
        self.WelcomeMsg1_Layout.add_widget(self.WelcomeMsg_Label)
        self.WelcomeMsg1_Layout.add_widget(self.WelcomeMsgSpare_ColoredCanvas)
        if (self.Config.ActWelcomeMsgDuration > 0):
            self.WelcomeMsg_Slider.value = self.Config.ActWelcomeMsgDuration
            self.WelcomeMsg_ChkBox.active = True
        else:
            self.WelcomeMsg_ChkBox.active = False

        # rebuild faster car behind
        self.FasterCarBehind1_Layout.add_widget(self.FasterCarBehind_ChkBox)
        self.FasterCarBehind1_Layout.add_widget(self.FasterCarBehind_Label)
        self.FasterCarBehind1_Layout.add_widget(self.FasterCarBehindSpare_ColoredCanvas)
        if (self.Config.ActShowFasterCarBehind):
            self.FasterCarBehind_Slider.value = self.Config.ActFasterCarBehindThreshold
            self.FasterCarBehind_ChkBox.active = True
        else:
            self.FasterCarBehind_ChkBox.active = False

        # rebuild last lap time
        self.LastLapDisplay1_Layout.add_widget(self.LastLapDisplay_ChkBox)
        self.LastLapDisplay1_Layout.add_widget(self.LastLapDisplay_Label)
        self.LastLapDisplay1_Layout.add_widget(self.LastLapDisplaySpare_ColoredCanvas)
        if (self.Config.ActLastLapTimeDisplayDuration > 0):
            
            self.LastLapDisplay_Slider.value = self.Config.ActLastLapTimeDisplayDuration
            self.LastLapDisplay_ChkBox.active = True
        else:
            self.LastLapDisplay_ChkBox.active = False

        # rebuild fuel / refill required
        if self.Config.ActShowRefillRequired:
            self.ShowRefillRequired_ChkBox.active = True
        else:
            self.ShowRefillRequired_ChkBox.active = False

        # set/unset show flags
        if self.Config.ActShowFlags:
            self.ShowFlags_ChkBox.active = True
        else:
            self.ShowFlags_ChkBox.active = False

        # set/unset RPM limit
        if self.Config.ActShowRpmLimit:
            self.RpmLimit_ChkBox.active = True
        else:
            self.RpmLimit_ChkBox.active = False

        # set/unset DRS information
        if self.Config.ActShowDrs:
            self.Drs_ChkBox.active = True
        else:
            self.Drs_ChkBox.active = False
        
        # set/unset flags blinking
        if self.Config.ActFlagsBlinking:
            self.FlagsBlinking_ChkBox.active = True
        else:
            self.FlagsBlinking_ChkBox.active = False

        # set/unset Background image
        if self.Config.ActBackgroundImageActive:
            self.BackgroundImageActive_ChkBox.active = True
        else:
            self.BackgroundImageActive_ChkBox.active = False

        # rebuild color pickers
        Custom.Graphics.ColorChooser(self.MainBgColor_Layout, self.Config.ActBgColor, LabelText='Main background color', PopupTitle='Choose background color', WithButton=False, DisableAlpha=True)
        Custom.Graphics.ColorChooser(self.SeperatorColor_Layout, self.Config.ActSepColor, LabelText='Seperator color', PopupTitle='Choose color for seperation lines', WithButton=False, DisableAlpha=False)
        Custom.Graphics.ColorChooser(self.MainTextColor_Layout, self.Config.ActMainTextColor, LabelText='Main text color', PopupTitle='Choose text color', WithButton=False, DisableAlpha=False)
        Custom.Graphics.ColorChooser(self.TitleTextColor_Layout, self.Config.ActTitleTextColor, LabelText='Title text color', PopupTitle='Choose color for the title texts', WithButton=False, DisableAlpha=False)
        Custom.Graphics.ColorChooser(self.GearTextColor_Layout, self.Config.ActGearTextColor, LabelText='Gear text color', PopupTitle='Choose color for the gear indicator', WithButton=False, DisableAlpha=False)
        Custom.Graphics.ColorChooser(self.TcColor_Layout, self.Config.ActTcColor, LabelText='TC active color', PopupTitle='Choose color for the indication that TC is active', WithButton=False, DisableAlpha=False)
        Custom.Graphics.ColorChooser(self.AbsColor_Layout, self.Config.ActAbsColor, LabelText='ABS active color', PopupTitle='Choose color for the indication that ABS is active', WithButton=False, DisableAlpha=False)
        Custom.Graphics.ColorChooser(self.PersonalBestColor_Layout, self.Config.ActPersonalBestColor, LabelText='Personal best color', PopupTitle='Choose color for the personal best lap time / delta (in that session)', WithButton=False, DisableAlpha=False)
        Custom.Graphics.ColorChooser(self.SessionBestColor_Layout, self.Config.ActSessionBestColor, LabelText='Session best color', PopupTitle='Choose color for the session best lap time / delta active', WithButton=False, DisableAlpha=False)

        # load all image files and remove them from cache
        # --> otherwise the image would not be shown correctoly if it was replaced (e.g. by restoring a backup)
        self.PreviewBackgroundImage_Image.remove_from_cache()
        self.PreviewBackgroundImage_Image.source = ARIS_folder + '\\background\\Background.png'
        self.PreviewBackgroundImage_Image.remove_from_cache()
        
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\BlueFlag.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\CheckeredFlag.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\DRSActive.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\DRSAvailable.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\FasterCarBehind.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\FuelLow.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\OrangeFlag.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\RPMTooHigh.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\WhiteFlag.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()
        self.PreviewBackgroundFlag_Image.source = ARIS_folder + '\\background\\YellowFlag.png'
        self.PreviewBackgroundFlag_Image.remove_from_cache()

        self.ButtonsBlockedRestore = False
        self.ButtonsBlockedBackup = False
        self.AcMain_Layout.disabled = False
        self.AcButtons_Layout.disabled = False
        self.Save_Button.disabled = False

        Clock.schedule_once(self.LoadPreviewSchedules, 0.1)

        if (self.MainStatus_Label.text != 'Startup...'):
            if not self.LoadingDefaults and not self.RestoringBackup:
                self.MainStatusUpdateCounter = 0
                self.MainStatus_Label.color = get_color_from_hex(OkColor)
                self.MainStatus_Label.text = 'Reloading configuration files finished'
            elif self.RestoringBackup:
                self.RestoringBackup = False
                self.MainStatusUpdateCounter = 0
                self.MainStatus_Label.color = get_color_from_hex(OkColor)
                self.MainStatus_Label.text = 'Backup restored. Saving configuration is not necessary'
        else:
            self.MainStatusUpdateCounter = 3
            self.MainStatus_Label.color = get_color_from_hex(OkColor)
            self.MainStatus_Label.text = 'Startup finished'

    def LoadDefaultsClicked(self, *args):

        if self.ButtonsBlockedRestore:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a file to restore.*')
                wnd.set_foreground()
                return
            except:
                return
        elif self.ButtonsBlockedBackup:
            try:
                wnd = Custom.WindowManager()
                wnd.find_window_wildcard('.*ARIS Configurator: Select a target folder for the backup.*')
                wnd.set_foreground()
                return
            except:
                return
        
        self.AcMain_Layout.disabled = True
        self.AcButtons_Layout.disabled = True

        self.PreviewBackgroundBlink = 0
        self.PreviewShowFlagBlue = False
        self.PreviewShowFlagCheckered = False
        self.PreviewShowFlagFasterCar = False
        self.PreviewShowFlagFuel = False
        self.PreviewShowFlagOrange = False
        self.PreviewShowFlagRpm = False
        self.PreviewShowFlagWhite = False
        self.PreviewShowFlagYellow = False
        self.PreviewShowAbs = False
        self.PreviewShowTc = False
        self.PreviewShowPersonalBest = False
        self.PreviewShowSessionBest = False
        self.PreviewShowDrsAvailable = False
        self.PreviewShowDrsActive = False
        
        self.LoadingDefaults = True
        self.MainStatusUpdateCounter = 0
        self.MainStatus_Label.color = get_color_from_hex(MessageColor)
        self.MainStatus_Label.text = 'Loading defaults...'
        Clock.schedule_once(self.LoadDefaults, 0.5)

    def LoadDefaults(self, *args):
        # set default values
        self.Config.ActRpmType = self.Config.DefaultRpmType
        self.Config.ActRpmDirection = self.Config.DefaultRpmDirection
        self.Config.ActRedlineType = self.Config.DefaultRedlineType
        self.Config.ActBgColor['Color'] = self.Config.DefaultBgColor
        self.Config.ActSepColor['Color'] = self.Config.DefaultSepColor
        self.Config.ActMainTextColor['Color'] = self.Config.DefaultMainTextColor
        self.Config.ActTitleTextColor['Color'] = self.Config.DefaultTitleTextColor
        self.Config.ActGearTextColor['Color'] = self.Config.DefaultGearTextColor
        self.Config.ActTcColor['Color'] = self.Config.DefaultTcColor
        self.Config.ActAbsColor['Color'] = self.Config.DefaultAbsColor
        self.Config.ActPersonalBestColor['Color'] = self.Config.DefaultPersonalBestColor
        self.Config.ActSessionBestColor['Color'] = self.Config.DefaultSessionBestColor
        self.Config.ActWelcomeMsgDuration = self.Config.DefaultWelcomeMsgDuration
        self.Config.ActShowFasterCarBehind = self.Config.DefaultShowFasterCarBehind
        self.Config.ActFasterCarBehindThreshold = self.Config.DefaultFasterCarBehindThreshold
        self.Config.ActLastLapTimeDisplayDuration = self.Config.DefaultLastLapTimeDisplayDuration
        self.Config.ActLastLapTimeDisplayDuration = self.Config.DefaultLastLapTimeDisplayDuration
        self.Config.ActShowRpmLimit = self.Config.DefaultShowRpmLimit
        self.Config.ActShowDrs = self.Config.DefaultShowDrs
        self.Config.ActShowFlags = self.Config.DefaultShowFlags
        self.Config.ActFlagsBlinking = self.Config.DefaultFlagsBlinking
        self.Config.ActBackgroundImageActive = self.Config.DefaultBackgroundImageActive
        self.Config.ActRpmDirectionDefault = self.Config.DefaultRpmDirectionElementsDefault[0]
        self.Config.ActRpmDirectionElementsDefault = self.Config.DefaultRpmDirectionElementsDefault
        self.Config.ActRpmDirectionGauge = self.Config.DefaultRpmDirectionElementsGauge[0]
        self.Config.ActRpmDirectionElementsGauge = self.Config.DefaultRpmDirectionElementsGauge
        self.Config.ActRedlineTypeElements = self.Config.DefaultRedlineTypeElements
        self.Config.ActRpmTypeElements = self.Config.DefaultRpmTypeElements
        self.Config.ActShowRefillRequired = self.Config.DefaultShowRefillRequired
        self.Config.ActBorderRadius = self.Config.DefaultBorderRadius

        self.Reload()
        self.MainStatusUpdateCounter = 0
        self.MainStatus_Label.color = get_color_from_hex(OkColor)
        self.MainStatus_Label.text = 'Loading default configuration finished. Don\'t forget to save'
        self.LoadingDefaults = False

    def CheckARIS(self, *args):
        ARIS_file = Path(ARIS_folder + '\\ARIS.djson')
        ARIS_version = '0'
        if (ARIS_file.is_file()):
            try:
                with open(ARIS_folder + '\\ARIS.djson', 'r') as file:
                    try:
                        ARISJson = json.load(file)
                        ARIS_version = ARISJson['Metadata']['Description'].replace('ARIS v','')
                        Custom.DebugPrint(DebugMode, 'Checking ARIS successful. Version found ' + ARIS_version)
                    except:
                        self.MainStatusUpdateCounter = 0
                        self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                        self.MainStatus_Label.text = 'Error checking ARIS. Could not read JSON file'
                        Custom.DebugPrint(DebugMode, 'Error checking ARIS. Could not read JSON file ' + ARIS_folder + '\\ARIS.djson')
                        ARIS_version = '0'
            except:
                self.MainStatusUpdateCounter = 0
                self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
                self.MainStatus_Label.text = 'Error checking ARIS. Could not open ARIS.djson'
                Custom.DebugPrint(DebugMode, 'Error checking ARIS. Could not open ' + ARIS_folder + '\\ARIS.djson')
                ARIS_version = '0'
        else:
            self.MainStatusUpdateCounter = 0
            self.MainStatus_Label.color = get_color_from_hex(ErrorColor)
            self.MainStatus_Label.text = 'Error checking ARIS. Object is no file'
            Custom.DebugPrint(DebugMode, 'Error checking ARIS. Object is no file: ' + str(ARIS_file))
            ARIS_version = '0'
        
        return ARIS_version

class ConfigFile:
    # default values
    DefaultRpmTypeElements = ['angular elements', 'round elements', 'linear gauge']
    DefaultRpmDirectionElementsDefault = ['outer to inner', 'left to right']
    DefaultRpmDirectionElementsGauge = ['inner to outer', 'left to right']
    DefaultRedlineTypeElements = ['blue RPM graph', 'blue RPM graph with\nbackground image', 'background image']
    DefaultRpmType = DefaultRpmTypeElements[0]
    DefaultRpmDirection = DefaultRpmDirectionElementsDefault[0]
    DefaultRedlineType = DefaultRedlineTypeElements[0]
    DefaultBgColor = '#000006FF'
    DefaultSepColor = '#808080FF'
    DefaultMainTextColor = '#FFFFFFFF'
    DefaultTitleTextColor = '#FFFF00FF'
    DefaultGearTextColor = '#FF7F50FF'
    DefaultTcColor = '#C71585FF'
    DefaultAbsColor = '#FF8C00FF'
    DefaultSessionBestColor = '#800080FF'
    DefaultPersonalBestColor = '#008000FF'
    DefaultWelcomeMsgDuration = 3.0
    DefaultShowFasterCarBehind = True
    DefaultFasterCarBehindThreshold = 35.0
    DefaultShowFlags = True
    DefaultShowRpmLimit = True
    DefaultShowDrs = False
    DefaultLastLapTimeDisplayDuration = 10.0
    DefaultFlagsBlinking = True
    DefaultBackgroundImageActive = False
    DefaultShowRefillRequired = True
    DefaultBorderRadius = 4

    # init values
    RpmType = 'not loaded'
    RpmDirection = 'not loaded'
    RedlineType = 'not loaded'
    BgColor = '#00000000'
    SepColor = '#00000000'
    MainTextColor = '#00000000'
    TitleTextColor = '#00000000'
    GearTextColor = '#00000000'
    TcColor = '#00000000'
    AbsColor = '#00000000'
    SessionBestColor = '#00000000'
    PersonalBestColor = '#00000000'
    WelcomeMsgDuration = '0.0'
    ShowFasterCarBehind = '0'
    FasterCarBehindThreshold = '0.0'
    ShowFlags = '0'
    ShowRpmLimit = '0'
    ShowDrs = '0'
    LastLapTimeDisplayDuration = '0.0'
    FlagsBlinking = '0'
    BackgroundImageActive = '0'
    ShowRefillRequired = '0'
    BorderRadius = '0'

    ActRpmType = 'not loaded'
    ActRpmTypeElements = ['not loaded']
    ActRpmDirection = 'not loaded'
    ActRpmDirectionDefault = 'not loaded'
    ActRpmDirectionGauge = 'not loaded'
    ActRpmDirectionElementsDefault = ['not loaded']
    ActRpmDirectionElementsGauge = ['not loaded']
    ActRedlineType = 'not loaded'
    ActRedlineTypeElements = ['not loaded']
    ActBgColor = '#00000000'
    ActSepColor = '#00000000'
    ActMainTextColor = '#00000000'
    ActTitleTextColor = '#00000000'
    ActGearTextColor = '#00000000'
    ActTcColor = '#00000000'
    ActAbsColor = '#00000000'
    ActSessionBestColor = '#00000000'
    ActPersonalBestColor = '#00000000'
    ActWelcomeMsgDuration = 0.0
    ActShowFasterCarBehind = False
    ActFasterCarBehindThreshold = 0.0
    ActShowFlags = False
    ActShowRpmLimit = False
    ActShowDrs = False
    ActLastLapTimeDisplayDuration = 0.0
    ActFlagsBlinking = False
    ActBackgroundImageActive = False
    ActShowRefillRequired = False
    ActBorderRadius = 0

    ReadOk = False
    ReadResult = ''
    SaveResult = ''
    
    def __init__(self, **kwargs):
        super(ConfigFile, self).__init__(**kwargs)
        # other init things here

    def read(self):
        ##########################################################################################
        #                                                                                        #
        # Read configuration files                                                               #
        #                                                                                        #
        ##########################################################################################

        self.ReadOk = True
        
        try:
            self.file = open(ARIS_folder + '\\config\\design\\RPM_type.ini', 'r')
            self.RpmType = self.file.read(1)
            self.file.close()

            self.ActRpmTypeElements = ['angular elements', 'round elements', 'linear gauge']
            if (self.RpmType == '0'):
                self.ActRpmType = 'angular elements'
            elif (self.RpmType == '1'):
                self.ActRpmType = 'round elements'
            elif (self.RpmType == '2'):
                self.ActRpmType = 'linear gauge'
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in RPM_type.ini is out of range'

        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read RPM_type.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\RPM_direction.ini', 'r')
            self.RpmDirection = self.file.read(1)
            self.file.close()
            
            self.ActRpmDirectionElementsDefault = ['outer to inner', 'left to right']
            self.ActRpmDirectionElementsGauge = ['inner to outer', 'left to right']
            if (self.RpmDirection == '0'):
                self.ActRpmDirectionDefault = 'outer to inner'
                self.ActRpmDirectionGauge = 'inner to outer'
                if ((self.ActRpmType == 'angular elements') or (self.ActRpmType == 'round elements')):
                    self.ActRpmDirection = self.ActRpmDirectionDefault
                else:
                    self.ActRpmDirection = self.ActRpmDirectionGauge
            elif (self.RpmDirection == '1'):
                self.ActRpmDirectionDefault = 'left to right'
                self.ActRpmDirectionGauge = 'left to right'
                if ((self.ActRpmType == 'angular elements') or (self.ActRpmType == 'round elements')):
                    self.ActRpmDirection = self.ActRpmDirectionDefault
                else:
                    self.ActRpmDirection = self.ActRpmDirectionGauge
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in RPM_direction.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read RPM_direction.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\RedLineIndicatorType.ini', 'r')
            self.RedlineType = self.file.read(1)
            self.file.close()

            self.ActRedlineTypeElements = ['blue RPM graph', 'blue RPM graph with\nbackground image', 'background image']
            if (self.RedlineType == '0'):
                self.ActRedlineType = 'blue RPM graph'
            elif (self.RedlineType == '1'):
                self.ActRedlineType = 'blue RPM graph with\nbackground image'
            elif (self.RedlineType == '2'):
                self.ActRedlineType = 'background image'
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in RedLineIndicatorType.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read RedLineIndicatorType.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\BackgroundColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in BackgroundColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.BgColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read BackgroundColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\SeperatorColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in SeperatorColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.SepColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read SeperatorColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\WelcomeMessageDisplayTime.ini', 'r')
            self.WelcomeMsgDuration = self.file.readline()
            self.file.close()
            self.ActWelcomeMsgDuration = float(self.WelcomeMsgDuration)
            if ((self.ActWelcomeMsgDuration < 0) or (self.ActWelcomeMsgDuration > 99.99)):
                self.ActWelcomeMsgDuration = 3.0
                self.ReadOk = False
                self.ReadResult = 'Error: Value in WelcomeMessageDisplayTime.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read WelcomeMessageDisplayTime.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\functional\\ShowFasterCarBehind.ini', 'r')
            self.ShowFasterCarBehind = self.file.readline()
            self.file.close()
            if (self.ShowFasterCarBehind == '0'):
                self.ActShowFasterCarBehind = False
            elif (self.ShowFasterCarBehind == '1'):
                self.ActShowFasterCarBehind = True
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in ShowFasterCarBehind.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read ShowFasterCarBehind.ini'
        
        try:
            self.file = open(ARIS_folder + '\\config\\functional\\ShowFlags.ini', 'r')
            self.ShowFlags = self.file.readline()
            self.file.close()
            if (self.ShowFlags == '0'):
                self.ActShowFlags = False
            elif (self.ShowFlags == '1'):
                self.ActShowFlags = True
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in ShowFlags.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read ShowFlags.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\functional\\ShowRPMLimit.ini', 'r')
            self.ShowRpmLimit = self.file.readline()
            self.file.close()
            if (self.ShowRpmLimit == '0'):
                self.ActShowRpmLimit = False
            elif (self.ShowRpmLimit == '1'):
                self.ActShowRpmLimit = True
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in ShowRPMLimit.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read ShowRPMLimit.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\functional\\ShowDRS.ini', 'r')
            self.ShowDrs = self.file.readline()
            self.file.close()
            if (self.ShowDrs == '0'):
                self.ActShowDrs = False
            elif (self.ShowDrs == '1'):
                self.ActShowDrs = True
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in ShowDRS.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read ShowDRS.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\functional\\FasterCarBehind_ThresholdFactor.ini', 'r')
            self.FasterCarBehindThreshold = self.file.readline()
            self.file.close()
            self.ActFasterCarBehindThreshold = float(self.FasterCarBehindThreshold)
            if ((self.ActFasterCarBehindThreshold < 1) or (self.ActFasterCarBehindThreshold > 100)):
                self.FasterCarBehindThreshold = 35.0
                self.ReadOk = False
                self.ReadResult = 'Error: Value in FasterCarBehind_ThresholdFactor.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read FasterCarBehind_ThresholdFactor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\TextMainColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in TextMainColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.MainTextColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read TextMainColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\TextTitleColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in TextTitleColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.TitleTextColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read TextTitleColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\TextGearColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in TextGearColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.GearTextColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read TextGearColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\TCColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in TCColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.TcColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read TCColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\ABSColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in ABSColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.AbsColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read ABSColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\PersonalBestColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in PersonalBestColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.PersonalBestColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read PersonalBestColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\SessionBestColor.ini', 'r')
            Color = self.file.readline()
            self.file.close()
            retVal = Custom.Graphics.CheckColorHexCode(Color)
            if (retVal != 0):
                Color = '#00000000'
                self.ReadOk = False
                self.ReadResult = 'Error: Color in SessionBestColor.ini not valid'
            # Change color from ARGB to RGBA as SimHub uses ARGB
            self.SessionBestColor = Custom.Graphics.ArgbToRgba(Color)
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read SessionBestColor.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\functional\\LastLapDisplayTime.ini', 'r')
            self.LastLapTimeDisplayDuration = self.file.readline()
            self.file.close()
            self.ActLastLapTimeDisplayDuration = float(self.LastLapTimeDisplayDuration)
            if ((self.ActLastLapTimeDisplayDuration < 0) or (self.ActLastLapTimeDisplayDuration > 20)):
                self.ActLastLapTimeDisplayDuration = 0.0
                self.ReadOk = False
                self.ReadResult = 'Error: Value in LastLapDisplayTime.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read LastLapDisplayTime.ini'
        
        try:
            self.file = open(ARIS_folder + '\\config\\design\\FlagsBlinking.ini', 'r')
            self.FlagsBlinking = self.file.readline()
            self.file.close()
            if (self.FlagsBlinking == '0'):
                self.ActFlagsBlinking = False
            elif (self.FlagsBlinking == '1'):
                self.ActFlagsBlinking = True
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in FlagsBlinking.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read FlagsBlinking.ini'
        
        try:
            self.file = open(ARIS_folder + '\\config\\design\\BackgroundImageActive.ini', 'r')
            self.BackgroundImageActive = self.file.readline()
            self.file.close()
            if (self.BackgroundImageActive == '0'):
                self.ActBackgroundImageActive = False
            elif (self.BackgroundImageActive == '1'):
                self.ActBackgroundImageActive = True
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in BackgroundImageActive.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read BackgroundImageActive.ini'
        
        try:
            self.file = open(ARIS_folder + '\\config\\functional\\ShowRefillRequired.ini', 'r')
            self.ShowRefillRequired = self.file.readline()
            self.file.close()
            if (self.ShowRefillRequired == '0'):
                self.ActShowRefillRequired = False
            elif (self.ShowRefillRequired == '1'):
                self.ActShowRefillRequired = True
            else:
                self.ReadOk = False
                self.ReadResult = 'Error: Value in ShowRefillRequired.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read ShowRefillRequired.ini'

        try:
            self.file = open(ARIS_folder + '\\config\\design\\BorderRadius.ini', 'r')
            self.BorderRadius = self.file.readline()
            self.file.close()
            self.ActBorderRadius = int(self.BorderRadius)
            if ((self.ActBorderRadius < 0) or (self.ActBorderRadius > 20)):
                self.ActBorderRadius = 4
                self.ReadOk = False
                self.ReadResult = 'Error: Value in BorderRadius.ini is out of range'
        except:
            self.ReadOk = False
            self.ReadResult = 'Error: Could not read BorderRadius.ini'
        
        
        self.ActBgColor = {'Color':self.BgColor}
        self.ActSepColor = {'Color':self.SepColor}
        self.ActMainTextColor = {'Color':self.MainTextColor}
        self.ActTitleTextColor = {'Color':self.TitleTextColor}
        self.ActGearTextColor = {'Color':self.GearTextColor}
        self.ActTcColor = {'Color':self.TcColor}
        self.ActAbsColor = {'Color':self.AbsColor}
        self.ActPersonalBestColor = {'Color':self.PersonalBestColor}
        self.ActSessionBestColor = {'Color':self.SessionBestColor}

    def save(self):
        ##########################################################################################
        #                                                                                        #
        # Write configuration files                                                              #
        #                                                                                        #
        ##########################################################################################
        
        save = 0
        
        if ((int(self.RpmType) != 0) and (self.ActRpmType == 'angular elements')):
            file = open(ARIS_folder + '\\config\\design\\RPM_type.ini', 'w')
            file.write('0')
            file.close()
            self.RpmType = '0'
            save = 1
        elif ((int(self.RpmType) != 1) and (self.ActRpmType == 'round elements')):
            file = open(ARIS_folder + '\\config\\design\\RPM_type.ini', 'w')
            file.write('1')
            file.close()
            self.RpmType = '1'
            save = 1
        elif ((int(self.RpmType) != 2) and (self.ActRpmType == 'linear gauge')):
            file = open(ARIS_folder + '\\config\\design\\RPM_type.ini', 'w')
            file.write('2')
            file.close()
            self.RpmType = '2'
            save = 1
        
        if ((int(self.RpmDirection) != 0) and ((self.ActRpmDirection == 'outer to inner') or (self.ActRpmDirection == 'inner to outer'))):
            file = open(ARIS_folder + '\\config\\design\\RPM_direction.ini', 'w')
            file.write('0')
            file.close()
            self.RpmDirection = '0'
            save = 1
        elif ((int(self.RpmDirection) != 1) and (self.ActRpmDirection == 'left to right')):
            file = open(ARIS_folder + '\\config\\design\\RPM_direction.ini', 'w')
            file.write('1')
            file.close()
            self.RpmDirection = '1'
            save = 1
        
        if ((int(self.RedlineType) != 0) and (self.ActRedlineType == 'blue RPM graph')):
            file = open(ARIS_folder + '\\config\\design\\RedLineIndicatorType.ini', 'w')
            file.write('0')
            file.close()
            self.RedlineType = '0'
            save = 1
        elif ((int(self.RedlineType) != 1) and (self.ActRedlineType == 'blue RPM graph with background image')):
            file = open(ARIS_folder + '\\config\\design\\RedLineIndicatorType.ini', 'w')
            file.write('1')
            file.close()
            self.RedlineType = '1'
            save = 1
        elif ((int(self.RedlineType) != 2) and (self.ActRedlineType == 'background image')):
            file = open(ARIS_folder + '\\config\\design\\RedLineIndicatorType.ini', 'w')
            file.write('2')
            file.close()
            self.RedlineType = '2'
            save = 1
            
        if (self.BgColor.upper() != self.ActBgColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActBgColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\BackgroundColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.BgColor = self.ActBgColor['Color']
            save = 1
            
        if (self.SepColor.upper() != self.ActSepColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActSepColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\SeperatorColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.SepColor = self.ActSepColor['Color']
            save = 1
        
        if (float(self.WelcomeMsgDuration) != self.ActWelcomeMsgDuration):
            file = open(ARIS_folder + '\\config\\design\\WelcomeMessageDisplayTime.ini', 'w')
            file.write(str(self.ActWelcomeMsgDuration))
            file.close()
            self.WelcomeMsgDuration = str(self.ActWelcomeMsgDuration)
            save = 1
        
        if (float(self.BorderRadius) != self.ActBorderRadius):
            file = open(ARIS_folder + '\\config\\design\\BorderRadius.ini', 'w')
            file.write(str(int(self.ActBorderRadius)))
            file.close()
            self.BorderRadius = str(self.ActBorderRadius)
            save = 1
        
        if (float(self.LastLapTimeDisplayDuration) != self.ActLastLapTimeDisplayDuration):
            file = open(ARIS_folder + '\\config\\functional\\LastLapDisplayTime.ini', 'w')
            file.write(str(self.ActLastLapTimeDisplayDuration))
            file.close()
            self.LastLapTimeDisplayDuration = str(self.ActLastLapTimeDisplayDuration)
            save = 1
        
        if (self.ActShowFasterCarBehind):
            if (float(self.ShowFasterCarBehind) != 1.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowFasterCarBehind.ini', 'w')
                file.write('1')
                file.close()
                self.ShowFasterCarBehind = '1'
                save = 1
        else:
            if (float(self.ShowFasterCarBehind) != 0.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowFasterCarBehind.ini', 'w')
                file.write('0')
                file.close()
                self.ShowFasterCarBehind = '0'
                save = 1
        
        if (self.ActShowFasterCarBehind):
            if (float(self.FasterCarBehindThreshold) != self.ActFasterCarBehindThreshold):
                file = open(ARIS_folder + '\\config\\functional\\FasterCarBehind_ThresholdFactor.ini', 'w')
                file.write(str(self.ActFasterCarBehindThreshold))
                file.close()
                self.FasterCarBehindThreshold = str(self.ActFasterCarBehindThreshold)
                save = 1
        
        if (self.ActShowFlags):
            if (float(self.ShowFlags) != 1.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowFlags.ini', 'w')
                file.write('1')
                file.close()
                self.ShowFlags = '1'
                save = 1
        else:
            if (float(self.ShowFlags) != 0.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowFlags.ini', 'w')
                file.write('0')
                file.close()
                self.ShowFlags = '0'
                save = 1
    
        if (self.ActShowRpmLimit):
            if (float(self.ShowRpmLimit) != 1.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowRPMLimit.ini', 'w')
                file.write('1')
                file.close()
                self.ShowRpmLimit = '1'
                save = 1
        else:
            if (float(self.ShowRpmLimit) != 0.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowRPMLimit.ini', 'w')
                file.write('0')
                file.close()
                self.ShowRpmLimit = '0'
                save = 1
        
        if (self.ActShowDrs):
            if (float(self.ShowDrs) != 1.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowDRS.ini', 'w')
                file.write('1')
                file.close()
                self.ShowDrs = '1'
                save = 1
        else:
            if (float(self.ShowDrs) != 0.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowDRS.ini', 'w')
                file.write('0')
                file.close()
                self.ShowDrs = '0'
                save = 1
        
        if (self.MainTextColor.upper() != self.ActMainTextColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActMainTextColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\TextMainColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.MainTextColor = self.ActMainTextColor['Color']
            save = 1
    
        if (self.TitleTextColor.upper() != self.ActTitleTextColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActTitleTextColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\TextTitleColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.TitleTextColor = self.ActTitleTextColor['Color']
            save = 1
        
        if (self.GearTextColor.upper() != self.ActGearTextColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActGearTextColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\TextGearColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.GearTextColor = self.ActGearTextColor['Color']
            save = 1
    
        if (self.TcColor.upper() != self.ActTcColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActTcColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\TCColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.TcColor = self.ActTcColor['Color']
            save = 1
        
        if (self.AbsColor.upper() != self.ActAbsColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActAbsColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\ABSColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.AbsColor = self.ActAbsColor['Color']
            save = 1
        
        if (self.PersonalBestColor.upper() != self.ActPersonalBestColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActPersonalBestColor['Color'])
            print(Color)
            file = open(ARIS_folder + '\\config\\design\\PersonalBestColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.PersonalBestColor = self.ActPersonalBestColor['Color']
            save = 1
        
        if (self.SessionBestColor.upper() != self.ActSessionBestColor['Color'].upper()):
            # Change color from RGBA to ARGB as SimHub uses ARGB
            Color = Custom.Graphics.RgbaToAgb(self.ActSessionBestColor['Color'])
            file = open(ARIS_folder + '\\config\\design\\SessionBestColor.ini', 'w')
            file.write(Color.upper())
            file.close()
            self.SessionBestColor = self.ActSessionBestColor['Color']
            save = 1
    
        if (self.ActFlagsBlinking):
            if (float(self.FlagsBlinking) != 1.0):
                file = open(ARIS_folder + '\\config\\design\\FlagsBlinking.ini', 'w')
                file.write('1')
                file.close()
                self.FlagsBlinking = '1'
                save = 1
        else:
            if (float(self.FlagsBlinking) != 0.0):
                file = open(ARIS_folder + '\\config\\design\\FlagsBlinking.ini', 'w')
                file.write('0')
                file.close()
                self.FlagsBlinking = '0'
                save = 1
    
        if (self.ActBackgroundImageActive):
            if (float(self.BackgroundImageActive) != 1.0):
                file = open(ARIS_folder + '\\config\\design\\BackgroundImageActive.ini', 'w')
                file.write('1')
                file.close()
                self.BackgroundImageActive = '1'
                save = 1
        else:
            if (float(self.BackgroundImageActive) != 0.0):
                file = open(ARIS_folder + '\\config\\design\\BackgroundImageActive.ini', 'w')
                file.write('0')
                file.close()
                self.BackgroundImageActive = '0'
                save = 1
        
        if (self.ActShowRefillRequired):
            if (float(self.ShowRefillRequired) != 1.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowRefillRequired.ini', 'w')
                file.write('1')
                file.close()
                self.ShowRefillRequired = '1'
                save = 1
        else:
            if (float(self.ShowRefillRequired) != 0.0):
                file = open(ARIS_folder + '\\config\\functional\\ShowRefillRequired.ini', 'w')
                file.write('0')
                file.close()
                self.ShowRefillRequired = '0'
                save = 1
        
        if (save == 1):
            self.SaveResult = 'Configuration saved'
            Custom.DebugPrint(DebugMode, 'Configuration saved')
        elif (save == 0):
            self.SaveResult = 'Nothing to save'
            Custom.DebugPrint(DebugMode, 'Configuration not saved. There is nothing to save')
        else:
            self.SaveResult = 'Error while saving. Check the config and try again'
            Custom.DebugPrint(DebugMode, 'Error while saving. Check the config and try again')

###############################################################
#                                                             #
#                           M A I N                           #
#                                                             #
###############################################################

if __name__ == '__main__':
    ArisConfiguratorApp().run()
