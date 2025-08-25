; Inno Setup Script for Unsplash Image Search & GPT Description Tool
; This script creates a professional Windows installer with modern features
; Generated for version 2.0.0

#define MyAppName "Unsplash Image Search GPT Tool"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Language Learning Tools"
#define MyAppURL "https://github.com/yourusername/unsplash-image-search-gpt"
#define MyAppExeName "Unsplash_Image_Search_GPT_Tool_v2.0.0.exe"
#define MyAppDescription "AI-powered image search and Spanish vocabulary learning tool"
#define MyAppCopyright "Copyright © 2024 Language Learning Tools. All rights reserved."

; Detect source directory automatically
#ifndef SourceDir
  #define SourceDir "..\dist"
#endif

[Setup]
; Application Information
AppId={{8A5B2C1D-9E4F-4A3B-B8C7-D6E9F0A1B2C3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright={#MyAppCopyright}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoCopyright={#MyAppCopyright}

; Default Installation Directory
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output Configuration
OutputDir=..\dist
OutputBaseFilename={#MyAppName}_Setup_v{#MyAppVersion}
SetupIconFile=app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273

; Windows Version Requirements
MinVersion=6.1sp1
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Visual Settings
WizardStyle=modern
WizardSizePercent=100,100
WizardResizable=yes
DisableDirPage=no
DisableProgramGroupPage=no
DisableReadyPage=no
ShowLanguageDialog=auto

; Security and Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
CreateUninstallRegKey=yes

; Digital Signature (uncomment and configure if you have a certificate)
;SignTool=signtool sign /f "certificate.pfx" /p "password" /t http://timestamp.digicert.com /fd SHA256 $f
;SignedUninstaller=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "startup"; Description: "Start {#MyAppName} when Windows starts"; GroupDescription: "Startup Options"; Flags: unchecked
Name: "associate"; Description: "Associate with .unsplash files"; GroupDescription: "File Associations"; Flags: unchecked

[Files]
; Main application executable
Source: "{#SourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Configuration and documentation files
Source: "{#SourceDir}\README.md"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#SourceDir}\LICENSE"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#SourceDir}\.env.example"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#SourceDir}\checksums.json"; DestDir: "{app}\docs"; Flags: ignoreversion skipifsourcedoesntexist

; Additional resources (if they exist)
Source: "{#SourceDir}\src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "{#SourceDir}\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "{#SourceDir}\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; Microsoft Visual C++ Redistributables (if needed)
; Source: "vcredist_x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Registry]
; Application registration
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "InstallDate"; ValueData: {code:GetDateTimeString}

; File associations (optional)
Root: HKCR; Subkey: ".unsplash"; ValueType: string; ValueName: ""; ValueData: "UnsplashProject"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "UnsplashProject"; ValueType: string; ValueName: ""; ValueData: "Unsplash Project File"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "UnsplashProject\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associate
Root: HKCR; Subkey: "UnsplashProject\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate

; Startup registry entry
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Tasks: startup

[Icons]
; Start menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"; Tasks: desktopicon

; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

; Documentation shortcuts
Name: "{group}\Documentation\User Manual"; Filename: "{app}\docs\README.md"; IconFilename: "{sys}\shell32.dll"; IconIndex: 70
Name: "{group}\Documentation\License"; Filename: "{app}\docs\LICENSE"; IconFilename: "{sys}\shell32.dll"; IconIndex: 70

[Run]
; Post-installation tasks
Filename: "{app}\{#MyAppExeName}"; Parameters: "--setup-wizard"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent unchecked
Filename: "{app}\docs\README.md"; Description: "View User Manual"; Flags: nowait postinstall skipifsilent shellexec unchecked

; Install Visual C++ Redistributables if needed
; Filename: "{tmp}\vcredist_x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installing Microsoft Visual C++ Redistributables..."; Check: VCRedistNeedsInstall

[UninstallRun]
; Cleanup tasks on uninstall
Filename: "{cmd}"; Parameters: "/C ""taskkill /f /im {#MyAppExeName} 2>nul"""; RunOnceId: "StopApp"; Flags: runhidden

[UninstallDelete]
; Remove configuration and cache files
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"
Type: filesandordirs; Name: "{localappdata}\{#MyAppName}"
Type: files; Name: "{userdesktop}\{#MyAppName}.lnk"

[Code]
// Custom functions for advanced installer features

// Get current date/time as string for registry
function GetDateTimeString(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd hh:nn:ss', #0, #0);
end;

// Check if Visual C++ Redistributables need to be installed
function VCRedistNeedsInstall: Boolean;
begin
  // Check if VC++ 2019-2022 x64 redistributables are installed
  Result := not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64');
end;

// Custom welcome page
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check Windows version
  if not IsWin64 then begin
    MsgBox('This application requires a 64-bit version of Windows.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Check if another instance is running
  if CheckForMutexes('UnsplashGPTToolMutex') then begin
    if MsgBox('The application appears to be running. Setup cannot continue while the application is running.' + #13#10#13#10 + 'Do you want to close the application and continue with setup?', mbConfirmation, MB_YESNO) = IDYES then begin
      // Try to close the application gracefully
      if Exec('taskkill', '/F /IM ' + '{#MyAppExeName}', '', SW_HIDE, ewWaitUntilTerminated, 0) then begin
        Sleep(2000); // Wait for the application to close
      end;
    end else begin
      Result := False;
      Exit;
    end;
  end;
end;

// Custom installation progress messages
procedure CurStepChanged(CurStep: TSetupStep);
begin
  case CurStep of
    ssInstall:
      WizardForm.StatusLabel.Caption := 'Installing {#MyAppName}...';
    ssPostInstall:
      WizardForm.StatusLabel.Caption := 'Configuring {#MyAppName}...';
  end;
end;

// Custom uninstall confirmation
function InitializeUninstall(): Boolean;
var
  Response: Integer;
begin
  Response := MsgBox('Are you sure you want to remove {#MyAppName} and all of its components?' + #13#10#13#10 + 
                     'Your configuration files and data will be preserved unless you choose to remove them on the next page.', 
                     mbConfirmation, MB_YESNO or MB_DEFBUTTON2);
  Result := Response = IDYES;
end;

// Custom finish page
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then begin
    WizardForm.FinishedLabel.Caption := 
      'Setup has finished installing {#MyAppName} on your computer.' + #13#10#13#10 +
      'Before using the application, please:' + #13#10 +
      '1. Configure your API keys (OpenAI and Unsplash)' + #13#10 +
      '2. Review the user manual' + #13#10 +
      '3. Set up your preferences' + #13#10#13#10 +
      'Click Finish to complete Setup.';
  end;
end;

// DPI Awareness
procedure InitializeWizard();
begin
  // Enable high DPI awareness
  WizardForm.Font.Name := 'Segoe UI';
  WizardForm.Font.Size := 9;
end;

[Messages]
; Custom messages for better user experience
WelcomeLabel2=This will install [name/ver] on your computer.%n%nThis application helps you search for images on Unsplash and learn Spanish vocabulary using AI-powered descriptions.%n%nIt is recommended that you close all other applications before continuing.
ClickNext=Click Next to continue, or Cancel to exit Setup.
BeveledLabel={#MyAppName} Setup
FinishedHeadingLabel=Completing the {#MyAppName} Setup Wizard
