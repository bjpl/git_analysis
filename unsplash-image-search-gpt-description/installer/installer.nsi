; NSIS Script for Unsplash Image Search GPT Description
; Requires NSIS 3.0 or later with Modern UI 2
; Download from: https://nsis.sourceforge.io/

!define PRODUCT_NAME "Unsplash Image Search GPT Description"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "Image Search Tools"
!define PRODUCT_WEB_SITE "https://github.com/your-username/unsplash-image-search-gpt-description"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\unsplash-image-search.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_STARTMENU_REGVAL "NSIS:StartMenuDir"

; Include Modern UI
!include "MUI2.nsh"
!include "Sections.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "assets\app_icon.ico"
!define MUI_UNICON "assets\app_icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\wizard_image.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "assets\wizard_image.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\header_image.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Start menu page
Var StartMenuFolder
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "${PRODUCT_NAME}"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${PRODUCT_STARTMENU_REGVAL}"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

; Custom configuration page
Page custom ConfigPageCreate ConfigPageLeave

; Installation page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\unsplash-image-search.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS "--setup-wizard"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.md"
!define MUI_FINISHPAGE_LINK "Visit our website for support"
!define MUI_FINISHPAGE_LINK_LOCATION "${PRODUCT_WEB_SITE}"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Spanish"

; Reserve files for faster startup
!insertmacro MUI_RESERVEFILE_LANGDLL

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "output\unsplash-image-search-nsis-setup.exe"
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Version Information
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "Comments" "AI-powered image search and description tool"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© 2024 ${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "InternalName" "unsplash-image-search-setup.exe"
VIAddVersionKey /LANG=${LANG_ENGLISH} "OriginalFilename" "unsplash-image-search-setup.exe"

; Variables for custom configuration
Var Dialog
Var UnsplashKeyLabel
Var UnsplashKeyText
Var OpenAIKeyLabel  
Var OpenAIKeyText
Var LanguageLabel
Var LanguageDropdown
Var DataDirLabel
Var DataDirText
Var DataDirBrowse

; Custom configuration page functions
Function ConfigPageCreate
  !insertmacro MUI_HEADER_TEXT "Configuration" "Configure API keys and preferences"
  
  nsDialogs::Create 1018
  Pop $Dialog
  
  ${If} $Dialog == error
    Abort
  ${EndIf}
  
  ; Unsplash API Key
  ${NSD_CreateLabel} 10u 20u 280u 12u "Unsplash API Key (optional - can be configured later):"
  Pop $UnsplashKeyLabel
  
  ${NSD_CreateText} 10u 35u 280u 12u ""
  Pop $UnsplashKeyText
  
  ; OpenAI API Key
  ${NSD_CreateLabel} 10u 60u 280u 12u "OpenAI API Key (optional - can be configured later):"
  Pop $OpenAIKeyLabel
  
  ${NSD_CreatePassword} 10u 75u 280u 12u ""
  Pop $OpenAIKeyText
  
  ; Language selection
  ${NSD_CreateLabel} 10u 100u 280u 12u "Default search language:"
  Pop $LanguageLabel
  
  ${NSD_CreateDropList} 10u 115u 100u 60u ""
  Pop $LanguageDropdown
  ${NSD_CB_AddString} $LanguageDropdown "English"
  ${NSD_CB_AddString} $LanguageDropdown "Spanish"
  ${NSD_CB_AddString} $LanguageDropdown "French"
  ${NSD_CB_AddString} $LanguageDropdown "German"
  ${NSD_CB_SelectString} $LanguageDropdown "English"
  
  ; Data directory
  ${NSD_CreateLabel} 10u 140u 280u 12u "Data directory for sessions and cache:"
  Pop $DataDirLabel
  
  ${NSD_CreateText} 10u 155u 220u 12u "$DOCUMENTS\${PRODUCT_NAME}"
  Pop $DataDirText
  
  ${NSD_CreateButton} 235u 154u 50u 14u "Browse..."
  Pop $DataDirBrowse
  ${NSD_OnClick} $DataDirBrowse BrowseDataDir
  
  nsDialogs::Show
FunctionEnd

Function BrowseDataDir
  nsDialogs::SelectFolderDialog "Select Data Directory" "$DOCUMENTS\${PRODUCT_NAME}"
  Pop $0
  ${If} $0 != error
    ${NSD_SetText} $DataDirText $0
  ${EndIf}
FunctionEnd

Function ConfigPageLeave
  ; Get values for use during installation
  ${NSD_GetText} $UnsplashKeyText $0
  ${NSD_GetText} $OpenAIKeyText $1
  ${NSD_GetText} $LanguageDropdown $2
  ${NSD_GetText} $DataDirText $3
  
  ; Store in variables for later use
  StrCpy $R0 $0  ; Unsplash key
  StrCpy $R1 $1  ; OpenAI key
  StrCpy $R2 $2  ; Language
  StrCpy $R3 $3  ; Data directory
FunctionEnd

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
  
  ; Check if already installed
  ReadRegStr $0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  ${If} $0 != ""
    MessageBox MB_YESNOCANCEL|MB_ICONQUESTION \
      "${PRODUCT_NAME} is already installed.$\n$\nClick 'Yes' to upgrade the existing installation.$\nClick 'No' to cancel.$\nClick 'Cancel' to install anyway." \
      /SD IDYES IDYES upgrade IDNO quit IDCANCEL continue
    upgrade:
      ExecWait $0
      BringToFront
      Goto continue
    quit:
      Quit
    continue:
  ${EndIf}
  
  ; Initialize variables
  StrCpy $R0 ""  ; Unsplash key
  StrCpy $R1 ""  ; OpenAI key
  StrCpy $R2 "English"  ; Language
  StrCpy $R3 "$DOCUMENTS\${PRODUCT_NAME}"  ; Data directory
FunctionEnd

; Installation sections
Section "Core Application" SecCore
  SectionIn RO  ; Required section
  
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; Main application files
  File "..\dist\unsplash-image-search.exe"
  File /r "..\dist\*"
  
  ; Create directories
  CreateDirectory "$INSTDIR\data"
  CreateDirectory "$INSTDIR\docs"
  CreateDirectory "$INSTDIR\examples"
  
  ; Copy data and documentation
  File /oname=README.md "..\README.md"
  File /oname=LICENSE "..\LICENSE"
  SetOutPath "$INSTDIR\data"
  File /r "..\data\*"
  SetOutPath "$INSTDIR\docs"
  File /r "..\docs\*"
  SetOutPath "$INSTDIR\examples"
  File /r "..\examples\*"
  
  ; Create configuration file
  Call CreateConfigFile
  
  ; Create user data directories
  CreateDirectory "$R3"
  CreateDirectory "$R3\sessions"
  CreateDirectory "$R3\cache"
  CreateDirectory "$R3\exports"
  CreateDirectory "$R3\vocabulary"
SectionEnd

Section "Desktop Shortcut" SecDesktop
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\unsplash-image-search.exe"
SectionEnd

Section "Quick Launch Shortcut" SecQuickLaunch
  CreateShortCut "$QUICKLAUNCH\${PRODUCT_NAME}.lnk" "$INSTDIR\unsplash-image-search.exe"
SectionEnd

Section "File Associations" SecAssoc
  ; Associate .uigd files with the application
  WriteRegStr HKCR ".uigd" "" "UnsplashImageSearchSession"
  WriteRegStr HKCR "UnsplashImageSearchSession" "" "Unsplash Image Search Session File"
  WriteRegStr HKCR "UnsplashImageSearchSession\DefaultIcon" "" "$INSTDIR\unsplash-image-search.exe,0"
  WriteRegStr HKCR "UnsplashImageSearchSession\shell\open\command" "" '"$INSTDIR\unsplash-image-search.exe" "%1"'
  
  ; Refresh shell
  System::Call 'shell32.dll::SHChangeNotify(l, l, i, i) v (0x08000000, 0, 0, 0)'
SectionEnd

Section "Sample Data and Examples" SecSamples
  SetOutPath "$INSTDIR\examples"
  File "assets\sample_session.uigd"
  File "assets\quick_start_guide.pdf"
SectionEnd

Section -AdditionalIcons
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${PRODUCT_NAME}.lnk" "$INSTDIR\unsplash-image-search.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Documentation.lnk" "$INSTDIR\README.md"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\uninst.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\unsplash-image-search.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\unsplash-image-search.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  ; Estimate install size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create desktop shortcut"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecQuickLaunch} "Create quick launch shortcut"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecAssoc} "Associate .uigd session files with the application"
  !insertmacro MUI_DESCRIPTION_TEXT ${SecSamples} "Install sample data and quick start guide"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function CreateConfigFile
  FileOpen $4 "$INSTDIR\config.ini" w
  FileWrite $4 "[UNSPLASH]$\r$\n"
  FileWrite $4 "ACCESS_KEY=$R0$\r$\n"
  FileWrite $4 "$\r$\n"
  FileWrite $4 "[OPENAI]$\r$\n"
  FileWrite $4 "API_KEY=$R1$\r$\n"
  FileWrite $4 "$\r$\n"
  FileWrite $4 "[SETTINGS]$\r$\n"
  FileWrite $4 "DATA_DIR=$R3$\r$\n"
  FileWrite $4 "DEFAULT_LANGUAGE=$R2$\r$\n"
  FileWrite $4 "FIRST_RUN=true$\r$\n"
  FileWrite $4 "CACHE_SIZE=100$\r$\n"
  FileWrite $4 "AUTO_SAVE=true$\r$\n"
  FileClose $4
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  ; Remove file associations
  DeleteRegKey HKCR ".uigd"
  DeleteRegKey HKCR "UnsplashImageSearchSession"
  
  ; Remove application files
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\unsplash-image-search.exe"
  Delete "$INSTDIR\config.ini"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\LICENSE"
  RMDir /r "$INSTDIR\data"
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\examples"
  RMDir /r "$INSTDIR\_internal"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  !insertmacro MUI_STARTMENU_GETFOLDER "Application" $StartMenuFolder
  Delete "$SMPROGRAMS\$StartMenuFolder\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Documentation.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$QUICKLAUNCH\${PRODUCT_NAME}.lnk"
  
  ; Ask about user data removal
  MessageBox MB_YESNO|MB_ICONQUESTION \
    "Do you want to remove user data (sessions, cache, vocabulary files)?$\n$\nThis cannot be undone." \
    IDNO skip_user_data
  
  ; Remove user data
  ReadRegStr $0 HKCU "Software\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}" "DataDirectory"
  ${If} $0 != ""
    RMDir /r "$0"
  ${Else}
    RMDir /r "$DOCUMENTS\${PRODUCT_NAME}"
  ${EndIf}
  
  skip_user_data:
  
  ; Remove registry entries
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  DeleteRegKey HKCU "Software\${PRODUCT_PUBLISHER}\${PRODUCT_NAME}"
  
  ; Refresh shell
  System::Call 'shell32.dll::SHChangeNotify(l, l, i, i) v (0x08000000, 0, 0, 0)'
  
  SetAutoClose true
SectionEnd