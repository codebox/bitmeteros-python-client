#!/usr/bin/env python

"""
The Prefs class is used to contain the users preferences, such as colour selection, and the size
and position of the graph. Prefs 
"""

import wx

class Prefs():
    def __init__(self, db, defaults):
        self.db       = db
        self.defaults = defaults
        self.prefs    = None

    def Save(self):
      # Save the current set of prefs to the database
        self.db.SavePrefs(self.prefs)

    def Get(self, name):
        if self.prefs == None:
          # This is the first time we have accessed a value, so read from the database
            self.prefs = self.db.GetPrefs()
        
        val = self.prefs.get(name)
        if val == None:
            val = self.defaults.get(name)
            
        return val
        
    def GetNum(self, name):
      # Convert the named value into a number and return
        val = self.Get(name)
        if val != None:
            return int(val)
        else:
            return None
        
    def GetCol(self, name):
      # Convert the named value into a colour and return
        val = self.GetObj(name)
        if val != None:
            col = wx.Colour()
            col.Set(val[0],val[1],val[2])
            return col
        else:
            return None    
            
    def GetObj(self, name):
      # Eval the named value and return the result
        val = self.Get(name)
        if val != None:
            return eval(val)
        else:
            return None    
                
    def SetObj(self, name, value):
      # Store the name/value pair
        self.prefs[name] = str(value)