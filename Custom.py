import zipfile
import win32gui
import re
import os
from datetime import datetime
from kivy.utils import get_hex_from_color, get_color_from_hex
from kivy.graphics import Color
from kivy.graphics import Rectangle, RoundedRectangle
from kivy.graphics import Line
from kivy.graphics import Ellipse
from kivy.uix.button import ButtonBehavior
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout


def DebugPrint(Active, TextToPrint):
    if Active:
        print('[DEBUG] ' + datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ': ' + TextToPrint)
    else:
        pass

class ColoredCanvas(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super(ColoredCanvas, self).__init__(**kwargs)
        # draw new canvas
        with self.canvas:
            Color(0,0,0,0)
            self.Rectangle = RoundedRectangle(  pos = self.pos,
                                                size = self.size,
                                                radius = [0])
            self.Ellipse = Ellipse( pos = self.pos,
                                    size = self.size)

        # listen / react to changes
        self.bind(pos=self.Update, size=self.Update)
        #self.bind(pos=lambda obj, pos: setattr(self.rect, "pos", pos))
        #self.bind(size=lambda obj, size: setattr(self.rect, "size", size))
    
    def DrawRectangle(self, **options):
        self.canvas.clear()
        with self.canvas:
            # set color
            if 'Color' in options:
                Rgba = options['Color']
                if (len(Rgba) == 4):
                    Color(Rgba[0], Rgba[1], Rgba[2], Rgba[3])
                elif (len(Rgba) == 3):
                    Color(Rgba[0], Rgba[1], Rgba[2])
                else:
                    Color(0,0,0,1)
            else:
                # take black if no color is given
                Color(0,0,0,1)
            if 'BorderWidth' in options:
                # if border is active draw the inner rectangle a little bit smaller (because of the round edges of the border)
                if 'Radius' in options:
                    self.Rectangle = RoundedRectangle(  pos = [self.pos[0] + options['BorderWidth'], self.pos[1] + options['BorderWidth']],
                                                    size = [self.size[0] - 2 * options['BorderWidth'], self.size[1] - 2 * options['BorderWidth']],
                                                    radius = [options['Radius']])
                else:
                    self.Rectangle = Rectangle( pos = [self.pos[0] + options['BorderWidth'], self.pos[1] + options['BorderWidth']],
                                                size = [self.size[0] - 2 * options['BorderWidth'], self.size[1] - 2 * options['BorderWidth']])
            else:
                if 'Radius' in options:
                    self.Rectangle = RoundedRectangle(  pos = self.pos,
                                                    size = self.size,
                                                    radius = [options['Radius']])
                else:
                    self.Rectangle = Rectangle( pos = self.pos,
                                                size = self.size)
            if 'BorderWidth' in options:
                # set color for border
                if 'BorderColor' in options:
                    Rgba = options['BorderColor']
                    if (len(Rgba) == 4):
                        Color(Rgba[0], Rgba[1], Rgba[2], Rgba[3])
                    elif (len(Rgba) == 3):
                        Color(Rgba[0], Rgba[1], Rgba[2])
                    else:
                        Color(0,0,0,1)
                else:
                    # take black if no color is given
                    Color(0,0,0,1)
                # draw the border (consider border width in border position and size)
                if 'Radius' in options:
                    self.Border = Line( rounded_rectangle = [self.x + options['BorderWidth'], self.y + options['BorderWidth'], self.width - 2 * options['BorderWidth'], self.height - 2 * options['BorderWidth'], (options['Radius'])],
                                        width = options['BorderWidth'])
                else:
                    self.Border = Line( rectangle = [self.x + options['BorderWidth'], self.y + options['BorderWidth'], self.width - 2 * options['BorderWidth'], self.height - 2 * options['BorderWidth']],
                                        width = options['BorderWidth'])
    
    def DrawCircle(self, **options):
        # clear old canvas
        self.canvas.clear()

        # draw new canvas
        with self.canvas:
            # set color
            if 'Color' in options:
                Rgba = options['Color']
                if (len(Rgba) == 4):
                    Color(Rgba[0], Rgba[1], Rgba[2], Rgba[3])
                elif (len(Rgba) == 3):
                    Color(Rgba[0], Rgba[1], Rgba[2])
                else:
                    Color(0,0,0,1)
            else:
                # take black if no color is given
                Color(0,0,0,1)
            # draw epllipse with given color
            self.Ellipse = Ellipse( pos = [options['CenterX'] - options['Radius'], options['CenterY'] - options['Radius']],
                                    size = [2 * options['Radius'], 2 * options['Radius']])

            if 'BorderWidth' in options:
                if (options['BorderWidth'] > 0):
                    # set color for border
                    if 'BorderColor' in options:
                        Rgba = options['BorderColor']
                        if (len(Rgba) == 4):
                            Color(Rgba[0], Rgba[1], Rgba[2], Rgba[3])
                        elif (len(Rgba) == 3):
                            Color(Rgba[0], Rgba[1], Rgba[2])
                        else:
                            Color(0,0,0,1)
                    else:
                        # take black if no color is given
                        Color(0,0,0,1)
                    # draw the border if needed
                    self.Border = Line( circle = [options['CenterX'], options['CenterY'], options['Radius']],
                                        width = options['BorderWidth'])

    def Update(self, *args):
        # set new position and size for rectangle
        self.Rectangle.pos = self.pos
        self.Rectangle.size = self.size

class LabelButton(ButtonBehavior, Label):
    pass

class Graphics():

    def ArgbToRgba(Argb):
        # convert ARGB color code to RGBA color code
        if (len(Argb) == 9):
            a = Argb[1:3]
            Rgba = '#' + Argb[3:9] + a
            return Rgba
        else:
            return Argb
    
    def RgbaToAgb(Rgba):
        # convert RGBA color code to ARGB color code
        if (len(Rgba) == 9):
            a = Rgba[7:9]
            Argb = '#' +  a + Rgba[1:7]
            return Argb
        else:
            return Rgba
    
    def CheckColorHexCode(Color):
        # check color that it is a valid color code as hex
        ColorOk = True
        if ((len(Color) == 7) or (len(Color) == 9)):
            if ((Color[0]) != '#'):
                ColorOk = False
            if ((((Color[1]) >= '0') and ((Color[1]) <= '9')) or
                (((Color[1]) >= 'A') and ((Color[1]) <= 'F')) or
                (((Color[1]) >= 'a') and ((Color[1]) <= 'f'))):
                pass
            else:
                ColorOk = False
            if ((((Color[2]) >= '0') and ((Color[2]) <= '9')) or
                (((Color[2]) >= 'A') and ((Color[2]) <= 'F')) or
                (((Color[2]) >= 'a') and ((Color[2]) <= 'f'))):
                pass
            else:
                ColorOk = False
            if ((((Color[3]) >= '0') and ((Color[3]) <= '9')) or
                (((Color[3]) >= 'A') and ((Color[3]) <= 'F')) or
                (((Color[3]) >= 'a') and ((Color[3]) <= 'f'))):
                pass
            else:
                ColorOk = False
            if ((((Color[4]) >= '0') and ((Color[4]) <= '9')) or
                (((Color[4]) >= 'A') and ((Color[4]) <= 'F')) or
                (((Color[4]) >= 'a') and ((Color[4]) <= 'f'))):
                pass
            else:
                ColorOk = False
            if ((((Color[5]) >= '0') and ((Color[5]) <= '9')) or
                (((Color[5]) >= 'A') and ((Color[5]) <= 'F')) or
                (((Color[5]) >= 'a') and ((Color[5]) <= 'f'))):
                pass
            else:
                ColorOk = False
            if ((((Color[6]) >= '0') and ((Color[6]) <= '9')) or
                (((Color[6]) >= 'A') and ((Color[6]) <= 'F')) or
                (((Color[6]) >= 'a') and ((Color[6]) <= 'f'))):
                pass
            else:
                ColorOk = False
            if (len(Color) == 9):
                if ((((Color[7]) >= '0') and ((Color[7]) <= '9')) or
                    (((Color[7]) >= 'A') and ((Color[7]) <= 'F')) or
                    (((Color[7]) >= 'a') and ((Color[7]) <= 'f'))):
                    pass
                else:
                    ColorOk = False
                if ((((Color[8]) >= '0') and ((Color[8]) <= '9')) or
                    (((Color[8]) >= 'A') and ((Color[8]) <= 'F')) or
                    (((Color[8]) >= 'a') and ((Color[8]) <= 'f'))):
                    pass
        else:
            ColorOk = False
        
        if ColorOk:
            return 0
        else:
            return 1

    def ColorChooser(layout, args, **options):
        def ApplyColorChooser(layout, args, options):
            Color = (get_hex_from_color(layout.Popup_ColorPicker.color))
            if (options['DisableAlpha']):
                if ((Color[7] != 'F') and (Color[7] != 'f')) or ((Color[8] != 'F') and (Color[8] != 'f')):
                    layout.Popup_ColorPicker.color[3] = 1 # remove transparency
                    layout.PopupStatus_Label.text = 'Alpha channel is not supported here!\nAlpha channel has been removed'
                else:
                    # if popup was quit with OK button set new color
                    layout.ColorPickPreview_ColoredCanvas.DrawRectangle(Color = get_color_from_hex(Color))
                    args['Color'] = Color
                    layout.Popup.dismiss()
            else:
                # if popup was quit with OK button set new color
                layout.ColorPickPreview_ColoredCanvas.DrawRectangle(Color = get_color_from_hex(Color))
                args['Color'] = Color
                layout.Popup.dismiss()
        
        def CancelColorChooser(layout, args):
            layout.Popup_ColorPicker.color = get_color_from_hex(args['Color'])
            layout.Popup.dismiss()

        ###

        # clear all widgets first
        layout.clear_widgets()

        ##########################################################################################
        #                                                                                        #
        # Color picker popup                                                                     #
        #                                                                                        #
        ##########################################################################################

        layout.Popup_Layout = GridLayout(   cols = 1,
                                            spacing = [10])
        layout.Popup_ColorPicker = ColorPicker( color = get_color_from_hex(args['Color']),
                                                height = 400,
                                                size_hint_y = None)
        layout.Popup_Layout.add_widget(layout.Popup_ColorPicker)

        try:
            if (options['DisableAlpha']):
                layout.Popup_ColorPicker.children[0].children[1].children[4].disabled = True
        except:
            pass

        layout.Popup_Button_Layout = GridLayout(    cols = 3,
                                                    spacing = [20])
        layout.Popup_OkButton = Button( text = 'OK')
        layout.Popup_CancelButton = Button( text = 'Cancel')
        layout.PopupStatus_Label = Label(   text = '',
                                            color = get_color_from_hex('#FFA000FF'),
                                            width = 210,
                                            size_hint_x = None)
        layout.Popup_Button_Layout.add_widget(layout.Popup_OkButton)
        layout.Popup_Button_Layout.add_widget(layout.PopupStatus_Label)
        layout.Popup_Button_Layout.add_widget(layout.Popup_CancelButton)
        layout.Popup_Layout.add_widget(layout.Popup_Button_Layout)

        layout.Popup = Popup(   title = options['PopupTitle'],
                                size_hint = [None, None],
                                size = [575, 525],
                                content = layout.Popup_Layout,
                                auto_dismiss = layout)

        layout.Popup_OkButton.bind(on_release = lambda x:ApplyColorChooser(layout, args, options))
        layout.Popup_CancelButton.bind(on_release = lambda x:CancelColorChooser(layout, args))

        ##########################################################################################
        #                                                                                        #
        # Color picker preview and optional button                                               #
        #                                                                                        #
        ##########################################################################################

        # place label
        layout.Label = Label(   text = options['LabelText'],
                                valign = 'bottom',
                                height = layout.height / 2,
                                size_hint_y = None)
        layout.Label.bind(size = layout.Label.setter('text_size'))
        layout.add_widget(layout.Label)

        ###

        try:
            if (options['WithButton']):
                # set 2 coloumns and leave a little space between preview the button
                layout.ColorPick_Layout = GridLayout(   cols = 2,
                                                        spacing = [10, 10])
            else:
                # no button -> only 1 coloumn needed
                layout.ColorPick_Layout = GridLayout(cols = 1)
        except:
            # no button -> only 1 coloumn needed
            layout.ColorPick_Layout = GridLayout(cols = 1)

        # define and place label as color preview
        layout.ColorPickPreview_ColoredCanvas = ColoredCanvas(  height = layout.height,
                                                                width = layout.width,
                                                                size_hint_y = None)
        layout.ColorPickPreview_ColoredCanvas.pos[0] = layout.pos[0]
        layout.ColorPickPreview_ColoredCanvas.pos[1] = layout.pos[1] - layout.Label.height
        layout.ColorPickPreview_ColoredCanvas.DrawRectangle(Color = get_color_from_hex(args['Color']))
        layout.ColorPick_Layout.add_widget(layout.ColorPickPreview_ColoredCanvas)

        try:
            if (options['WithButton']):
                # place button if WithButton option is active
                layout.ColorPick_Button = Button(text = 'Change')
                layout.ColorPick_Layout.add_widget(layout.ColorPick_Button)
                layout.ColorPick_Button.bind(on_release = layout.Popup.open)
            else:
                # make preview clickable if WithButton option is not active
                layout.ColorPickPreview_ColoredCanvas.bind(on_release = layout.Popup.open)
        except:
            # make preview clickable if WithButton option is not handed over
            layout.ColorPickPreview_ColoredCanvas.bind(on_release = layout.Popup.open)

        # place build layout on layout handed over
        layout.add_widget(layout.ColorPick_Layout)

class WindowManager:
    def __init__ (self):
        self.handle = None

    def find_window(self, class_name, window_name = None):
        # find a window by its class name
        self.handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        # check all opened windows
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self.handle = hwnd

    def find_window_wildcard(self, wildcard):
        # find a window whose title matches the wildcard
        self.handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        # put the window in the foreground
        win32gui.SetForegroundWindow(self.handle)

class Zip:
    def CreateZIP(folder, filename, compress = zipfile.ZIP_DEFLATED):
        filename_len = len(filename)
        
        # check length of file name
        if (filename_len > 4):
            file_ending_slice = slice(filename_len - 4, filename_len)
            file_ending = filename[file_ending_slice]
            if (file_ending.lower() != '.zip'):
                filename = filename + '.zip'
        else:
            filename = filename + '.zip'

        # create ZIP file
        with zipfile.ZipFile(filename, 'w', compress) as zip_target:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    add = os.path.join(root, file)
                    add = add.replace('\\', '\\')
                    zip_target.write(add, arcname = os.path.join(root.replace(folder, "config\\"), file))
        zip_target.close()

    def AddToZIP(folder, filename, compress = zipfile.ZIP_DEFLATED):
        filename_len = len(filename)

        # check length of file name
        if (filename_len > 4):
            file_ending_slice = slice(filename_len - 4, filename_len)
            file_ending = filename[file_ending_slice]
            if (file_ending.lower() != '.zip'):
                filename = filename + '.zip'
        else:
            filename = filename + '.zip'

        # add file/folder to ZIP file
        with zipfile.ZipFile(filename, 'a', compress) as zip_target:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    add = os.path.join(root, file)
                    add = add.replace('\\', '\\')
                    zip_target.write(add, arcname = os.path.join(root.replace(folder, "background\\"), file))
        zip_target.close()
