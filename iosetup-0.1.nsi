;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Interstate Outlaws 0.1.0 Alpha"
  OutFile "IOSetup-0.1.0.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Interstate Outlaws"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Interstate Outlaws" ""

  ;Vista redirects $SMPROGRAMS to all users without this
  RequestExecutionLevel admin

;--------------------------------
;Variables

  Var MUI_TEMP
  Var STARTMENU_FOLDER

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
; !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY

  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Interstate Outlaws" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
  !insertmacro MUI_PAGE_STARTMENU Application $STARTMENU_FOLDER

  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Dummy Section" SecDummy

  SetOutPath "$INSTDIR"
  
  ;ADD YOUR OWN FILES HERE...
  File /r /x *~ /x *.pyc *

  ;tell user they need python!

  MessageBox MB_YESNO "Python is Required for Interstate Outlaws to run. Would you like to install it now?" /SD IDYES IDNO endPython
    ExecWait '"msiexec" /i "$INSTDIR\utils\python-2.4.4.msi"'
    Goto endPython
  endPython:
  
  ;Store installation folder
  WriteRegStr HKCU "Software\Interstate Outlaws" "" $INSTDIR

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts for all users
    setshellvarcontext all
    CreateDirectory "$SMPROGRAMS\$STARTMENU_FOLDER"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Interstate Outlaws.lnk" "$INSTDIR\outlaws.py" "" "$INSTDIR\outlaws.ico"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\IO Server.lnk" "$INSTDIR\outlaws-lobbyserver.py" "" "$INSTDIR\outlaws.ico"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\ReadMe.lnk" "$INSTDIR\readme.txt"
    CreateShortCut "$SMPROGRAMS\$STARTMENU_FOLDER\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortCut "$DESKTOP\Interstate Outlaws.lnk" "$INSTDIR\outlaws.py" "" "$INSTDIR\outlaws.ico"
  !insertmacro MUI_STARTMENU_WRITE_END


  ;Create uninstaller

  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "A test section."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...

  RMDir /r "$INSTDIR"

  !insertmacro MUI_STARTMENU_GETFOLDER Application $MUI_TEMP
    
  Delete "$SMPROGRAMS\$MUI_TEMP\Uninstall.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\Interstate Outlaws.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\IO Server.lnk"
  Delete "$SMPROGRAMS\$MUI_TEMP\readme.lnk"
  Delete "$DESKTOP\Interstate Outlaws.lnk"

  ;Delete empty start menu parent diretories
  StrCpy $MUI_TEMP "$SMPROGRAMS\$MUI_TEMP"
 
  startMenuDeleteLoop:
	ClearErrors
    RMDir $MUI_TEMP
    GetFullPathName $MUI_TEMP "$MUI_TEMP\.."
    
    IfErrors startMenuDeleteLoopDone
  
    StrCmp $MUI_TEMP $SMPROGRAMS startMenuDeleteLoopDone startMenuDeleteLoop
  startMenuDeleteLoopDone:

  DeleteRegKey /ifempty HKCU "Software\Interstate Outlaws"

SectionEnd