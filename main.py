#!/usr/bin/env python

"""
This is the main module of the BitMeter OS desktop client
"""

import time
import wx
import sys
import os
import os.path
import gettext
import string
import webbrowser
from prefs import Prefs
from about import AboutDialog
from db import Db
from options import OptionsDialog

VERSION = "0.1.0"
BYTES_PER_K=1024
_=gettext.gettext

class MyFrame(wx.Frame):
    def __init__(self, parent, title, db, defaultPrefs, capabilities):
        wx.Frame.__init__(self, parent, -1, title, style= wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.CLIP_CHILDREN )
        
        self.db=db
        self.capabilities = capabilities
        self.data = []
        
        self.options = None
        self.about = None
        
        self.prefs = Prefs(self.db, defaultPrefs)
        
      # Don't allow the user to shrink the window below these dimensions
        self.minYSize = 30
        self.minXSize = 50
        
      # This is the main graph
        self.panel = wx.Panel(self, style=wx.BORDER_SIMPLE)
        self.panel.Bind(wx.EVT_MOTION,    self.OnPanelMove)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnPanelDown)
        self.panel.Bind(wx.EVT_LEFT_UP,   self.OnPanelUp)
        self.panel.Bind(wx.EVT_PAINT,     self.OnPanelPaint)
        
      # This is the label below the graph showing numeric values
        self.label = wx.StaticText(self, -1, "-", style = wx.ST_NO_AUTORESIZE | wx.BORDER_SIMPLE | wx.ALIGN_CENTER)
        self.label.Bind(wx.EVT_LEFT_DOWN, self.OnLabelDown)
        self.Bind(wx.EVT_MOTION,    self.OnLabelMove)
        self.Bind(wx.EVT_LEFT_UP,   self.OnLabelUp)
        self.label.SetCursor(wx.StockCursor(wx.CURSOR_SIZENWSE))
        self.label.SetFont(wx.Font(8, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.panel, 1, flag = wx.EXPAND)
        box.Add((10,1), 0)
        box.Add(self.label, 0, flag = wx.EXPAND)
        
      # Restore the position of the graph from last time
        self.SetPosition(self.prefs.GetObj('position'))
        self.OnPrefsUpdated()
       
        self.SetSizer(box)
        self.Fit()
        self.SetSize(self.prefs.GetObj('size'))
        
      # We update the graph each second with new data
        self.timer = wx.Timer(self)
        self.timer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        
        self.InitBuffer()
        self.Bind(wx.EVT_IDLE, self.OnIdle)

      # Find the file-system location where we are running from
        encoding = sys.getfilesystemencoding()
        if hasattr(sys, "frozen"):
            self.modulePath = os.path.dirname(unicode(sys.executable, encoding))    
        else:
            self.modulePath = os.path.dirname(unicode(__file__, encoding))

        iconPath = os.path.join(self.modulePath, "resources", "bitmeter.ico")
        icon = wx.Icon(iconPath, wx.BITMAP_TYPE_ICO)  

      # The menu can be accessed from the main graph, and from the tray icon
        self.popupmenu = wx.Menu()
        self.trayIcon = TrayIcon(self, self.popupmenu, icon);
        self.showHideMain = self.popupmenu.Append(-1, _("Hide Graph"))
        self.Bind(wx.EVT_MENU, self.ToggleGraph)
        self.trayIcon.Bind(wx.EVT_MENU, self.ToggleGraph)
        
      # Menu item to open the Options dialog
        options = self.popupmenu.Append(-1, _("Options"))
        self.Bind(wx.EVT_MENU, self.OnMenuOptions, options)
        self.trayIcon.Bind(wx.EVT_MENU, self.OnMenuOptions, options)
      
      # Menu item to open the Web Interface
        webInterface = self.popupmenu.Append(-1, _("Web Interface"))
        self.Bind(wx.EVT_MENU, self.OnMenuWebInterface, webInterface)
        self.trayIcon.Bind(wx.EVT_MENU, self.OnMenuWebInterface, webInterface)
        
      # Need this to build the web interface url
        self.webPort = self.db.GetConfigValue('web.port', 2605)

      # Menu item to open the About dialog
        about = self.popupmenu.Append(-1, _("About"))
        self.Bind(wx.EVT_MENU, self.OnMenuAbout, about)
        self.trayIcon.Bind(wx.EVT_MENU, self.OnMenuAbout, about)
        
        self.popupmenu.AppendSeparator()
        
      # Menu item to quit he application
        exit = self.popupmenu.Append(-1, _("Exit"))
        self.Bind(wx.EVT_MENU, self.OnMenuExit, exit)
        self.trayIcon.Bind(wx.EVT_MENU, self.OnMenuExit, exit)
        
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def ToggleGraph(self, event):
      # Show/Hide the graph
        self.Show(not self.IsShown())
        if self.IsShown():
            self.showHideMain.SetText( _('Hide Graph'))
        else:
            self.showHideMain.SetText( _('Show Graph'))
       
    def FormatAmounts(self, dl, ul):
      # This value gets displayed below the main graph
        return "DL: %.2f UL: %.2f" % (float(dl)/1000, float(ul)/1000)
        
    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.panel.ScreenToClient(pos)
        self.panel.PopupMenu(self.popupmenu, pos)
    
    def OnMenuWebInterface(self, event):
      # Open the web interface in the default browser
        webbrowser.open("http://localhost:" + str(self.webPort))
    
    def OnMenuAbout(self, event):
      # Open the About dialog
        self.about = AboutDialog(VERSION)
        self.about.ShowModal()
        self.about.Destroy()
        self.about = None

    def OnMenuExit(self,event):
      # Close all open windows
        if self.options:
            self.options.Close()
        if self.about:
            self.about.Close()
        self.Close()
    
    def OnClose(self, event):
      # Store the current size/position of the graph before exiting
        self.prefs.SetObj('size', self.GetSize())
        self.prefs.SetObj('position', self.GetPosition())
        self.prefs.Save()
        
        self.trayIcon.RemoveIcon()  
        self.trayIcon.Destroy()  
        self.Destroy()

    def OnPrefsUpdated(self):
      # Callback invoked from the Options dialog when the user clicks 'OK'
        if self.capabilities['opacity']:
            self.SetTransparent(self.prefs.GetNum('opacity') * 2.55)
            
        self.SetBackgroundColour(self.prefs.GetCol('bgcolour')) 
        
        self.dlPen = wx.Pen(self.prefs.GetCol('dlcolour'), 1)
        self.ulPen = wx.Pen(self.prefs.GetCol('ulcolour'), 1)
        self.olPen = wx.Pen(self.prefs.GetCol('olcolour'), 1)
        self.scale = self.prefs.GetNum('scale')
        
        if not (self.prefs.GetObj('float') ^ (not self.HasFlag(wx.STAY_ON_TOP))):
          # Set the 'Stay On Top' flag to the appropriate value
            self.ToggleWindowStyle(wx.STAY_ON_TOP)
        
        if self.capabilities['clickthru']:
          # Windows only, window passes all mouse clicks to whatever is underneath
            if not (self.prefs.GetObj('clickthru') ^ (not self.HasFlag(wx.TRANSPARENT_WINDOW))):
                self.ToggleWindowStyle(wx.TRANSPARENT_WINDOW)
        
    def OnMenuOptions(self,event):
      # Open the Options dialog
        self.options = OptionsDialog(self, self.prefs, self.capabilities, self.OnPrefsUpdated)
        self.options.ShowModal()
        self.options.Destroy()
        self.options = None

    def OnPanelDown(self, event):
      # Mouse down over the graph means we want to drag the window
        self._panelDownPos = event.GetPosition()
        if not self.panel.HasCapture():
            self.panel.CaptureMouse()

    def OnPanelMove(self, event):
        if event.Dragging() and event.LeftIsDown():
          # The window is being dragged            
            pos = event.GetPosition()
            displacement = self._panelDownPos - pos
            self.SetPosition( self.GetPosition() - displacement )
               
    def OnPanelUp(self, event):
      # Stop dragging the window
        if self.panel.HasCapture():
            self.panel.ReleaseMouse()

    def GetEventYInWindow(self, event):
      # Calculate the y-coordinate of a mouse click within the label, relative to the whole window
        return self.GetSize().height - self.label.GetSize().height + event.GetPosition().y
        
    def OnLabelDown(self,event):
      # Mouse down in the label means we want to resize the window
        self._prevXInWindow = event.GetPosition().x
        self._prevYInWindow = self.GetEventYInWindow(event)
        self._origWidth     = self.GetSize().width
        self._origHeight    = self.GetSize().height
        
        if not self.HasCapture():
            self.CaptureMouse()
                
    def OnLabelMove(self,event):
      # Mouse move in the label means we should resize the window
        if event.Dragging():
            pos = event.GetPosition()
            displacementX = self._prevXInWindow - pos.x
            displacementY = self._prevYInWindow - pos.y
            newXSize = self._origWidth - displacementX
            newYSize = self._origHeight - displacementY
            if newYSize < self.minYSize:
                newYSize = self.minYSize
            if newXSize < self.minXSize:
                newXSize = self.minXSize
            self.SetSize(wx.Size(newXSize, newYSize))
            self.reInitBuffer = True

    def OnLabelUp(self,event):
      # Mouse up in the label means we want to stop resizing
        if self.HasCapture():
            self.ReleaseMouse()
    
    def OnPanelPaint(self, event):
      # Paint the graph with whatever is in our in-memory buffer
        dc = wx.BufferedPaintDC(self.panel, self.buffer)

    def OnIdle(self, event):
        if self.reInitBuffer:
          # We have new data to be displayed
            self.InitBuffer()
            self.Refresh(False)

    def InitBuffer(self):
      # Draw the next graph to be displayed onto the in-memory buffer
        size = self.panel.GetSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawLines(dc)
        self.reInitBuffer = False    
        
    def DrawLines(self, dc):
      # Draw the graph using the current upload/download values
        h = self.panel.GetSize().height
        now = time.time()
        ts = 0

        for d in self.data:
            ts = d[0]
            dl = d[1]
            ul = d[2]
            
            x = now - ts - 1
            y0  = h
            yDl = y0 - dl * h / (self.scale * BYTES_PER_K)
            yUl = y0 - ul * h / (self.scale * BYTES_PER_K)
            
            if dl < ul:
                dc.SetPen(self.olPen)
                dc.DrawLine(x, y0, x, yDl)
                dc.SetPen(self.ulPen)
                dc.DrawLine(x, yDl, x, yUl)
            else:
                dc.SetPen(self.olPen)
                dc.DrawLine(x, y0, x, yUl)
                dc.SetPen(self.dlPen)
                dc.DrawLine(x, yUl, x, yDl)
            
    def OnTimer(self, event):
      # Query the database to get the latest values
        now = int(time.time())
        results = self.db.GetData(now - self.GetSize().width, now)

      # Store the results and set the flag indicating that the graph should be re-drawn
        self.data = results[1]
        self.reInitBuffer = True
        self.panel.Refresh()
        self.label.SetLabel(self.FormatAmounts(results[0][0], results[0][1]))

class TrayIcon(wx.TaskBarIcon):  
    def __init__(self, parent, menu, icon):  
        wx.TaskBarIcon.__init__(self)  
        self.parentApp = parent  
        self.menu = menu
        self.CreateMenu()
        self.SetIcon(icon, "BitMeter OS")  
        self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.ShowHideGraph)  

    def ShowHideGraph(self, event):
        self.parentApp.Show(True)
        self.parentApp.Raise()
        self.parentApp.showHideMain.SetText(_('Hide Graph'))
        
    def CreateMenu(self):  
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.ShowMenu)  

    def ShowMenu(self,event):  
        self.PopupMenu(self.menu)  

            
class BitMeterApp(wx.App):
    def OnInit(self):
        dbPath = os.getenv('BITMETER_DB')
        
      # This holds flags indicating which display features are available on the current platform
        capabilities = {}
        
        if sys.platform == 'win32':
          # Windows
            dbPath = dbPath or "/Documents and Settings/All Users/Application Data/BitMeterOS/bitmeter.db"
            capabilities['clickthru'] = True
            capabilities['opacity']   = True
            
        elif sys.platform == 'darwin':
          # Mac OSX
            dbPath = dbPath or "/Library/Application Support/BitMeter/bitmeter.db"
            capabilities['clickthru'] = False
            capabilities['opacity']   = True
            
        elif sys.platform.startswith('linux'):
          # Linux
            dbPath = dbPath or "/var/lib/bitmeter/bitmeter.db"
            capabilities['clickthru'] = False
            capabilities['opacity']   = False
        
        if not os.path.exists(dbPath):
            print (_('Database file not found') + ': ' + dbPath)
            sys.exit(1)
        
      # Initial values for the user preferences
        defaultPrefs = {}
        defaultPrefs['dlcolour']  = '(255,0,0)'
        defaultPrefs['ulcolour']  = '(0,255,0)'
        defaultPrefs['olcolour']  = '(255,255,0)'
        defaultPrefs['bgcolour']  = '(255,255,255)'
        defaultPrefs['size']      = '(150,85)'
        defaultPrefs['position']  = '(100,100)'
        defaultPrefs['scale']     = '1000'
        defaultPrefs['opacity']   = '70'
        defaultPrefs['float']     = 'True'
        defaultPrefs['clickthru'] = 'False'
        
        frame = MyFrame(None, "", Db(dbPath, 'client.py.'), defaultPrefs, capabilities)
        self.SetTopWindow(frame)
        frame.Show(True)
        
        return True

if __name__ == '__main__':
    app = BitMeterApp(redirect=False)
    app.MainLoop()
