from Qt import QtCore, QtGui, QtWidgets
from maya import cmds
from VertexAnimationTexture import VertexAnimationCapture
from importlib import reload
reload(VertexAnimationCapture)
import json
import os
from subprocess import Popen

class BaseWindow(object):
    windowName = ("BaseWindow")

    def show(self):

        if cmds.window(self.windowName, query=True, exists=True): #if window by this name exists
            cmds.deleteUI(self.windowName) #delete window

        cmds.window(self.windowName) #create window with name

        self.buildUI() #class method to set window layout and settings

        cmds.showWindow() #show window

    def buildUI(self):
        pass

    def reset(self, *args):
        pass

    def close(self, *args):
        cmds.deleteUI(self.windowName)


class VATUI(BaseWindow, dict):
    windowName = "VAT_Window"
    vatfunc = VertexAnimationCapture.VertsToTexture()
    updated = False



    def buildUI(self):
        self["Warning"] = "MAKE SURE THAT SRGB IS SET TO OFF"

        column = cmds.columnLayout()
        cmds.rowLayout(numberOfColumns=2)
        cmds.text(label="VAT Texture Generator", font="boldLabelFont")
        cmds.text(label="- Charles von Kalm")

        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=4)
        cmds.text(label="Object:", font="boldLabelFont")
        self.ObjectNameText = cmds.text(label="")

        cmds.text(label="Vertices:", font="boldLabelFont")
        self.VerticesText = cmds.text(label="")

        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=2)
        cmds.text(label="Image Size:", font="boldLabelFont")
        self.ImageSizeText = cmds.text(label="")

        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=2)
        cmds.text(label="Time Range:", font="boldLabelFont")
        self.TimeRangeText = cmds.text(label="")


        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=4)
        cmds.text(label="Scale:", font="boldLabelFont")
        self.scalefield = cmds.intField(value=1, width=50)
        self["Scale"] = cmds.intField(self.scalefield, value=True, query=True)

        cmds.text(label="Steps:", font="boldLabelFont")
        self.stepfield = cmds.intField(value=1, width=50)
        self["Steps"] = cmds.intField(self.stepfield, value=True, query=True)

        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=3)
        cmds.text(label="Do Split?", font="boldLabelFont", ann="Not Recommend - Often leaves bad results in engine.")
        self.splitbox = cmds.checkBox(label='')
        cmds.button(label="Update Info", command=self.doUpdate)

        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=3)
        cmds.button(label="Directory", command=self.findDirectory)
        self.outputfield = cmds.textField(text='', editable=False, width=200)
        self["Output"] = cmds.textField(self.outputfield, text=True, query=True)

        cmds.setParent(column)
        cmds.rowLayout(numberOfColumns=3)
        cmds.button(label="Start", command=self.output)
        cmds.button(label="Open Folder", command=self.opendir)
        self.highbitbox = cmds.checkBox(label='Do 16bit Image')

    def opendir(self, *args):
        if not self["Output"] == "":
            Popen(['explorer', os.path.realpath(self["Output"])])

    def output(self, *args):
        if self.updated:
            cmds.confirmDialog(t="Warning", m="Hard Edges will not bake properly onto normal map. \nImages wider then 2048 run higher risks of breaking.\nMesh outputs from first frame ensure that it is your resting frame.\nJoint-based movement may need manual export of frame 0 mesh.\nLocal based vertex location, if the 'mesh' is moved via direct keying or parent constraint will not work.\nMesh channel box must remain 0,0,0 for all transforms.")
            self["Steps"] = cmds.intField(self.stepfield, value=True, query=True)
            self["Scale"] = cmds.intField(self.scalefield, value=True, query=True)
            self["16 Bit"] = cmds.checkBox(self.highbitbox, query=True, value=True)

            if self["Output"] == "":
                cmds.warning("No Output")
                return


            self.vatfunc.main(start=self.info[4], stop=self.info[5], scale=self["Scale"], step=self["Steps"], dirpath=self["Output"], selectedObj=self.info[0], split=self["Split"], bit=self["16 Bit"])

            infoFile = os.path.join(self["Output"], '%s._infoFile.json' % self.info[0])

            with open(infoFile, 'w') as f:
                json.dump(self, f, indent=4)

    def findDirectory(self, *args):
        try:
            path = cmds.fileDialog2(dialogStyle=2, fileMode=3, okCaption='Select')[0]
        except:
            path = ""
        self["Output"] = path
        cmds.textField(self.outputfield, edit=True, text=path)


    def doUpdate(self, *args):
        steps = cmds.intField(self.stepfield, value=True, query=True)
        split = cmds.checkBox(self.splitbox, query=True, value=True)

        self.info = self.vatfunc.getMeshInfo(step=steps, split=split)
        if not self.info:
            return

        cmds.text(self.ObjectNameText, edit=True, label=self.info[0])
        cmds.text(self.VerticesText, edit=True, label=self.info[1])
        cmds.text(self.ImageSizeText, edit=True, label=f"{self.info[3]}x{self.info[2]}")
        cmds.text(self.TimeRangeText, edit=True, label=f"{self.info[4]}-{self.info[5]}")

        self["ObjectName"] = self.info[0]
        self["Vertices"] = self.info[1]
        self["ImageSize"] = f"{self.info[3]}x{self.info[2]}"
        self["CaptureRange"] = f"{self.info[4]}-{self.info[5]}"
        self["Split"] = split

        self.updated = True


