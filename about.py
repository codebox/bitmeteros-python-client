#!/usr/bin/env python

"""
This module manages the About dialog window of the BitMeter OS desktop client
"""

import wx
import platform
import gettext

DONATE_URL  = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=9675111"
CODEBOX_URL = "http://codebox.org.uk/bitmeteros"
_=gettext.gettext

class AboutDialog(wx.Dialog):
    def __init__(self, version):
        wx.Dialog.__init__(self, None, -1, _('About'), size=(200, 150))
        
        titleLabel = wx.StaticText(self, -1, "BitMeter OS")
        titleLabel.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL))
        
        self.gridSizer = wx.FlexGridSizer(cols=5, hgap=6, vgap=6)
        self.AddVersion(_("BitMeter Version"), version)
        self.AddVersion(_("Python Version"), platform.python_version())
        self.AddVersion(_("wx Version"), wx.version())
        
        linkLabel = wx.StaticText(self, -1, CODEBOX_URL)
        linkFont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        linkFont.SetUnderlined(True)
        linkLabel.SetForegroundColour('blue')
        linkLabel.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        linkLabel.SetFont(linkFont)
        linkLabel.Bind(wx.EVT_LEFT_UP, self.OnCodeboxLinkClick)

        licenceText = wx.TextCtrl(self, -1,
                    _("BitMeterOS is free software: you can redistribute it and/or modify "
				    "it under the terms of the GNU General Public License as published by "
					"the Free Software Foundation, either version 3 of the License, or "
					"(at your option) any later version.\n\n"
					"BitMeterOS is distributed in the hope that it will be useful, "
					"but WITHOUT ANY WARRANTY; without even the implied warranty of "
					"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
					"GNU General Public License for more details."), size=(-1, 75), style=wx.TE_MULTILINE|wx.TE_READONLY)

        licenceBox = wx.BoxSizer(wx.HORIZONTAL)
        licenceBox.Add((10,0), 0)
        licenceBox.Add(licenceText, 1)
        licenceBox.Add((10,0), 0)

        donateLabel = wx.StaticText(self, -1, _("Donate"))
        donateLabel.SetForegroundColour('blue')
        donateLabel.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        donateLabel.SetFont(linkFont)
        donateLabel.Bind(wx.EVT_LEFT_UP, self.OnDonateLinkClick)
        
        okBtn = wx.Button(self, -1, _("OK"), size=(50,25))
        okBtn.Bind(wx.EVT_BUTTON, self.OnOkClick)
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add((0,10), 0)
        box.Add(titleLabel, 0, flag=wx.ALIGN_CENTER)
        box.Add((0,10), 0)
        box.Add(linkLabel, 0, flag=wx.ALIGN_CENTER)
        box.Add((0,10), 0)
        box.Add(self.gridSizer, 0, flag=wx.ALIGN_CENTER)
        box.Add((0,10), 0)
        box.Add(licenceBox, 1, flag=wx.ALIGN_CENTER|wx.EXPAND)
        box.Add((0,5), 0)
        box.Add(donateLabel, 0, flag=wx.ALIGN_CENTER)
        box.Add((0,10), 0)
        box.Add(okBtn, 0, flag=wx.ALIGN_CENTER)
        box.Add((0,5), 0)
        
        self.SetSizer(box)
        self.Fit()
    
    def AddVersion(self,name,value):
        nameLabel  = wx.StaticText(self, -1, name + ":")
        valueLabel = wx.StaticText(self, -1, value)
        self.gridSizer.Add((10, 0), 1, wx.EXPAND)
        self.gridSizer.Add(nameLabel, 1, wx.ALIGN_RIGHT)
        self.gridSizer.Add((10, 0), 0)
        self.gridSizer.Add(valueLabel, 1, wx.ALIGN_LEFT)
        self.gridSizer.Add((10, 0), 1, wx.EXPAND)
        
    def OnCodeboxLinkClick(self,event):
        webbrowser.open(CODEBOX_URL)
    
    def OnDonateLinkClick(self,event):
        webbrowser.open(DONATE_URL)
        
    def OnOkClick(self, event):
        self.Close()
