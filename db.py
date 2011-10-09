#!/usr/bin/env python

"""
The Db class manages access to the local BitMeter OS database, and provides
convenience methods for retrieving bandwidth data and reading/writing user
preference values. User preferences are stored in the 'config' table, names
are prefixed to distinguish them from configuration values used by other clients. 
"""

import sqlite3

class Db:
    def __init__(self, dbPath, prefsPrefix):
        self.cn             = sqlite3.connect(dbPath)
        self.prefsPrefix    = prefsPrefix
        self.prefsPrefixLen = len(self.prefsPrefix)
        
    def GetConfigValue(self, name, default=None):
      # Return a global (ie not specific to this client) config value
        result = self.cn.cursor().execute("select value from config where key=?", (name,)).fetchone()
        if result == None:
            return default
        else:
            return result[0]

    def GetPrefs(self):
      # Return a dictionary containing all the user preference values stored for this application
        c = self.cn.cursor()
        c.execute("select key,value from config where key like '" + self.prefsPrefix + "%'")
        
        prefs={}
        for row in c:
            prefs[row[0][self.prefsPrefixLen:]] = row[1]
            
        c.close()
        
        return prefs

    def SavePrefs(self, vals):
      # Store the user preference values contained in the vals dictionary in the database
        preModPrefs = self.GetPrefs()
        
        c = self.cn.cursor()
        for k,v in vals.iteritems():
            keyWithPrefix = self.prefsPrefix + k
            originalValue = preModPrefs.get(k)
            if originalValue == None:
              # This is a new value, so insert a new row
                t = (keyWithPrefix,v,)
                c.execute("insert into config (key,value) values (?,?)", t)
            elif originalValue != v:
              # This is an existing value that has been changed, update the appropriate row
                t = (v,keyWithPrefix,)
                c.execute("update config set value=? where key=?", t)
                
        self.cn.commit()        
        c.close()
                    
    def GetData(self, t, now):
      # Return a list of lists, representing recent bandwidth data.
      # All data appearing on or after time 't' will be returned
        c = self.cn.cursor()
        c.execute('select ts,dl,ul from data where ts >=' + str(t) + ' order by ts')
        
        data=[]
        nowData = [0,0]
        
        for row in c:
            data.append(row)
            if (row[0] == now-1):
              # We will display this ul/dl pair in the caption below the graph
                nowData = [row[1], row[2]]
            
        c.close()
        
        return [nowData, data]

