# -*- coding: utf-8 -*-
""" *==LICENSE==*

CyanWorlds.com Engine - MMOG client, server and tools
Copyright (C) 2011  Cyan Worlds, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Additional permissions under GNU GPL version 3 section 7

If you modify this Program, or any covered work, by linking or
combining it with any of RAD Game Tools Bink SDK, Autodesk 3ds Max SDK,
NVIDIA PhysX SDK, Microsoft DirectX SDK, OpenSSL library, Independent
JPEG Group JPEG library, Microsoft Windows Media SDK, or Apple QuickTime SDK
(or a modified version of those libraries),
containing parts covered by the terms of the Bink SDK EULA, 3ds Max EULA,
PhysX SDK EULA, DirectX SDK EULA, OpenSSL and SSLeay licenses, IJG
JPEG Library README, Windows Media SDK EULA, or QuickTime SDK EULA, the
licensors of this Program grant you additional
permission to convey the resulting work. Corresponding Source for a
non-source form of such a combination shall include the source code for
the parts of OpenSSL and IJG JPEG Library used as well as that of the covered
work.

You can contact Cyan Worlds, Inc. by email legal@cyan.com
 or by snail mail at:
      Cyan Worlds, Inc.
      14617 N Newport Hwy
      Mead, WA   99021

 *==LICENSE==* """
# Include Plasma code
from Plasma import *
from PlasmaTypes import *

# for save/load
import cPickle

## COMMENTED OUT by Jeff due to the re-write in the garrison wall

##############################################################
# define the attributes/parameters that we need from the 3dsMax scene
##############################################################
northWall = ptAttribSceneobjectList(1,"North Wall Decals",byObject=1)
southWall = ptAttribSceneobjectList(2,"South Wall Decals",byObject=1)
northBlocker = ptAttribSceneobjectList(3,"North Wall Blockers",byObject=1)
southBlocker = ptAttribSceneobjectList(4,"South Wall Blockers",byObject=1)
##############################################################
# grsnMainWallPython
##############################################################

## keep track of what to draw
NorthBlockers = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
SouthBlockers = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]

ReceiveInit = false

NorthState = 0
SouthState = 0


## for team light responders
kTeamLightsOn = 0
kTeamLightsOff = 1
kTeamLightsBlink = 2

## game states

kWaiting    = 0
kNorthSit   = 1
kSouthSit   = 2
kNorthSelect = 3
kSouthSelect = 4
kNorthReady = 5
kSouthReady = 6
kNorthPlayerEntry = 7
kSouthPlayerEntry = 8
kGameInProgress = 9
kNorthWin = 10
kSouthWin = 11
kSouthQuit = 12
kNorthQuit = 13


class grsnMainWallPython(ptResponder):
   
    # constants
    
    def __init__(self):
        "construction"
        PtDebugPrint("grsnMainWallPython::init begin")
        ptResponder.__init__(self)
        self.id = 52394
        self.version = 1
        PtDebugPrint("grsnMainWallPython::init end")        
    
    def OnServerInitComplete(self):
        global ReceiveInit
        
        ageSDL = PtGetAgeSDL()
        PtDebugPrint("grsnWallPython::OnServerInitComplete")        
        solo = true
        if len(PtGetPlayerList()):
            solo = false
            ReceiveInit = true
            return
        else:
            print"solo in climbing wall"
            
        #ageSDL.setFlags("nState",0,1)
        #ageSDL.setFlags("sState",0,1)
        #ageSDL.setFlags("NumBlockers",0,1)
        #ageSDL.setFlags("nBlockerChange",0,1)
        #ageSDL.setFlags("sBlockerChange",0,1)
        
        ageSDL.setNotify(self.key,"nState",0.0)
        ageSDL.setNotify(self.key,"sState",0.0)
        ageSDL.setNotify(self.key,"NumBlockers",0.0)
        ageSDL.setNotify(self.key,"nBlockerChange",0.0)
        ageSDL.setNotify(self.key,"sBlockerChange",0.0)
        
        #ageSDL.sendToClients("nState")
        #ageSDL.sendToClients("sState")
        #ageSDL.sendToClients("NumBlockers")
        #ageSDL.sendToClients("nBlockerChange")
        #ageSDL.sendToClients("sBlockerChange")
    
    def OnClimbingBlockerEvent(self,blocker):
        
        print"looking for blocker named ",blocker.getName()
        i = 0
        while i < 171:
            if (northBlocker.value[i] == blocker):
                northWall.value[i].runAttachedResponder(kTeamLightsBlink)
                print"found matching texture named ",northWall.value[i].getName()
                return
            elif (southBlocker.value[i] == blocker):
                southWall.value[i].runAttachedResponder(kTeamLightsBlink)
                print"found matching texture named ",southWall.value[i].getName()
                return
            i = i + 1
        
    def OnSDLNotify(self,VARname,SDLname,playerID,tag):
        global NorthState
        global SouthState
        
        ageSDL = PtGetAgeSDL()
        value = ageSDL[VARname][0]
        print "grsnMainWallPython.OnSDLNotify: VARname = ",VARname," SDLname = ",SDLname," playerID = ",playerID," value = ",value
        
        if (VARname == "nBlockerChange"):
            team = 1
            index = ageSDL[VARname][0]
            on = ageSDL[VARname][1]
            self.SetWallIndex(index,on,team)
            
        elif (VARname == "sBlockerChange"):
            team = 0
            index = ageSDL[VARname][0]
            on = ageSDL[VARname][1]
            self.SetWallIndex(index,on,team)
        
        elif ((VARname == "nState") or (VARname == "sState")):
            state = value
            if (VARname == "nState"):
                NorthState = state
            else:
                SouthState = state
            if ((state == kSouthWin) or (state == kNorthWin) or (state == kNorthQuit) or (state == kSouthQuit)):
                #display wall settings
                i = 0
                while (i < 20):
                    value = SouthBlockers[i] 
                    if (value > -1):
                        southWall.value[value].runAttachedResponder(kTeamLightsOn)
                        print"drawing s wall index",value
                    value = NorthBlockers[i] 
                    if (value >  -1):
                        northWall.value[value].runAttachedResponder(kTeamLightsOn)
                        print"drawing n wall index",value
                    i = i + 1
            elif (state == kSouthSelect):
                #clear wall settings
                i = 0
                while (i < 171):
                    southWall.value[i].runAttachedResponder(kTeamLightsOff)
                    if (i < 20):
                        SouthBlockers[i] = -1
                    i = i + 1
            elif (state == kNorthSelect):
                #clear wall settings
                i = 0
                while (i < 171):
                    if (i < 20):
                        NorthBlockers[i] = -1
                    northWall.value[i].runAttachedResponder(kTeamLightsOff)
                    i = i + 1
    
    def SetWallIndex(self,index,value,north):
        global SouthBlockers
        global NorthBlockers
        
        i = 0
        if (value):
            if (north):
                while (NorthBlockers[i] >= 0):
                    i = i + 1
                    if (i == 20):
                        print"yikes - somehow overran the array!"
                        return
                NorthBlockers[i] = index
                print"set north wall index ",index," in slot ",i," to true"
            else:
                while (SouthBlockers[i] >= 0):
                    i = i + 1
                    if (i == 20):
                        print"yikes - somehow overran the array!"
                        return
                SouthBlockers[i] = index
                print"set south wall index ",index," in slot ",i," to true"
        else:
            if (north):
                while (NorthBlockers[i] != index):
                    i = i + 1
                    if (i == 20):
                        print"this should not get hit - looked for non-existent NorthWall entry!"
                        return
                NorthBlockers[i] = -1
                print"removed index ",index," from list slot ",i
            else:
                while (SouthBlockers[i] != index):
                    i = i + 1
                    if (i == 20):
                        print"this should not get hit - looked for non-existent SouthWall entry!"
                        return
                SouthBlockers[i] = -1
                print"removed index ",index," from list slot ",i