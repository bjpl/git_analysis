; NSIS Script for Unsplash Image Search & GPT Description Tool
; Creates a professional Windows installer with modern UI
; Compatible with NSIS 3.08+

;--------------------------------
; Modern UI Configuration
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"

;--------------------------------
; Application Information
!define APP_NAME "Unsplash Image Search GPT Tool"
!define APP_VERSION "2.0.0"
!define APP_PUBLISHER "Language Learning Tools"
!define APP_URL "https://github.com/yourusername/unsplash-image-search-gpt"
!define APP_EXE "Unsplash_Image_Search_GPT_Tool_v2.0.0.exe"
!define APP_DESCRIPTION "AI-powered image search and Spanish vocabulary learning tool"
!define APP_GUID "{8A5B2C1D-9E4F-4A3B-B8C7-D6E9F0A1B2C3}"
!define APP_REGKEY "Software\${APP_PUBLISHER}\${APP_NAME}"
!define APP_UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_GUID}"

; Installer Configuration
Name "${APP_NAME}"
OutFile "..\dist\${APP_NAME}_Setup_v${APP_VERSION}.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKCU "${APP_REGKEY}" "InstallPath"
RequestExecutionLevel admin
ShowInstDetails show
ShowUnInstDetails show
Compressor /SOLID lzma
SetCompressor lzma

; Version Information
VIProductVersion "2.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "Copyright © 2024 ${APP_PUBLISHER}. All rights reserved."
VIAddVersionKey "FileDescription" "${APP_DESCRIPTION}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"

;--------------------------------
; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "app_icon.ico"
!define MUI_UNICON "app_icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "installer_header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer_wizard.bmp"
!define MUI_COMPONENTSPAGE_SMALLDESC

; Custom colors and fonts
!define MUI_TEXTCOLOR 0x000000
!define MUI_BGCOLOR 0xFFFFFF
!define MUI_INSTALLCOLORS /windows

;--------------------------------
; Pages Configuration

; Welcome Page
!define MUI_WELCOMEPAGE_TITLE "Welcome to ${APP_NAME} Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of ${APP_NAME}.$\r$\n$\r$\n${APP_DESCRIPTION}$\r$\n$\r$\nBefore starting the installation, please ensure you have:$\r$\n• OpenAI API key$\r$\n• Unsplash API key$\r$\n• Internet connection$\r$\n$\r$\nClick Next to continue."
!insertmacro MUI_PAGE_WELCOME

; License Page
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"

; Components Page
!insertmacro MUI_PAGE_COMPONENTS

; Directory Page
!insertmacro MUI_PAGE_DIRECTORY

; Start Menu Page
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${APP_REGKEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
Var StartMenuFolder
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

; Installation Page
!insertmacro MUI_PAGE_INSTFILES

; Finish Page
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!define MUI_FINISHPAGE_LINK "Visit our website for updates and support"
!define MUI_FINISHPAGE_LINK_LOCATION "${APP_URL}"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\docs\README.md"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View User Manual"
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Spanish"

;--------------------------------
; Installation Types and Components

InstType "Complete Installation"
InstType "Minimal Installation"
InstType "Portable Installation"

; Main Application Component
Section "${APP_NAME}" SecMain
  SectionIn 1 2 3 RO
  
  ; Set output path to installation directory
  SetOutPath "$INSTDIR"
  
  ; Install main executable
  File "..\dist\${APP_EXE}"
  
  ; Install configuration files
  File /nonfatal "..\dist\.env.example"
  
  ; Create data directory
  CreateDirectory "$INSTDIR\data"
  
  ; Install documentation
  CreateDirectory "$INSTDIR\docs"
  File /nonfatal /oname=docs\README.md "..\README.md"
  File /nonfatal /oname=docs\LICENSE "..\LICENSE"
  File /nonfatal /oname=docs\checksums.json "..\dist\checksums.json"
  
  ; Install source files (for reference)
  File /r /nonfatal "..\dist\src"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Write installation info to registry
  WriteRegStr HKCU "${APP_REGKEY}" "InstallPath" "$INSTDIR"
  WriteRegStr HKCU "${APP_REGKEY}" "Version" "${APP_VERSION}"
  WriteRegDWORD HKCU "${APP_REGKEY}" "InstallDate" $R0
  
  ; Write uninstall information
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "QuietUninstallString" "$INSTDIR\Uninstall.exe /S"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "URLInfoAbout" "${APP_URL}"
  WriteRegStr HKLM "${APP_UNINSTALL_KEY}" "HelpLink" "${APP_URL}"
  WriteRegDWORD HKLM "${APP_UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${APP_UNINSTALL_KEY}" "NoRepair" 1
  
  ; Calculate and write installation size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "${APP_UNINSTALL_KEY}" "EstimatedSize" "$0"
  
SectionEnd

; Desktop Shortcut
Section "Desktop Shortcut" SecDesktop
  SectionIn 1
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

; Start Menu Shortcuts
Section "Start Menu Shortcuts" SecStartMenu
  SectionIn 1 2
  
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  
  CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
  CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
  CreateShortCut "$SMPROGRAMS\$StartMenuFolder\User Manual.lnk" "$INSTDIR\docs\README.md" "" "$SYSDIR\shell32.dll" 70
  CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  
  !insertmacro MUI_STARTMENU_WRITE_END
  
SectionEnd

; Quick Launch Shortcut
Section "Quick Launch Shortcut" SecQuickLaunch
  SectionIn 1
  ; Only create if Quick Launch exists (Windows 7 and earlier)
  IfFileExists "$QUICKLAUNCH" 0 +2
  CreateShortCut "$QUICKLAUNCH\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

; File Associations
Section "File Associations" SecAssoc
  SectionIn 1
  
  ; Register .unsplash file extension
  WriteRegStr HKCR ".unsplash" "" "UnsplashProject"
  WriteRegStr HKCR "UnsplashProject" "" "Unsplash Project File"
  WriteRegStr HKCR "UnsplashProject\DefaultIcon" "" "$INSTDIR\${APP_EXE},0"
  WriteRegStr HKCR "UnsplashProject\shell\open\command" "" '"$INSTDIR\${APP_EXE}" "%1"'
  
  ; Notify Windows of the association change
  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)'
  
SectionEnd

; Auto-start Option
Section /o "Start with Windows" SecAutoStart
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APP_NAME}" '"$INSTDIR\${APP_EXE}" --minimized'
SectionEnd

;--------------------------------
; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Core application files. This component is required."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a shortcut on the desktop for easy access."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create shortcuts in the Start Menu."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecQuickLaunch} "Create a shortcut in the Quick Launch toolbar."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecAssoc} "Associate .unsplash files with ${APP_NAME}."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecAutoStart} "Automatically start ${APP_NAME} when Windows starts."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Installation Functions

Function .onInit
  ; Check Windows version (require Windows 7 SP1 or later)
  ${IfNot} ${AtLeastWin7}
    MessageBox MB_OK|MB_ICONSTOP "This application requires Windows 7 SP1 or later."
    Abort
  ${EndIf}
  
  ; Check if 64-bit Windows
  ${IfNot} ${RunningX64}
    MessageBox MB_OK|MB_ICONSTOP "This application requires a 64-bit version of Windows."
    Abort
  ${EndIf}
  
  ; Check if application is already running
  System::Call 'kernel32::CreateMutex(p 0, b 0, t "UnsplashGPTToolMutex") p .r1 ?e'
  Pop $R0
  StrCmp $R0 0 +3
    MessageBox MB_OK|MB_ICONSTOP "${APP_NAME} is already running. Please close it and try again."
    Abort
  
  ; Check for previous installation
  ReadRegStr $R0 HKCU "${APP_REGKEY}" "InstallPath"
  ${If} $R0 != ""
    StrCpy $INSTDIR $R0
    MessageBox MB_YESNO|MB_ICONQUESTION "${APP_NAME} is already installed at $R0.$\r$\nDo you want to upgrade it?" IDYES +2
    Abort
  ${EndIf}
  
  ; Get current date/time for registry
  System::Call "kernel32::GetSystemTimeAsFileTime(*l) v"
  System::Int64Op $0 / 10000000
  Pop $R0
  
FunctionEnd

; Custom installation page
Function CustomInstallPage
  ; Check available disk space
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  System::Call "kernel32::GetDiskFreeSpaceEx(t '$INSTDIR', *l, *l, *l) b"
  Pop $R0
  ${If} $R0 == 0
    MessageBox MB_OK|MB_ICONSTOP "Unable to determine available disk space."
    Abort
  ${EndIf}
FunctionEnd

;--------------------------------
; Uninstaller

Section "Uninstall"
  
  ; Stop the application if running
  ExecWait 'taskkill /F /IM "${APP_EXE}" /T' $0
  Sleep 1000
  
  ; Remove files
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\.env.example"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Remove directories
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\src"
  RMDir /r "$INSTDIR\data"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$QUICKLAUNCH\${APP_NAME}.lnk"
  
  ; Remove Start Menu shortcuts
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\User Manual.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  
  ; Remove registry entries
  DeleteRegKey HKCU "${APP_REGKEY}"
  DeleteRegKey HKLM "${APP_UNINSTALL_KEY}"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APP_NAME}"
  
  ; Remove file associations
  DeleteRegKey HKCR ".unsplash"
  DeleteRegKey HKCR "UnsplashProject"
  
  ; Notify Windows of the association change
  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)'
  
  ; Ask user if they want to remove user data
  MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to remove your personal settings and data?$\r$\n$\r$\nThis includes:$\r$\n• Configuration files$\r$\n• Vocabulary lists$\r$\n• Session logs$\r$\n$\r$\nSelect 'No' to keep your data for future installations." IDNO +3
  RMDir /r "$APPDATA\${APP_NAME}"
  RMDir /r "$LOCALAPPDATA\${APP_NAME}"
  
SectionEnd

;--------------------------------
; Uninstaller Functions

Function un.onInit
  ; Confirmation dialog
  MessageBox MB_YESNO|MB_ICONQUESTION "Are you sure you want to uninstall ${APP_NAME}?" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  MessageBox MB_OK|MB_ICONINFORMATION "${APP_NAME} has been successfully removed from your computer."
FunctionEnd

;--------------------------------
; Custom Strings for different languages

; English strings
LangString DESC_SecMain ${LANG_ENGLISH} "Core application files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Start Menu shortcuts"

; Spanish strings
LangString DESC_SecMain ${LANG_SPANISH} "Archivos principales de la aplicación (requerido)"
LangString DESC_SecDesktop ${LANG_SPANISH} "Acceso directo en el escritorio"
LangString DESC_SecStartMenu ${LANG_SPANISH} "Accesos directos en el Menú Inicio"
