; Enhanced Inno Setup Script for Unsplash Image Search GPT Description
; Requires Inno Setup 6.2 or later with IDP (Internet Download Plugin)
; Download from: https://jrsoftware.org/isinfo.php
; IDP Plugin: https://github.com/DomGries/InnoDependencyInstaller

#define MyAppName "Unsplash Image Search GPT Description"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Image Search Tools"
#define MyAppURL "https://github.com/your-username/unsplash-image-search-gpt-description"
#define MyAppExeName "unsplash-image-search.exe"
#define MyAppDescription "AI-powered image search and description tool with Spanish language learning features"
#define MyAppVersionInfoVersion "1.0.0.0"
#define MyAppId "{{B8F4A2C1-9D3E-4F7A-8B2C-1E5A6D9F3C8B}"

; Include dependencies installer
#include "dependencies\CodeDependencies.iss"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
AppReadmeFile={app}\README.md
AppContact=support@image-search-tools.com
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
InfoBeforeFile=installer\assets\info_before.txt
InfoAfterFile=installer\assets\info_after.txt
OutputDir=.\output
OutputBaseFilename=unsplash-image-search-setup-{#MyAppVersion}
SetupIconFile=.\assets\app_icon.ico
Compression=lzma2/max
SolidCompression=yes
InternalCompressLevel=max
WizardStyle=modern
WizardImageFile=.\assets\wizard_left.bmp
WizardSmallImageFile=.\assets\wizard_small.bmp
WizardImageStretch=no
WizardImageBackColor=clWhite
DisableWelcomePage=no
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersionInfoVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoTextVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductTextVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}
VersionInfoOriginalFileName=unsplash-image-search-setup-{#MyAppVersion}.exe
VersionInfoInternalName=unsplash-image-search-setup
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x86 x64
MinVersion=6.1sp1
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=yes
RestartApplications=yes
CreateUninstallRegKey=yes
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousSetupType=yes
UsePreviousTasks=yes
UsePreviousUserInfo=yes
UsePreviousLanguage=yes
UserInfoPage=yes
DirExistsWarning=auto
EnableDirDoesntExistWarning=yes
UpdateUninstallLogAppName=yes
ShowLanguageDialog=auto
LanguageDetectionMethod=uilanguage
SetupLogging=yes
SignTool=signtool
SignedUninstaller=yes

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "..\LICENSE"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"; LicenseFile: "installer\assets\LICENSE_es.txt"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"; LicenseFile: "installer\assets\LICENSE_fr.txt"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"; LicenseFile: "installer\assets\LICENSE_de.txt"

[Types]
Name: "full"; Description: "Full installation (recommended)"
Name: "minimal"; Description: "Minimal installation"
Name: "portable"; Description: "Portable installation (no registry entries)"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "core"; Description: "Core application files"; Types: full minimal portable custom; Flags: fixed
Name: "docs"; Description: "Documentation and help files"; Types: full custom
Name: "examples"; Description: "Sample data and examples"; Types: full custom
Name: "devtools"; Description: "Development tools and debugging support"; Types: custom
Name: "languages"; Description: "Additional language support"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Components: not portable
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; OnlyBelowVersion: 6.1; Components: not portable
Name: "associate"; Description: "Associate .uigd files (session files) with {#MyAppName}"; GroupDescription: "File associations"; Components: not portable
Name: "startmenu"; Description: "Create start menu entries"; GroupDescription: "{cm:AdditionalIcons}"; Components: not portable; Flags: unchecked
Name: "startup"; Description: "Start {#MyAppName} automatically when Windows starts"; GroupDescription: "System integration"; Components: not portable; Flags: unchecked
Name: "firewall"; Description: "Add Windows Firewall exception for API access"; GroupDescription: "System integration"; Components: not portable
Name: "updater"; Description: "Enable automatic update checking"; GroupDescription: "Updates"; Flags: unchecked

[Files]
; Main application files - Core component
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion signonce; Components: core
Source: "..\dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "..\dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\dist\*.pyd"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Configuration and runtime files
Source: "..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: ".\assets\config.ini.template"; DestDir: "{app}"; DestName: "config.ini.template"; Flags: ignoreversion; Components: core
Source: ".\scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion; Components: core

; Documentation files
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: docs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion; Components: docs
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: docs
Source: ".\assets\*.pdf"; DestDir: "{app}\docs"; Flags: ignoreversion; Components: docs

; Examples and sample data
Source: "..\examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: examples
Source: ".\assets\samples\*"; DestDir: "{app}\examples"; Flags: ignoreversion; Components: examples

; Language support files
Source: "..\locales\*"; DestDir: "{app}\locales"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: languages

; Development and debugging tools
Source: "..\debug\*"; DestDir: "{app}\debug"; Flags: ignoreversion; Components: devtools
Source: ".\tools\*"; DestDir: "{app}\tools"; Flags: ignoreversion; Components: devtools

; Prerequisites and redistributables
Source: ".\redist\vcredist_x86.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: not IsWin64
Source: ".\redist\vcredist_x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: IsWin64
Source: ".\redist\dotnetfx48.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

; Silent installation configuration templates
Source: ".\config\silent_install.xml"; DestDir: "{app}\config"; Flags: ignoreversion
Source: ".\config\enterprise_config.json"; DestDir: "{app}\config"; Flags: ignoreversion

; Uninstaller resources
Source: ".\assets\uninstall_banner.bmp"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; File associations for .uigd files
Root: HKCR; Subkey: ".uigd"; ValueType: string; ValueName: ""; ValueData: "UnsplashImageSearchSession"; Flags: uninsdeletevalue; Tasks: associate; Components: not portable
Root: HKCR; Subkey: "UnsplashImageSearchSession"; ValueType: string; ValueName: ""; ValueData: "Unsplash Image Search Session File"; Flags: uninsdeletekey; Tasks: associate; Components: not portable
Root: HKCR; Subkey: "UnsplashImageSearchSession\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associate; Components: not portable
Root: HKCR; Subkey: "UnsplashImageSearchSession\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate; Components: not portable
Root: HKCR; Subkey: "UnsplashImageSearchSession\shell\edit\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --edit ""%1"""; Tasks: associate; Components: not portable

; Additional file associations for .uiconfig files
Root: HKCR; Subkey: ".uiconfig"; ValueType: string; ValueName: ""; ValueData: "UnsplashImageSearchConfig"; Flags: uninsdeletevalue; Tasks: associate; Components: not portable
Root: HKCR; Subkey: "UnsplashImageSearchConfig"; ValueType: string; ValueName: ""; ValueData: "Unsplash Image Search Configuration File"; Flags: uninsdeletekey; Tasks: associate; Components: not portable
Root: HKCR; Subkey: "UnsplashImageSearchConfig\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},1"; Tasks: associate; Components: not portable
Root: HKCR; Subkey: "UnsplashImageSearchConfig\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" --config ""%1"""; Tasks: associate; Components: not portable

; Application settings registry entries
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey; Components: not portable
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey; Components: not portable
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetInstallDate}"; Flags: uninsdeletekey; Components: not portable
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "FirstRun"; ValueData: "1"; Flags: uninsdeletekey; Components: not portable
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "DataDirectory"; ValueData: "{code:GetDataDirectory}"; Flags: uninsdeletekey; Components: not portable
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "AutoUpdate"; ValueData: "{code:GetAutoUpdateSetting}"; Flags: uninsdeletekey; Components: not portable; Tasks: updater
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Language"; ValueData: "{language}"; Flags: uninsdeletekey; Components: not portable

; Startup registry entry
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Tasks: startup; Components: not portable

; Windows Firewall exceptions
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile\AuthorizedApplications\List"; ValueType: string; ValueName: "{app}\{#MyAppExeName}"; ValueData: "{app}\{#MyAppExeName}:*:Enabled:Unsplash Image Search"; Flags: uninsdeletevalue; Tasks: firewall; Components: not portable
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\DomainProfile\AuthorizedApplications\List"; ValueType: string; ValueName: "{app}\{#MyAppExeName}"; ValueData: "{app}\{#MyAppExeName}:*:Enabled:Unsplash Image Search"; Flags: uninsdeletevalue; Tasks: firewall; Components: not portable

; Enterprise/Group Policy settings (HKLM for system-wide)
Root: HKLM; Subkey: "Software\Policies\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Policies\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "ConfigFile"; ValueData: "{app}\config\enterprise_config.json"; Flags: uninsdeletekey; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Policies\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "AllowUserConfiguration"; ValueData: "{code:GetAllowUserConfig}"; Flags: uninsdeletekey; Check: IsAdminInstallMode

; Add/Remove Programs entries with enhanced information
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetInstallDateFormatted}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1"; ValueType: string; ValueName: "Contact"; ValueData: "support@image-search-tools.com"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1"; ValueType: string; ValueName: "HelpLink"; ValueData: "{#MyAppURL}/wiki"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1"; ValueType: string; ValueName: "URLUpdateInfo"; ValueData: "{#MyAppURL}/releases"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1"; ValueType: dword; ValueName: "NoModify"; ValueData: "1"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1"; ValueType: dword; ValueName: "NoRepair"; ValueData: "1"; Flags: uninsdeletekey

[Icons]
; Main application shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0; Comment: "Launch {#MyAppName}"; Tasks: startmenu; Components: not portable
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0; Comment: "Launch {#MyAppName}"; Tasks: desktopicon; Components: not portable
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunchicon; Components: not portable

; Additional shortcuts in start menu group
Name: "{group}\{#MyAppName} Documentation"; Filename: "{app}\README.md"; WorkingDir: "{app}"; Comment: "View documentation and help"; Tasks: startmenu; Components: docs and not portable
Name: "{group}\{#MyAppName} Examples"; Filename: "{app}\examples"; WorkingDir: "{app}\examples"; Comment: "Browse example files and templates"; Tasks: startmenu; Components: examples and not portable
Name: "{group}\Configuration Wizard"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--setup-wizard"; WorkingDir: "{app}"; Comment: "Configure API keys and settings"; Tasks: startmenu; Components: not portable
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; WorkingDir: "{app}"; Comment: "Uninstall {#MyAppName}"; Tasks: startmenu; Components: not portable

; System tools shortcuts (for debugging)
Name: "{group}\Tools\Debug Mode"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--debug"; WorkingDir: "{app}"; Comment: "Launch in debug mode"; Tasks: startmenu; Components: devtools and not portable
Name: "{group}\Tools\Log Viewer"; Filename: "{app}\tools\log_viewer.exe"; WorkingDir: "{app}\tools"; Comment: "View application logs"; Tasks: startmenu; Components: devtools and not portable

[Run]
; Install prerequisites
Filename: "{tmp}\vcredist_x86.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installing Visual C++ Redistributable (x86)..."; Flags: waituntilterminated; Check: not IsWin64 and VCRedistNeedsInstall
Filename: "{tmp}\vcredist_x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installing Visual C++ Redistributable (x64)..."; Flags: waituntilterminated; Check: IsWin64 and VCRedistNeedsInstall
Filename: "{tmp}\dotnetfx48.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Installing .NET Framework 4.8..."; Flags: waituntilterminated; Check: DotNetFrameworkNeedsInstall

; Configure Windows Firewall
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall add rule name=""{#MyAppName}"" dir=in action=allow program=""{app}\{#MyAppExeName}"" enable=yes"; StatusMsg: "Configuring Windows Firewall..."; Flags: waituntilterminated runhidden; Tasks: firewall; Components: not portable

; Run post-install configuration
Filename: "{app}\{#MyAppExeName}"; Parameters: "--setup-wizard --first-run"; Description: "Launch {#MyAppName} Configuration Wizard"; Flags: nowait postinstall skipifsilent; Check: not WizardSilent
Filename: "{app}\{#MyAppExeName}"; Parameters: "--validate-installation"; Description: "Verify installation integrity"; Flags: waituntilterminated postinstall skipifsilent; Components: devtools

; Open documentation and examples
Filename: "{app}\README.md"; Description: "View Quick Start Guide and Documentation"; Flags: nowait postinstall skipifsilent shellexec unchecked; Components: docs; Check: not WizardSilent
Filename: "{app}\examples"; Description: "Browse Example Files and Templates"; Flags: nowait postinstall skipifsilent shellexec unchecked; Components: examples; Check: not WizardSilent

; Register for automatic updates
Filename: "{app}\{#MyAppExeName}"; Parameters: "--register-updater"; StatusMsg: "Registering for automatic updates..."; Flags: waituntilterminated runhidden; Tasks: updater

; Import previous settings if available
Filename: "{app}\scripts\migrate_settings.exe"; Parameters: "--auto"; StatusMsg: "Importing previous settings..."; Flags: waituntilterminated runhidden; Check: PreviousInstallationFound

[UninstallRun]
; Remove Windows Firewall rules
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall delete rule name=""{#MyAppName}"""; Flags: waituntilterminated runhidden; Tasks: firewall; Components: not portable

; Export user settings before uninstall (optional)
Filename: "{app}\{#MyAppExeName}"; Parameters: "--export-settings --output ""{userdocs}\{#MyAppName}_backup.json"""; RunOnceId: "ExportSettings"; Flags: waituntilterminated; Check: ShouldBackupSettings

; Clean up temporary files
Filename: "{app}\{#MyAppExeName}"; Parameters: "--cleanup-temp"; RunOnceId: "CleanupTempFiles"; Flags: waituntilterminated

; Unregister from automatic updates
Filename: "{app}\{#MyAppExeName}"; Parameters: "--unregister-updater"; RunOnceId: "UnregisterUpdater"; Flags: waituntilterminated runhidden; Tasks: updater

[Code]
var
  DataDirPage: TInputDirWizardPage;
  ConfigPage: TInputQueryWizardPage;
  InstallTypePage: TInputOptionWizardPage;
  LicensePage: TOutputMsgWizardPage;
  PrereqPage: TOutputProgressWizardPage;
  MigrationPage: TInputQueryWizardPage;
  
  // Global variables for installation state
  IsPortableInstall: Boolean;
  PreviousVersion: String;
  DataDirectory: String;
  SilentConfigFile: String;
  
procedure InitializeWizard;
begin
  // Initialize global variables
  IsPortableInstall := False;
  PreviousVersion := '';
  DataDirectory := '';
  SilentConfigFile := ExpandConstant('{param:config|}');
  
  // Check for silent installation with config file
  if (SilentConfigFile <> '') and FileExists(SilentConfigFile) then
  begin
    LoadSilentConfiguration;
  end;
  
  // Create custom wizard pages (only in interactive mode)
  if not WizardSilent then
  begin
    CreateWizardPages;
  end;
end;

procedure CreateWizardPages;
begin
  // Installation type selection page
  InstallTypePage := CreateInputOptionPage(wpWelcome,
    'Installation Type', 'Choose the type of installation',
    'Please select the installation type that best suits your needs.',
    True, False);
  InstallTypePage.Add('Full Installation (Recommended)');
  InstallTypePage.Add('Minimal Installation');
  InstallTypePage.Add('Portable Installation (No registry entries)');
  InstallTypePage.Add('Enterprise Installation (Silent/Managed)');
  InstallTypePage.Values[0] := True;
  
  // Previous installation migration page
  if PreviousInstallationFound then
  begin
    MigrationPage := CreateInputQueryPage(InstallTypePage.ID,
      'Previous Installation Found', 'Migrate settings and data',
      'A previous installation of {#MyAppName} was detected. You can choose to migrate your settings and data.');
    MigrationPage.Add('Migrate user settings and configuration', True);
    MigrationPage.Add('Import session files and vocabulary data', True);
    MigrationPage.Add('Preserve cached images and temporary files', False);
    MigrationPage.Values[0] := True;
    MigrationPage.Values[1] := True;
  end;
  
  // Data directory selection page
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Select Data Directory', 'Where should user data be stored?',
    'Select the folder where session files, vocabulary lists, and cached images will be stored. ' +
    'For portable installations, this will be a subfolder of the installation directory.',
    False, '');
  DataDirPage.Add('User data directory:');
  DataDirPage.Values[0] := ExpandConstant('{userdocs}\{#MyAppName}');
  
  // Enhanced configuration page with validation
  ConfigPage := CreateInputQueryPage(DataDirPage.ID,
    'API Configuration', 'Configure API keys and preferences',
    'Enter your API keys and configure default settings. All fields are optional and can be configured later.');
  ConfigPage.Add('Unsplash API Key (optional):', False);
  ConfigPage.Add('OpenAI API Key (optional):', True);
  ConfigPage.Add('Default search language:', False);
  ConfigPage.Add('Cache size (MB):', False);
  ConfigPage.Add('Enable automatic updates:', False);
  ConfigPage.Values[2] := 'English';
  ConfigPage.Values[3] := '500';
  ConfigPage.Values[4] := 'Yes';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Handle installation type selection
  if (InstallTypePage <> nil) and (CurPageID = InstallTypePage.ID) then
  begin
    IsPortableInstall := InstallTypePage.Values[2];
    
    if InstallTypePage.Values[2] then // Portable installation
    begin
      WizardForm.DirEdit.Text := ExpandConstant('{userappdata}\{#MyAppName}');
      DataDirPage.Values[0] := ExpandConstant('{userappdata}\{#MyAppName}\Data');
    end
    else if InstallTypePage.Values[3] then // Enterprise installation
    begin
      if not IsAdminInstallMode then
      begin
        MsgBox('Enterprise installation requires administrator privileges. Please restart the installer as administrator.', mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
  
  // Validate data directory
  if (DataDirPage <> nil) and (CurPageID = DataDirPage.ID) then
  begin
    DataDirectory := DataDirPage.Values[0];
    
    if not DirExists(DataDirectory) then
    begin
      if MsgBox('The directory does not exist. Create it now?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        if not ForceDirectories(DataDirectory) then
        begin
          MsgBox('Failed to create directory: ' + DataDirectory + #13#10 + 
                 'Please choose a different location or check permissions.', mbError, MB_OK);
          Result := False;
        end;
      end
      else
        Result := False;
    end
    else
    begin
      // Check if directory is writable
      if not IsDirectoryWritable(DataDirectory) then
      begin
        MsgBox('The selected directory is not writable. Please choose a different location.', mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
  
  // Validate configuration settings
  if (ConfigPage <> nil) and (CurPageID = ConfigPage.ID) then
  begin
    // Validate Unsplash API key
    if (ConfigPage.Values[0] <> '') then
    begin
      if Length(ConfigPage.Values[0]) < 20 then
      begin
        MsgBox('Unsplash API key appears to be too short (should be at least 20 characters). ' +
               'Please verify the key or leave blank to configure later.', mbError, MB_OK);
        Result := False;
      end;
    end;
    
    // Validate OpenAI API key
    if (ConfigPage.Values[1] <> '') then
    begin
      if (Pos('sk-', ConfigPage.Values[1]) <> 1) or (Length(ConfigPage.Values[1]) < 20) then
      begin
        MsgBox('OpenAI API key should start with "sk-" and be at least 20 characters long. ' +
               'Please verify the key or leave blank to configure later.', mbError, MB_OK);
        Result := False;
      end;
    end;
    
    // Validate cache size
    if (ConfigPage.Values[3] <> '') then
    begin
      if (StrToIntDef(ConfigPage.Values[3], -1) < 50) or (StrToIntDef(ConfigPage.Values[3], -1) > 10000) then
      begin
        MsgBox('Cache size must be between 50 and 10000 MB.', mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  case CurStep of
    ssInstall:
      begin
        // Perform pre-installation tasks
        PrepareInstallation;
      end;
    
    ssPostInstall:
      begin
        // Post-installation configuration
        CreateConfigurationFiles;
        CreateUserDirectories;
        HandlePreviousInstallation;
        SetupPortableMode;
      end;
  end;
end;

procedure PrepareInstallation;
begin
  // Log installation start
  Log('Starting installation of {#MyAppName} version {#MyAppVersion}');
  
  // Check available disk space
  if not CheckDiskSpace then
  begin
    MsgBox('Insufficient disk space for installation. Please free up some space and try again.', mbError, MB_OK);
    Abort;
  end;
  
  // Close any running instances
  if IsAppRunning('{#MyAppExeName}') then
  begin
    if MsgBox('{#MyAppName} is currently running. Close it now?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      CloseApplication('{#MyAppExeName}');
    end
    else
    begin
      Abort;
    end;
  end;
end;

procedure CreateConfigurationFiles;
var
  ConfigFile: string;
  ConfigContent: string;
begin
  // Create main configuration file
  ConfigFile := ExpandConstant('{app}\config.ini');
  
  ConfigContent := '[UNSPLASH]' + #13#10 +
                  'ACCESS_KEY=' + GetConfigValue('UnsplashKey') + #13#10 +
                  #13#10 +
                  '[OPENAI]' + #13#10 +
                  'API_KEY=' + GetConfigValue('OpenAIKey') + #13#10 +
                  #13#10 +
                  '[SETTINGS]' + #13#10 +
                  'DATA_DIR=' + GetConfigValue('DataDirectory') + #13#10 +
                  'DEFAULT_LANGUAGE=' + GetConfigValue('Language') + #13#10 +
                  'CACHE_SIZE=' + GetConfigValue('CacheSize') + #13#10 +
                  'AUTO_UPDATE=' + GetConfigValue('AutoUpdate') + #13#10 +
                  'FIRST_RUN=true' + #13#10 +
                  'AUTO_SAVE=true' + #13#10 +
                  'INSTALLATION_TYPE=' + GetInstallationType + #13#10 +
                  'INSTALLATION_DATE=' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + #13#10 +
                  'VERSION=' + '{#MyAppVersion}' + #13#10;
  
  SaveStringToFile(ConfigFile, ConfigContent, False);
  
  // Create backup of configuration
  FileCopy(ConfigFile, ConfigFile + '.backup', False);
end;

procedure CreateUserDirectories;
var
  BaseDir: string;
begin
  BaseDir := GetConfigValue('DataDirectory');
  
  // Create directory structure
  ForceDirectories(BaseDir);
  ForceDirectories(BaseDir + '\sessions');
  ForceDirectories(BaseDir + '\cache');
  ForceDirectories(BaseDir + '\exports');
  ForceDirectories(BaseDir + '\vocabulary');
  ForceDirectories(BaseDir + '\logs');
  ForceDirectories(BaseDir + '\temp');
  ForceDirectories(BaseDir + '\backups');
  
  // Create initial files
  SaveStringToFile(BaseDir + '\README.txt', 
    'This directory contains user data for {#MyAppName}.' + #13#10 +
    'Please do not delete this folder unless you want to remove all your data.' + #13#10 +
    #13#10 +
    'Subdirectories:' + #13#10 +
    '- sessions: Saved search sessions' + #13#10 +
    '- cache: Temporary image cache' + #13#10 +
    '- exports: Exported data files' + #13#10 +
    '- vocabulary: Vocabulary lists' + #13#10 +
    '- logs: Application log files' + #13#10 +
    '- backups: Automatic backups' + #13#10, False);
end;

function InitializeUninstall(): Boolean;
var
  DataDir: string;
  BackupDir: string;
begin
  Result := True;
  
  // Read data directory from registry
  DataDir := GetDataDirectoryFromRegistry;
  if DataDir = '' then
    DataDir := ExpandConstant('{userdocs}\{#MyAppName}');
  
  // Check if user wants to keep data
  case MsgBox('What would you like to do with your user data and settings?' + #13#10 + #13#10 +
              'Yes = Remove all data (cannot be undone)' + #13#10 +
              'No = Keep data for future use' + #13#10 +
              'Cancel = Create backup before removal',
              mbConfirmation, MB_YESNOCANCEL or MB_DEFBUTTON2) of
    IDYES:
      begin
        // Remove all user data
        if DirExists(DataDir) then
        begin
          DelTree(DataDir, True, True, True);
          Log('User data directory removed: ' + DataDir);
        end;
        
        // Remove configuration
        DeleteFile(ExpandConstant('{app}\config.ini'));
        DeleteFile(ExpandConstant('{app}\config.ini.backup'));
      end;
    
    IDNO:
      begin
        // Keep user data, only remove application
        Log('User data preserved at: ' + DataDir);
      end;
    
    IDCANCEL:
      begin
        // Create backup before removal
        BackupDir := ExpandConstant('{userdocs}\{#MyAppName}_Backup_' + 
                     GetDateTimeString('yyyymmdd_hhnnss', '', ''));
        
        if DirExists(DataDir) then
        begin
          if CopyDirectory(DataDir, BackupDir) then
          begin
            MsgBox('Backup created at: ' + BackupDir, mbInformation, MB_OK);
            DelTree(DataDir, True, True, True);
          end
          else
          begin
            MsgBox('Failed to create backup. User data will be preserved.', mbError, MB_OK);
          end;
        end;
        
        // Remove configuration
        DeleteFile(ExpandConstant('{app}\config.ini'));
      end;
  end;
end;

// Additional utility functions
function GetInstallDate: string;
begin
  Result := GetDateTimeString('yyyy-mm-dd', '-', ':');
end;

function GetInstallDateFormatted: string;
begin
  Result := GetDateTimeString('yyyymmdd', '', '');
end;

function GetDataDirectory: string;
begin
  if DataDirectory <> '' then
    Result := DataDirectory
  else if DataDirPage <> nil then
    Result := DataDirPage.Values[0]
  else
    Result := ExpandConstant('{userdocs}\{#MyAppName}');
end;

function GetAutoUpdateSetting: Cardinal;
begin
  if (ConfigPage <> nil) and (ConfigPage.Values[4] = 'Yes') then
    Result := 1
  else
    Result := 0;
end;

function GetAllowUserConfig: Cardinal;
begin
  // For enterprise installations, read from silent config
  if IsAdminInstallMode then
    Result := 0
  else
    Result := 1;
end;

function GetConfigValue(Key: string): string;
begin
  case Key of
    'UnsplashKey':
      if ConfigPage <> nil then Result := ConfigPage.Values[0] else Result := '';
    'OpenAIKey':
      if ConfigPage <> nil then Result := ConfigPage.Values[1] else Result := '';
    'Language':
      if ConfigPage <> nil then Result := ConfigPage.Values[2] else Result := 'English';
    'CacheSize':
      if ConfigPage <> nil then Result := ConfigPage.Values[3] else Result := '500';
    'AutoUpdate':
      if ConfigPage <> nil then Result := ConfigPage.Values[4] else Result := 'Yes';
    'DataDirectory':
      Result := GetDataDirectory;
  else
    Result := '';
  end;
end;

function GetInstallationType: string;
begin
  if IsPortableInstall then
    Result := 'Portable'
  else if IsAdminInstallMode then
    Result := 'Enterprise'
  else
    Result := 'Standard';
end;

function PreviousInstallationFound: Boolean;
var
  UninstallKey: string;
begin
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1';
  Result := RegKeyExists(HKLM, UninstallKey) or RegKeyExists(HKCU, UninstallKey);
  
  if Result then
  begin
    // Get previous version
    if not RegQueryStringValue(HKLM, UninstallKey, 'DisplayVersion', PreviousVersion) then
      RegQueryStringValue(HKCU, UninstallKey, 'DisplayVersion', PreviousVersion);
  end;
end;

function VCRedistNeedsInstall: Boolean;
begin
  // Check if Visual C++ Redistributable is installed
  Result := not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\' + 
    GetArchitectureString);
end;

function DotNetFrameworkNeedsInstall: Boolean;
var
  Version: Cardinal;
begin
  // Check for .NET Framework 4.8 or later
  Result := not RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full', 
    'Release', Version) or (Version < 528040);
end;

function GetArchitectureString: string;
begin
  if IsWin64 then
    Result := 'x64'
  else
    Result := 'x86';
end;

function IsDirectoryWritable(Dir: string): Boolean;
var
  TestFile: string;
begin
  TestFile := Dir + '\~test_write.tmp';
  Result := SaveStringToFile(TestFile, 'test', False);
  if Result then
    DeleteFile(TestFile);
end;

function CheckDiskSpace: Boolean;
var
  RequiredSpace: Int64;
  AvailableSpace: Int64;
begin
  RequiredSpace := 100 * 1024 * 1024; // 100 MB minimum
  GetSpaceOnDisk(ExtractFileDrive(ExpandConstant('{app}')), False, AvailableSpace, RequiredSpace);
  Result := AvailableSpace >= RequiredSpace;
end;

function IsAppRunning(AppName: string): Boolean;
var
  WindowHandle: HWND;
begin
  WindowHandle := FindWindowByWindowName(AppName);
  Result := WindowHandle <> 0;
end;

procedure CloseApplication(AppName: string);
var
  WindowHandle: HWND;
  ProcessId: DWORD;
begin
  WindowHandle := FindWindowByWindowName(AppName);
  if WindowHandle <> 0 then
  begin
    GetWindowThreadProcessId(WindowHandle, ProcessId);
    PostMessage(WindowHandle, WM_CLOSE, 0, 0);
    // Wait a bit for graceful shutdown
    Sleep(2000);
    // Force terminate if still running
    if IsAppRunning(AppName) then
    begin
      KillProcess(ProcessId);
    end;
  end;
end;

function GetDataDirectoryFromRegistry: string;
begin
  if not RegQueryStringValue(HKCU, 'Software\{#MyAppPublisher}\{#MyAppName}', 
                            'DataDirectory', Result) then
    Result := '';
end;

function CopyDirectory(SourceDir, DestDir: string): Boolean;
begin
  Result := Exec(ExpandConstant('{cmd}'), 
    '/C xcopy "' + SourceDir + '" "' + DestDir + '" /E /I /H /Y', 
    '', SW_HIDE, ewWaitUntilTerminated, 0);
end;

function ShouldBackupSettings: Boolean;
begin
  Result := MsgBox('Would you like to backup your settings and data before uninstalling?' + #13#10 +
                   'This will create a backup file that you can restore later.',
                   mbConfirmation, MB_YESNO) = IDYES;
end;

procedure LoadSilentConfiguration;
var
  ConfigLines: TArrayOfString;
  I: Integer;
  Line, Key, Value: string;
  SeparatorPos: Integer;
begin
  if LoadStringsFromFile(SilentConfigFile, ConfigLines) then
  begin
    for I := 0 to GetArrayLength(ConfigLines) - 1 do
    begin
      Line := Trim(ConfigLines[I]);
      if (Line <> '') and (Pos('#', Line) <> 1) then
      begin
        SeparatorPos := Pos('=', Line);
        if SeparatorPos > 0 then
        begin
          Key := Trim(Copy(Line, 1, SeparatorPos - 1));
          Value := Trim(Copy(Line, SeparatorPos + 1, Length(Line)));
          
          // Apply configuration values
          case Key of
            'INSTALL_DIR':
              WizardForm.DirEdit.Text := Value;
            'DATA_DIR':
              DataDirectory := Value;
            'UNSPLASH_KEY':
              if ConfigPage <> nil then ConfigPage.Values[0] := Value;
            'OPENAI_KEY':
              if ConfigPage <> nil then ConfigPage.Values[1] := Value;
          end;
        end;
      end;
    end;
  end;
end;

procedure HandlePreviousInstallation;
var
  OldDataDir: string;
  NewDataDir: string;
begin
  if PreviousInstallationFound and (MigrationPage <> nil) then
  begin
    if MigrationPage.Values[0] then // Migrate settings
    begin
      // Migration logic here
      Log('Migrating settings from previous installation');
    end;
    
    if MigrationPage.Values[1] then // Import data
    begin
      // Data import logic here
      Log('Importing data from previous installation');
    end;
  end;
end;

procedure SetupPortableMode;
begin
  if IsPortableInstall then
  begin
    // Create portable.ini file to indicate portable mode
    SaveStringToFile(ExpandConstant('{app}\portable.ini'), 
      '[Portable]' + #13#10 +
      'Enabled=true' + #13#10 +
      'DataPath=.\Data' + #13#10, False);
      
    // Adjust data directory for portable installation
    DataDirectory := ExpandConstant('{app}\Data');
  end;
end;