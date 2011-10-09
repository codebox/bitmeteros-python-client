#!/usr/bin/env python

"""
This module manages the Options dialog window of the BitMeter OS desktop client
"""

import wx
import gettext

_=gettext.gettext

class OptionsDialog(wx.Dialog):
    def __init__(self, parent, prefs, capabilities, PrefsUpdated):
        wx.Dialog.__init__(self, None, -1, _("Options"))
        self.prefs = prefs
        self.capabilities = capabilities
        self.PrefsUpdated = PrefsUpdated
        
      # The 'Scale' value fields
        scaleLabel = wx.StaticText(self, -1, _("Scale:"))
        self.scaleTxt = wx.TextCtrl(self, -1, str(prefs.Get('scale')), size=(100, -1))
        self.scaleTxt.Bind(wx.EVT_CHAR, self.onScaleChar) 
        
        kbpsLabel = wx.StaticText(self, -1, _("kB/sec"))
        
        scaleBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        scaleBoxSizer.Add(self.scaleTxt, 0)
        scaleBoxSizer.Add((10,0),0)
        scaleBoxSizer.Add(kbpsLabel, 0, wx.ALIGN_CENTER_VERTICAL)

      # The Opacity slider
        if self.capabilities['opacity']:
            opacityLabel = wx.StaticText(self, -1, _("Opacity %:"))
            self.opacitySlider = wx.Slider(self, size=(150,-1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
            self.opacitySlider.SetMin(10)
            self.opacitySlider.SetMax(100)
            self.opacitySlider.SetValue(self.prefs.GetNum('opacity'))
            self.opacitySlider.SetTickFreq(5,1)
        
      # Float checkbox
        floatLabel = wx.StaticText(self, -1, _("Float:"))
        self.floatChk = wx.CheckBox(self, -1, "")
        self.floatChk.SetValue(prefs.GetObj('float'))

      # Click-Through checkbox
        if self.capabilities['clickthru']:
            clickThruLabel = wx.StaticText(self, -1, _("Click Through:"))
            self.clickThruChk = wx.CheckBox(self, -1, "")
            self.clickThruChk.SetValue(prefs.GetObj('clickthru'))

      # Colour picker buttons
        dlColLabel = wx.StaticText(self, -1, _("Download Colour:"))
        self.dlColBtn = wx.Button(self, -1, "...", size=(30,20))
        self.dlColBtn.Bind(wx.EVT_BUTTON, self.PromptForDlColour)

        ulColLabel = wx.StaticText(self, -1, _("Upload Colour:"))
        self.ulColBtn = wx.Button(self, -1, "...", size=(30,20))
        self.ulColBtn.Bind(wx.EVT_BUTTON, self.PromptForUlColour)

        olColLabel = wx.StaticText(self, -1, _("Overlap Colour:"))
        self.olColBtn = wx.Button(self, -1, "...", size=(30,20))
        self.olColBtn.Bind(wx.EVT_BUTTON, self.PromptForOlColour)

        bgColLabel = wx.StaticText(self, -1, _("Background Colour:"))
        self.bgColBtn = wx.Button(self, -1, "...", size=(30,20))
        self.bgColBtn.Bind(wx.EVT_BUTTON, self.PromptForBgColour)

        okBtn = wx.Button(self, -1, _("OK"))
        okBtn.Bind(wx.EVT_BUTTON, self.OnOkClick)
        cnBtn = wx.Button(self, -1, _("Cancel"))
        cnBtn.Bind(wx.EVT_BUTTON, self.OnCnClick)
        
        boxMain = wx.BoxSizer(wx.VERTICAL)
        
      # Do all the layout...
        gridSizer = wx.FlexGridSizer(cols=4, hgap=6, vgap=6)
        lPad = 10
        rPad = 10
        vPad = 5
        
        vPadRow = [(0, vPad), (0, vPad), (0, vPad), (0, vPad)]
        
        gridSizer.AddMany(vPadRow)
        gridSizer.AddMany([(lPad, 0), scaleLabel, scaleBoxSizer, (rPad,0)])
        if self.capabilities['opacity']:
            gridSizer.AddMany([(lPad,0), opacityLabel, self.opacitySlider, (rPad,0)])
        gridSizer.AddMany([(lPad,0), floatLabel, self.floatChk, (rPad,0)])
        if self.capabilities['clickthru']:
            gridSizer.AddMany([(lPad,0), clickThruLabel, self.clickThruChk, (rPad, 0)])
        
        gridSizer.AddMany(vPadRow)    
        gridSizer.AddMany([(lPad,0), dlColLabel, self.dlColBtn, (rPad,0)])
        gridSizer.AddMany([(lPad,0), ulColLabel, self.ulColBtn, (rPad,0)])
        gridSizer.AddMany([(lPad,0), olColLabel, self.olColBtn, (rPad,0)])
        gridSizer.AddMany([(lPad,0), bgColLabel, self.bgColBtn, (rPad,0)])
        gridSizer.AddMany(vPadRow)
        
        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxSizer.Add((60,0),1,wx.EXPAND)
        boxSizer.Add(okBtn,0)
        boxSizer.Add((20, 0),0)
        boxSizer.Add(cnBtn,0)
        boxSizer.Add((60,0),1,wx.EXPAND)
        boxSizer.Fit(self)
        
      # A nice frame to enclose the controls
        controlBox = wx.StaticBox(self, -1, _("BitMeter OS Options"))
        controlBoxSizer = wx.StaticBoxSizer(controlBox, wx.VERTICAL)
        controlBoxSizer.Add(gridSizer)
        
        boxMain.Add(controlBoxSizer)
        boxMain.Add((0, vPad * 2))
        boxMain.Add(boxSizer)
        boxMain.Add((0, vPad * 2))
        
        self.SetSizer(boxMain)
        self.Fit()
        
    def onScaleChar(self, event): 
      # Filter the characters that can be typed into the Scale box
        key = event.GetKeyCode() 

      # Numbers, left/right arrows, backspace, and delete are all allowed
        if (key >= 48 and key <=57) or (key == 314) or (key == 316) or (key == 8) or (key == 127): 
            event.Skip() 
            return 
        else: 
            return False 
    
    def PromptForDlColour(self, event):
        self.PromptForColour('dlcolour')

    def PromptForUlColour(self, event):
        self.PromptForColour('ulcolour')

    def PromptForOlColour(self, event):
        self.PromptForColour('olcolour')

    def PromptForBgColour(self, event):
        self.PromptForColour('bgcolour')
        
    def PromptForColour(self, name):
      # Display the colour picker dialog
        colData = wx.ColourData()
        colData.SetColour(self.prefs.GetCol(name))
        colData.SetChooseFull(False)
        dlg = wx.ColourDialog(self, colData)
        if dlg.ShowModal() == wx.ID_OK:
          # User picked a colur and clicked 'OK' so add the new colour to the prefs dictionary
            self.prefs.SetObj(name, dlg.GetColourData().GetColour())
        dlg.Destroy()

    def OnOkClick(self,event):
      # Update the prefs object with the values selected on the screen
        if (self.scaleTxt.GetValue() == '') or (int(self.scaleTxt.GetValue()) == 0):
             self.scaleTxt.SetValue(str(self.prefs.GetNum('scale')))
             
        self.prefs.SetObj('scale', self.scaleTxt.GetValue())
        if self.capabilities['opacity']:
            self.prefs.SetObj('opacity', self.opacitySlider.GetValue())
            
        self.prefs.SetObj('float', self.floatChk.GetValue())
        if self.capabilities['clickthru']:
            self.prefs.SetObj('clickthru', self.clickThruChk.GetValue())
            
        self.prefs.Save()
      # Notify the main window of the new prefs
        self.PrefsUpdated()
        self.Close()
        
    def OnCnClick(self,event):
        self.Close()
        
