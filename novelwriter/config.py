"""
novelWriter – Config Class
==========================
Class holding the user preferences and handling the config file

File History:
Created: 2018-09-22 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import json
import logging

from time import time
from pathlib import Path

from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import (
    QT_VERSION_STR, QStandardPaths, QSysInfo, QLocale, QLibraryInfo,
    QTranslator
)

from novelwriter.error import logException, formatException
from novelwriter.common import splitVersionNumber, formatTimeStamp, NWConfigParser
from novelwriter.constants import nwFiles, nwUnicode

logger = logging.getLogger(__name__)


class Config:

    LANG_NW   = 1
    LANG_PROJ = 2

    def __init__(self):

        # Initialisation
        # ==============

        # Set Application Variables
        self.appName   = "novelWriter"
        self.appHandle = "novelwriter"

        # Set Paths
        confRoot = Path(QStandardPaths.writableLocation(QStandardPaths.ConfigLocation))
        dataRoot = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))

        self._confPath = confRoot.absolute() / self.appHandle  # The user config location
        self._dataPath = dataRoot.absolute() / self.appHandle  # The user data location
        self._lastPath = Path.home().absolute()  # The user's last used path

        self._appPath = Path(__file__).parent.absolute()
        self._appRoot = self._appPath.parent
        if self._appRoot.is_file():
            # novelWriter is packaged as a single file
            self._appRoot = self._appRoot.parent
            self._appPath = self._appRoot

        # Runtime Settings and Variables
        self._hasError   = False  # True if the config class encountered an error
        self._errData    = []     # List of error messages
        self.confChanged = False  # True whenever the config has chenged, false after save
        self.cmdOpen     = None   # Path from command line for project to be opened on launch

        # Localisation Info
        self._qLocal     = QLocale.system()
        self._qtTrans    = {}
        self._qtLangPath = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        self._nwLangPath = str(self._appPath / "assets" / "i18n")

        # PDF Manual
        pdfDocs = self._appPath / "assets" / "manual.pdf"
        self.pdfDocs = pdfDocs if pdfDocs.is_file() else None

        # User Settings
        # =============

        self._recentProj = RecentProjects(self)

        # General GUI Settings
        self.guiLang     = self._qLocal.name()
        self.guiTheme    = ""     # GUI theme
        self.guiSyntax   = ""     # Syntax theme
        self.guiFont     = ""     # Defaults to system default font
        self.guiFontSize = 11     # Is overridden if system default is loaded
        self.guiScale    = 1.0    # Set automatically by Theme class
        self.lastNotes   = "0x0"  # The latest release notes that have been shown

        self.setDefaultGuiTheme()
        self.setDefaultSyntaxTheme()

        # Size Settings
        self.winGeometry  = [1200, 650]
        self.prefGeometry = [700, 615]
        self.projColWidth = [200, 60, 140]
        self.mainPanePos  = [300, 800]
        self.docPanePos   = [400, 400]
        self.viewPanePos  = [500, 150]
        self.outlnPanePos = [500, 150]
        self.isFullScreen = False

        # Feature Settings
        self.hideVScroll = False  # Hide vertical scroll bars on main widgets
        self.hideHScroll = False  # Hide horizontal scroll bars on main widgets
        self.emphLabels  = True   # Add emphasis to H1 and H2 item labels

        # Project Settings
        self.autoSaveProj = 60  # Interval for auto-saving project in seconds
        self.autoSaveDoc  = 30  # Interval for auto-saving document in seconds

        # Text Editor Settings
        self.textFont        = None   # Editor font
        self.textSize        = 12     # Editor font size
        self.textWidth       = 700    # Editor text width
        self.textMargin      = 40     # Editor/viewer text margin
        self.tabWidth        = 40     # Editor tabulator width

        self.focusWidth      = 800    # Focus Mode text width
        self.hideFocusFooter = False  # Hide document footer in Focus Mode
        self.showFullPath    = True   # Show full document path in editor header
        self.autoSelect      = True   # Auto-select word when applying format with no selection

        self.doJustify       = False  # Justify text
        self.showTabsNSpaces = False  # Show tabs and spaces in edior
        self.showLineEndings = False  # Show line endings in editor
        self.showMultiSpaces = True   # Highlight multiple spaces in the text

        self.doReplace       = True   # Enable auto-replace as you type
        self.doReplaceSQuote = True   # Smart single quotes
        self.doReplaceDQuote = True   # Smart double quotes
        self.doReplaceDash   = True   # Replace multiple hyphens with dashes
        self.doReplaceDots   = True   # Replace three dots with ellipsis

        self.scrollPastEnd   = 25     # Number of lines to scroll past end of document
        self.autoScroll      = False  # Typewriter-like scrolling
        self.autoScrollPos   = 30     # Start point for typewriter-like scrolling

        self.wordCountTimer  = 5.0    # Interval for word count update in seconds
        self.bigDocLimit     = 800    # Size threshold for heavy editor features in kilobytes
        self.incNotesWCount  = True   # The status bar word count includes notes

        self.highlightQuotes = True   # Highlight text in quotes
        self.allowOpenSQuote = False  # Allow open-ended single quotes
        self.allowOpenDQuote = True   # Allow open-ended double quotes
        self.highlightEmph   = True   # Add colour to text emphasis

        self.stopWhenIdle    = True   # Stop the status bar clock when the user is idle
        self.userIdleTime    = 300    # Time of inactivity to consider user idle

        # User-Selected Symbol Settings
        self.fmtApostrophe   = nwUnicode.U_RSQUO
        self.fmtSingleQuotes = [nwUnicode.U_LSQUO, nwUnicode.U_RSQUO]
        self.fmtDoubleQuotes = [nwUnicode.U_LDQUO, nwUnicode.U_RDQUO]
        self.fmtPadBefore    = ""
        self.fmtPadAfter     = ""
        self.fmtPadThin      = False

        # Spell Checking Settings
        self.spellLanguage = "en"

        # Search Bar Switches
        self.searchCase     = False
        self.searchWord     = False
        self.searchRegEx    = False
        self.searchLoop     = False
        self.searchNextFile = False
        self.searchMatchCap = False

        # Backup Settings
        self._backupPath     = None
        self.backupOnClose   = False
        self.askBeforeBackup = True

        # State
        self.showRefPanel = True  # The reference panel for the viewer is visible
        self.viewComments = True  # Comments are shown in the viewer
        self.viewSynopsis = True  # Synopsis is shown in the viewer

        # System and App Information
        # ==========================

        # Check Qt5 Versions
        verQt = splitVersionNumber(QT_VERSION_STR)
        self.verQtString = QT_VERSION_STR
        self.verQtMajor  = verQt[0]
        self.verQtMinor  = verQt[1]
        self.verQtPatch  = verQt[2]
        self.verQtValue  = verQt[3]

        verQt = splitVersionNumber(PYQT_VERSION_STR)
        self.verPyQtString = PYQT_VERSION_STR
        self.verPyQtMajor  = verQt[0]
        self.verPyQtMinor  = verQt[1]
        self.verPyQtPatch  = verQt[2]
        self.verPyQtValue  = verQt[3]

        # Check Python Version
        self.verPyString = sys.version.split()[0]
        self.verPyMajor  = sys.version_info[0]
        self.verPyMinor  = sys.version_info[1]
        self.verPyPatch  = sys.version_info[2]
        self.verPyHexVal = sys.hexversion

        # Check OS Type
        self.osType    = sys.platform
        self.osLinux   = False
        self.osWindows = False
        self.osDarwin  = False
        self.osUnknown = False
        if self.osType.startswith("linux"):
            self.osLinux = True
        elif self.osType.startswith("darwin"):
            self.osDarwin = True
        elif self.osType.startswith("win32"):
            self.osWindows = True
        elif self.osType.startswith("cygwin"):
            self.osWindows = True
        else:
            self.osUnknown = True

        # Other System Info
        self.hostName  = QSysInfo.machineHostName()
        self.kernelVer = QSysInfo.kernelVersion()

        # Packages
        self.hasEnchant = False  # The pyenchant package

        # Recent Cache
        self.recentProj = {}

        return

    ##
    #  Properties
    ##

    @property
    def hasError(self):
        return self._hasError

    @property
    def recentProjects(self):
        return self._recentProj

    ##
    #  Methods
    ##

    def pxInt(self, theSize):
        """Used to scale fixed gui sizes by the screen scale factor.
        This function returns an int, which is always rounded down.
        """
        return int(theSize*self.guiScale)

    def rpxInt(self, theSize):
        """Used to un-scale fixed gui sizes by the screen scale factor.
        This function returns an int, which is always rounded down.
        """
        return int(theSize/self.guiScale)

    def dataPath(self, target=None):
        """Return a path in the data folder.
        """
        if isinstance(target, str):
            return self._dataPath / target
        return self._dataPath

    def assetPath(self, target=None):
        """Return a path in the assets folder.
        """
        if isinstance(target, str):
            return self._appPath / "assets" / target
        return self._appPath / "assets"

    def lastPath(self):
        """Return the last path used by the user, but ensure it exists.
        """
        if self._lastPath.is_dir():
            return self._lastPath
        return Path.home().absolute()

    def backupPath(self):
        """Return the backup path.
        """
        if isinstance(self._backupPath, Path):
            if self._backupPath.is_dir():
                return self._backupPath
        return None

    def errorText(self):
        """Compile and return error messages from the initialisation of
        the Config class, and clear the error buffer.
        """
        errMessage = "<br>".join(self._errData)
        self._hasError = False
        self._errData = []
        return errMessage

    ##
    #  Config Actions
    ##

    def initConfig(self, confPath=None, dataPath=None):
        """Initialise the config class. The manual setting of confPath
        and dataPath is mainly intended for the test suite.
        """
        logger.debug("Initialising Config ...")
        if isinstance(confPath, (str, Path)):
            logger.info("Setting config from alternative path: %s", confPath)
            self._confPath = Path(confPath)
        if isinstance(dataPath, (str, Path)):
            logger.info("Setting data path from alternative path: %s", dataPath)
            self._dataPath = Path(dataPath)

        logger.debug("Config Path: %s", self._confPath)
        logger.debug("Data Path: %s", self._dataPath)
        logger.debug("App Root: %s", self._appRoot)
        logger.debug("App Path: %s", self._appPath)
        logger.debug("Last Path: %s", self._lastPath)
        logger.debug("PDF Manual: %s", self.pdfDocs)

        # If the config and data folders don't exist, create them
        # This assumes that the os config and data folders exist
        self._confPath.mkdir(exist_ok=True)
        self._dataPath.mkdir(exist_ok=True)

        # Also create the syntax and themes folders if possible
        if self._dataPath.is_dir():
            (self._dataPath / "syntax").mkdir(exist_ok=True)
            (self._dataPath / "themes").mkdir(exist_ok=True)

        # Check if config file exists, and load it. If not, we save defaults
        if (self._confPath / nwFiles.CONF_FILE).is_file():
            self.loadConfig()
        else:
            self.saveConfig()

        self._recentProj.loadCache()
        self._checkOptionalPackages()

        logger.debug("Config initialisation complete")

        return

    def initLocalisation(self, nwApp):
        """Initialise the localisation of the GUI.
        """
        self._qLocal = QLocale(self.guiLang)
        QLocale.setDefault(self._qLocal)
        self._qtTrans = {}

        langList = [
            (self._qtLangPath, "qtbase"),  # Qt 5.x
            (self._nwLangPath, "qtbase"),  # Alternative Qt 5.x
            (self._nwLangPath, "nw"),      # novelWriter
        ]
        for lngPath, lngBase in langList:
            for lngCode in self._qLocal.uiLanguages():
                qTrans = QTranslator()
                lngFile = "%s_%s" % (lngBase, lngCode.replace("-", "_"))
                if lngFile not in self._qtTrans:
                    if qTrans.load(lngFile, str(lngPath)):
                        logger.debug("Loaded: %s/%s", lngPath, lngFile)
                        nwApp.installTranslator(qTrans)
                        self._qtTrans[lngFile] = qTrans

        return

    def listLanguages(self, lngSet):
        """List localisation files in the i18n folder. The default GUI
        language is British English (en_GB).
        """
        if lngSet == self.LANG_NW:
            fPre = "nw_"
            fExt = ".qm"
            langList = {"en_GB": QLocale("en_GB").nativeLanguageName().title()}
        elif lngSet == self.LANG_PROJ:
            fPre = "project_"
            fExt = ".json"
            langList = {"en_GB": QLocale("en_GB").nativeLanguageName().title()}
        else:
            return []

        for qmFile in Path(self._nwLangPath).iterdir():
            qmName = qmFile.name
            if not (qmFile.is_file() and qmName.startswith(fPre) and qmName.endswith(fExt)):
                continue

            qmLang = qmName[len(fPre):-len(fExt)]
            qmName = QLocale(qmLang).nativeLanguageName().title()
            if qmLang and qmName and qmLang != "en_GB":
                langList[qmLang] = qmName

        return sorted(langList.items(), key=lambda x: x[0])

    def loadConfig(self):
        """Load preferences from file and replace default settings.
        """
        logger.debug("Loading config file")

        theConf = NWConfigParser()
        cnfPath = self._confPath / nwFiles.CONF_FILE
        try:
            with open(cnfPath, mode="r", encoding="utf-8") as inFile:
                theConf.read_file(inFile)
        except Exception as exc:
            logger.error("Could not load config file")
            logException()
            self._hasError = True
            self._errData.append("Could not load config file")
            self._errData.append(formatException(exc))
            return False

        # Main
        cnfSec = "Main"
        self.guiTheme    = theConf.rdStr(cnfSec, "theme", self.guiTheme)
        self.guiSyntax   = theConf.rdStr(cnfSec, "syntax", self.guiSyntax)
        self.guiFont     = theConf.rdStr(cnfSec, "guifont", self.guiFont)
        self.guiFontSize = theConf.rdInt(cnfSec, "guifontsize", self.guiFontSize)
        self.lastNotes   = theConf.rdStr(cnfSec, "lastnotes", self.lastNotes)
        self.guiLang     = theConf.rdStr(cnfSec, "guilang", self.guiLang)
        self.hideVScroll = theConf.rdBool(cnfSec, "hidevscroll", self.hideVScroll)
        self.hideHScroll = theConf.rdBool(cnfSec, "hidehscroll", self.hideHScroll)

        # Sizes
        cnfSec = "Sizes"
        self.winGeometry   = theConf.rdIntList(cnfSec, "geometry", self.winGeometry)
        self.prefGeometry  = theConf.rdIntList(cnfSec, "preferences", self.prefGeometry)
        self.projColWidth  = theConf.rdIntList(cnfSec, "projcols", self.projColWidth)
        self.mainPanePos   = theConf.rdIntList(cnfSec, "mainpane", self.mainPanePos)
        self.docPanePos    = theConf.rdIntList(cnfSec, "docpane", self.docPanePos)
        self.viewPanePos   = theConf.rdIntList(cnfSec, "viewpane", self.viewPanePos)
        self.outlnPanePos  = theConf.rdIntList(cnfSec, "outlinepane", self.outlnPanePos)
        self.isFullScreen  = theConf.rdBool(cnfSec, "fullscreen", self.isFullScreen)

        # Project
        cnfSec = "Project"
        self.autoSaveProj = theConf.rdInt(cnfSec, "autosaveproject", self.autoSaveProj)
        self.autoSaveDoc  = theConf.rdInt(cnfSec, "autosavedoc", self.autoSaveDoc)
        self.emphLabels   = theConf.rdBool(cnfSec, "emphlabels", self.emphLabels)

        # Editor
        cnfSec = "Editor"
        self.textFont        = theConf.rdStr(cnfSec, "textfont", self.textFont)
        self.textSize        = theConf.rdInt(cnfSec, "textsize", self.textSize)
        self.textWidth       = theConf.rdInt(cnfSec, "width", self.textWidth)
        self.textMargin      = theConf.rdInt(cnfSec, "margin", self.textMargin)
        self.tabWidth        = theConf.rdInt(cnfSec, "tabwidth", self.tabWidth)
        self.focusWidth      = theConf.rdInt(cnfSec, "focuswidth", self.focusWidth)
        self.hideFocusFooter = theConf.rdBool(cnfSec, "hidefocusfooter", self.hideFocusFooter)
        self.doJustify       = theConf.rdBool(cnfSec, "justify", self.doJustify)
        self.autoSelect      = theConf.rdBool(cnfSec, "autoselect", self.autoSelect)
        self.doReplace       = theConf.rdBool(cnfSec, "autoreplace", self.doReplace)
        self.doReplaceSQuote = theConf.rdBool(cnfSec, "repsquotes", self.doReplaceSQuote)
        self.doReplaceDQuote = theConf.rdBool(cnfSec, "repdquotes", self.doReplaceDQuote)
        self.doReplaceDash   = theConf.rdBool(cnfSec, "repdash", self.doReplaceDash)
        self.doReplaceDots   = theConf.rdBool(cnfSec, "repdots", self.doReplaceDots)
        self.scrollPastEnd   = theConf.rdInt(cnfSec, "scrollpastend", self.scrollPastEnd)
        self.autoScroll      = theConf.rdBool(cnfSec, "autoscroll", self.autoScroll)
        self.autoScrollPos   = theConf.rdInt(cnfSec, "autoscrollpos", self.autoScrollPos)
        self.fmtSingleQuotes = theConf.rdStrList(cnfSec, "fmtsinglequote", self.fmtSingleQuotes)
        self.fmtDoubleQuotes = theConf.rdStrList(cnfSec, "fmtdoublequote", self.fmtDoubleQuotes)
        self.fmtPadBefore    = theConf.rdStr(cnfSec, "fmtpadbefore", self.fmtPadBefore)
        self.fmtPadAfter     = theConf.rdStr(cnfSec, "fmtpadafter", self.fmtPadAfter)
        self.fmtPadThin      = theConf.rdBool(cnfSec, "fmtpadthin", self.fmtPadThin)
        self.spellLanguage   = theConf.rdStr(cnfSec, "spellcheck", self.spellLanguage)
        self.showTabsNSpaces = theConf.rdBool(cnfSec, "showtabsnspaces", self.showTabsNSpaces)
        self.showLineEndings = theConf.rdBool(cnfSec, "showlineendings", self.showLineEndings)
        self.showMultiSpaces = theConf.rdBool(cnfSec, "showmultispaces", self.showMultiSpaces)
        self.wordCountTimer  = theConf.rdFlt(cnfSec, "wordcounttimer", self.wordCountTimer)
        self.bigDocLimit     = theConf.rdInt(cnfSec, "bigdoclimit", self.bigDocLimit)
        self.incNotesWCount  = theConf.rdBool(cnfSec, "incnoteswcount", self.incNotesWCount)
        self.showFullPath    = theConf.rdBool(cnfSec, "showfullpath", self.showFullPath)
        self.highlightQuotes = theConf.rdBool(cnfSec, "highlightquotes", self.highlightQuotes)
        self.allowOpenSQuote = theConf.rdBool(cnfSec, "allowopensquote", self.allowOpenSQuote)
        self.allowOpenDQuote = theConf.rdBool(cnfSec, "allowopendquote", self.allowOpenDQuote)
        self.highlightEmph   = theConf.rdBool(cnfSec, "highlightemph", self.highlightEmph)
        self.stopWhenIdle    = theConf.rdBool(cnfSec, "stopwhenidle", self.stopWhenIdle)
        self.userIdleTime    = theConf.rdInt(cnfSec, "useridletime", self.userIdleTime)

        # Backup
        cnfSec = "Backup"
        backupPath           = theConf.rdStr(cnfSec, "backuppath", None)
        self.backupOnClose   = theConf.rdBool(cnfSec, "backuponclose", self.backupOnClose)
        self.askBeforeBackup = theConf.rdBool(cnfSec, "askbeforebackup", self.askBeforeBackup)
        self.setBackupPath(backupPath)

        # State
        cnfSec = "State"
        self.showRefPanel   = theConf.rdBool(cnfSec, "showrefpanel", self.showRefPanel)
        self.viewComments   = theConf.rdBool(cnfSec, "viewcomments", self.viewComments)
        self.viewSynopsis   = theConf.rdBool(cnfSec, "viewsynopsis", self.viewSynopsis)
        self.searchCase     = theConf.rdBool(cnfSec, "searchcase", self.searchCase)
        self.searchWord     = theConf.rdBool(cnfSec, "searchword", self.searchWord)
        self.searchRegEx    = theConf.rdBool(cnfSec, "searchregex", self.searchRegEx)
        self.searchLoop     = theConf.rdBool(cnfSec, "searchloop", self.searchLoop)
        self.searchNextFile = theConf.rdBool(cnfSec, "searchnextfile", self.searchNextFile)
        self.searchMatchCap = theConf.rdBool(cnfSec, "searchmatchcap", self.searchMatchCap)

        # Path
        cnfSec = "Path"
        self._lastPath = Path(theConf.rdStr(cnfSec, "lastpath", self._lastPath))

        # Check Certain Values for None
        self.spellLanguage = self._checkNone(self.spellLanguage)

        # If we're using straight quotes, disable auto-replace
        if self.fmtSingleQuotes == ["'", "'"] and self.doReplaceSQuote:
            logger.info("Using straight single quotes, so disabling auto-replace")
            self.doReplaceSQuote = False

        if self.fmtDoubleQuotes == ['"', '"'] and self.doReplaceDQuote:
            logger.info("Using straight double quotes, so disabling auto-replace")
            self.doReplaceDQuote = False

        return True

    def saveConfig(self):
        """Save the current preferences to file.
        """
        logger.debug("Saving config file")

        theConf = NWConfigParser()

        theConf["Main"] = {
            "timestamp":   formatTimeStamp(time()),
            "theme":       str(self.guiTheme),
            "syntax":      str(self.guiSyntax),
            "guifont":     str(self.guiFont),
            "guifontsize": str(self.guiFontSize),
            "lastnotes":   str(self.lastNotes),
            "guilang":     str(self.guiLang),
            "hidevscroll": str(self.hideVScroll),
            "hidehscroll": str(self.hideHScroll),
        }

        theConf["Sizes"] = {
            "geometry":    self._packList(self.winGeometry),
            "preferences": self._packList(self.prefGeometry),
            "projcols":    self._packList(self.projColWidth),
            "mainpane":    self._packList(self.mainPanePos),
            "docpane":     self._packList(self.docPanePos),
            "viewpane":    self._packList(self.viewPanePos),
            "outlinepane": self._packList(self.outlnPanePos),
            "fullscreen":  str(self.isFullScreen),
        }

        theConf["Project"] = {
            "autosaveproject": str(self.autoSaveProj),
            "autosavedoc":     str(self.autoSaveDoc),
            "emphlabels":      str(self.emphLabels),
        }

        theConf["Editor"] = {
            "textfont":        str(self.textFont),
            "textsize":        str(self.textSize),
            "width":           str(self.textWidth),
            "margin":          str(self.textMargin),
            "tabwidth":        str(self.tabWidth),
            "focuswidth":      str(self.focusWidth),
            "hidefocusfooter": str(self.hideFocusFooter),
            "justify":         str(self.doJustify),
            "autoselect":      str(self.autoSelect),
            "autoreplace":     str(self.doReplace),
            "repsquotes":      str(self.doReplaceSQuote),
            "repdquotes":      str(self.doReplaceDQuote),
            "repdash":         str(self.doReplaceDash),
            "repdots":         str(self.doReplaceDots),
            "scrollpastend":   str(self.scrollPastEnd),
            "autoscroll":      str(self.autoScroll),
            "autoscrollpos":   str(self.autoScrollPos),
            "fmtsinglequote":  self._packList(self.fmtSingleQuotes),
            "fmtdoublequote":  self._packList(self.fmtDoubleQuotes),
            "fmtpadbefore":    str(self.fmtPadBefore),
            "fmtpadafter":     str(self.fmtPadAfter),
            "fmtpadthin":      str(self.fmtPadThin),
            "spellcheck":      str(self.spellLanguage),
            "showtabsnspaces": str(self.showTabsNSpaces),
            "showlineendings": str(self.showLineEndings),
            "showmultispaces": str(self.showMultiSpaces),
            "wordcounttimer":  str(self.wordCountTimer),
            "bigdoclimit":     str(self.bigDocLimit),
            "incnoteswcount":  str(self.incNotesWCount),
            "showfullpath":    str(self.showFullPath),
            "highlightquotes": str(self.highlightQuotes),
            "allowopensquote": str(self.allowOpenSQuote),
            "allowopendquote": str(self.allowOpenDQuote),
            "highlightemph":   str(self.highlightEmph),
            "stopwhenidle":    str(self.stopWhenIdle),
            "useridletime":    str(self.userIdleTime),
        }

        theConf["Backup"] = {
            "backuppath":      str(self._backupPath or ""),
            "backuponclose":   str(self.backupOnClose),
            "askbeforebackup": str(self.askBeforeBackup),
        }

        theConf["State"] = {
            "showrefpanel":    str(self.showRefPanel),
            "viewcomments":    str(self.viewComments),
            "viewsynopsis":    str(self.viewSynopsis),
            "searchcase":      str(self.searchCase),
            "searchword":      str(self.searchWord),
            "searchregex":     str(self.searchRegEx),
            "searchloop":      str(self.searchLoop),
            "searchnextfile":  str(self.searchNextFile),
            "searchmatchcap":  str(self.searchMatchCap),
        }

        theConf["Path"] = {
            "lastpath": str(self._lastPath),
        }

        # Write config file
        cnfPath = self._confPath / nwFiles.CONF_FILE
        try:
            with open(cnfPath, mode="w", encoding="utf-8") as outFile:
                theConf.write(outFile)
            self.confChanged = False
        except Exception as exc:
            logger.error("Could not save config file")
            logException()
            self._hasError = True
            self._errData.append("Could not save config file")
            self._errData.append(formatException(exc))
            return False

        return True

    ##
    #  Setters
    ##

    def setLastPath(self, lastPath):
        """Set the last used path. Only the folder is saved, so if the
        path is not a folder, the parent of the path is used instead.
        """
        if isinstance(lastPath, (str, Path)):
            lastPath = Path(lastPath)
            if not lastPath.is_dir():
                lastPath = lastPath.parent
            if lastPath.is_dir():
                self._lastPath = lastPath
                logger.debug("Last path updated: %s" % self._lastPath)
        return

    def setBackupPath(self, backupPath):
        """Set the current backup path.
        """
        self._backupPath = None
        if isinstance(backupPath, (str, Path)):
            self._backupPath = Path(backupPath)
        return

    def setWinSize(self, newWidth, newHeight):
        """Set the size of the main window, but only if the change is
        larger than 5 pixels. The OS window manager will sometimes
        adjust it a bit, and we don't want the main window to shrink or
        grow each time the app is opened.
        """
        newWidth = int(newWidth/self.guiScale)
        newHeight = int(newHeight/self.guiScale)
        if abs(self.winGeometry[0] - newWidth) > 5:
            self.winGeometry[0] = newWidth
            self.confChanged = True
        if abs(self.winGeometry[1] - newHeight) > 5:
            self.winGeometry[1] = newHeight
            self.confChanged = True
        return

    def setPreferencesSize(self, newWidth, newHeight):
        """Sat the size of the Preferences dialog window.
        """
        self.prefGeometry[0] = int(newWidth/self.guiScale)
        self.prefGeometry[1] = int(newHeight/self.guiScale)
        self.confChanged = True
        return

    def setProjColWidths(self, colWidths):
        """Set the column widths of the Load Project dialog.
        """
        self.projColWidth = [int(x/self.guiScale) for x in colWidths]
        self.confChanged = True
        return

    def setMainPanePos(self, panePos):
        """Set the position of the main GUI splitter.
        """
        self.mainPanePos = [int(x/self.guiScale) for x in panePos]
        self.confChanged = True
        return

    def setDocPanePos(self, panePos):
        """Set the position of the main editor/viewer splitter.
        """
        self.docPanePos = [int(x/self.guiScale) for x in panePos]
        self.confChanged = True
        return

    def setViewPanePos(self, panePos):
        """Set the position of the viewer meta data splitter.
        """
        self.viewPanePos = [int(x/self.guiScale) for x in panePos]
        self.confChanged = True
        return

    def setOutlinePanePos(self, panePos):
        """Set the position of the outline details splitter.
        """
        self.outlnPanePos = [int(x/self.guiScale) for x in panePos]
        self.confChanged = True
        return

    def setShowRefPanel(self, checkState):
        """Set the visibility state of the reference panel.
        """
        self.showRefPanel = checkState
        self.confChanged = True
        return

    def setViewComments(self, viewState):
        """Set the visibility state of comments in the viewer.
        """
        self.viewComments = viewState
        self.confChanged = True
        return

    def setViewSynopsis(self, viewState):
        """Set the visibility state of synopsis comments in the viewer.
        """
        self.viewSynopsis = viewState
        self.confChanged = True
        return

    ##
    #  Default Setters
    ##

    def setDefaultGuiTheme(self):
        """Reset the GUI theme to default value.
        """
        self.guiTheme = "default"

    def setDefaultSyntaxTheme(self):
        """Reset the syntax theme to default value.
        """
        self.guiSyntax = "default_light"

    ##
    #  Getters
    ##

    def getWinSize(self):
        return [int(x*self.guiScale) for x in self.winGeometry]

    def getPreferencesSize(self):
        return [int(x*self.guiScale) for x in self.prefGeometry]

    def getProjColWidths(self):
        return [int(x*self.guiScale) for x in self.projColWidth]

    def getMainPanePos(self):
        return [int(x*self.guiScale) for x in self.mainPanePos]

    def getDocPanePos(self):
        return [int(x*self.guiScale) for x in self.docPanePos]

    def getViewPanePos(self):
        return [int(x*self.guiScale) for x in self.viewPanePos]

    def getOutlinePanePos(self):
        return [int(x*self.guiScale) for x in self.outlnPanePos]

    def getTextWidth(self, focusMode=False):
        if focusMode:
            return self.pxInt(max(self.focusWidth, 200))
        else:
            return self.pxInt(max(self.textWidth, 200))

    def getTextMargin(self):
        return self.pxInt(max(self.textMargin, 0))

    def getTabWidth(self):
        return self.pxInt(max(self.tabWidth, 0))

    ##
    #  Internal Functions
    ##

    def _packList(self, inData):
        """Pack a list of items into a comma-separated string for saving
        to the config file.
        """
        return ", ".join([str(inVal) for inVal in inData])

    def _checkNone(self, checkVal):
        """Return a NoneType if the value corresponds to None, otherwise
        return the value unchanged.
        """
        if checkVal is None:
            return None
        if isinstance(checkVal, str):
            if checkVal.lower() == "none":
                return None
        return checkVal

    def _checkOptionalPackages(self):
        """Cheks if we have the optional packages used by some features.
        """
        try:
            import enchant  # noqa: F401
        except ImportError:
            self.hasEnchant = False
            logger.debug("Checking package 'pyenchant': Missing")
        else:
            self.hasEnchant = True
            logger.debug("Checking package 'pyenchant': OK")
        return

# END Class Config


class RecentProjects:

    def __init__(self, mainConf):
        self.mainConf = mainConf
        self._data = {}
        return

    def loadCache(self):
        """Load the cache file for recent projects.
        """
        self._data = {}

        cacheFile = self.mainConf.dataPath(nwFiles.RECENT_FILE)
        if not cacheFile.is_file():
            return True

        try:
            with open(cacheFile, mode="r", encoding="utf-8") as inFile:
                theData = json.load(inFile)
            for projPath, theEntry in theData.items():
                self._data[projPath] = {
                    "title": theEntry.get("title", ""),
                    "words": theEntry.get("words", 0),
                    "time": theEntry.get("time", 0),
                }
        except Exception:
            logger.error("Could not load recent project cache")
            logException()
            return False

        return True

    def saveCache(self):
        """Save the cache dictionary of recent projects.
        """
        cacheFile = self.mainConf.dataPath(nwFiles.RECENT_FILE)
        cacheTemp = cacheFile.with_suffix(".tmp")
        try:
            with open(cacheTemp, mode="w+", encoding="utf-8") as outFile:
                json.dump(self._data, outFile, indent=2)
            cacheTemp.replace(cacheFile)
        except Exception:
            logger.error("Could not save recent project cache")
            logException()
            return False

        return True

    def listEntries(self):
        """List all items in the cache.
        """
        return [(k, e["title"], e["words"], e["time"]) for k, e in self._data.items()]

    def update(self, projPath, projTitle, wordCount, saveTime):
        """Add or update recent cache information on a given project.
        """
        self._data[str(projPath)] = {
            "title": projTitle,
            "words": int(wordCount),
            "time": int(saveTime),
        }
        self.saveCache()
        return

    def remove(self, projPath):
        """Try to remove a path from the recent projects cache.
        """
        if self._data.pop(str(projPath), None) is not None:
            logger.debug("Removed recent: %s", projPath)
            self.saveCache()
        return

# END Class RecentProjects
