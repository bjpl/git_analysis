; Inno Setup Script for Unsplash Image Search GPT Description
; Requires Inno Setup 6.0 or later
; Download from: https://jrsoftware.org/isinfo.php

#define MyAppName "Unsplash Image Search GPT Description"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Image Search Tools"
#define MyAppURL "https://github.com/your-username/unsplash-image-search-gpt-description"
#define MyAppExeName "unsplash-image-search.exe"
#define MyAppDescription "AI-powered image search and description tool with Spanish language learning features"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
AppId={{B8F4A2C1-9D3E-4F7A-8B2C-1E5A6D9F3C8B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=.\output
OutputBaseFilename=unsplash-image-search-setup
SetupIconFile=.\assets\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardImageFile=.\assets\wizard_image.bmp
WizardSmallImageFile=.\assets\wizard_small.bmp
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "associate"; Description: "Associate .uigd files (session files) with {#MyAppName}"; GroupDescription: "File associations"

[Files]
; Main application files
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration and data files
Source: "..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

; Sample configuration file
Source: ".\assets\config.ini.sample"; DestDir: "{app}"; DestName: "config.ini.sample"; Flags: ignoreversion

; Post-install configuration script
Source: ".\scripts\post_install.py"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; File association for .uigd files
Root: HKCR; Subkey: ".uigd"; ValueType: string; ValueName: ""; ValueData: "UnsplashImageSearchSession"; Flags: uninsdeletevalue; Tasks: associate
Root: HKCR; Subkey: "UnsplashImageSearchSession"; ValueType: string; ValueName: ""; ValueData: "Unsplash Image Search Session File"; Flags: uninsdeletekey; Tasks: associate
Root: HKCR; Subkey: "UnsplashImageSearchSession\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associate
Root: HKCR; Subkey: "UnsplashImageSearchSession\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate

; Application settings registry entries
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "FirstRun"; ValueData: "1"; Flags: uninsdeletekey

; Add to Windows Firewall exceptions (for API access)
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile\AuthorizedApplications\List"; ValueType: string; ValueName: "{app}\{#MyAppExeName}"; ValueData: "{app}\{#MyAppExeName}:*:Enabled:Unsplash Image Search"; Flags: uninsdeletevalue

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Run post-install configuration
Filename: "{app}\{#MyAppExeName}"; Parameters: "--setup-wizard"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
; Open documentation
Filename: "{app}\README.md"; Description: "View README and Quick Start Guide"; Flags: nowait postinstall skipifsilent shellexec

[UninstallRun]
; Clean up user data (optional - ask user)
Filename: "{app}\{#MyAppExeName}"; Parameters: "--cleanup"; RunOnceId: "CleanupUserData"

[Code]
var
  DataDirPage: TInputDirWizardPage;
  ConfigPage: TInputQueryWizardPage;
  
procedure InitializeWizard;
begin
  { Create custom pages }
  
  // Data directory selection page
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Select Data Directory', 'Where should user data be stored?',
    'Select the folder where session files, vocabulary lists, and cached images will be stored, then click Next.',
    False, '');
  DataDirPage.Add('User data directory:');
  DataDirPage.Values[0] := ExpandConstant('{userdocs}\{#MyAppName}');
  
  // Basic configuration page
  ConfigPage := CreateInputQueryPage(wpSelectTasks,
    'Initial Configuration', 'Configure basic application settings',
    'You can change these settings later in the application.');
  ConfigPage.Add('Unsplash API Key (optional):', False);
  ConfigPage.Add('OpenAI API Key (optional):', True);
  ConfigPage.Add('Default search language:', False);
  ConfigPage.Values[2] := 'English';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = DataDirPage.ID then
  begin
    // Validate data directory
    if not DirExists(DataDirPage.Values[0]) then
    begin
      if MsgBox('The directory does not exist. Create it?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        if not CreateDir(DataDirPage.Values[0]) then
        begin
          MsgBox('Failed to create directory. Please choose a different location.', mbError, MB_OK);
          Result := False;
        end;
      end
      else
        Result := False;
    end;
  end;
  
  if CurPageID = ConfigPage.ID then
  begin
    // Validate API keys format (basic check)
    if (ConfigPage.Values[0] <> '') and (Length(ConfigPage.Values[0]) < 10) then
    begin
      MsgBox('Unsplash API key appears to be too short. Please check the key or leave blank to configure later.', mbError, MB_OK);
      Result := False;
    end;
    
    if (ConfigPage.Values[1] <> '') and (not Pos('sk-', ConfigPage.Values[1]) = 1) then
    begin
      MsgBox('OpenAI API key should start with "sk-". Please check the key or leave blank to configure later.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: string;
  ConfigData: TArrayOfString;
begin
  if CurStep = ssPostInstall then
  begin
    // Create initial configuration file
    ConfigFile := ExpandConstant('{app}\config.ini');
    SetArrayLength(ConfigData, 12);
    
    ConfigData[0] := '[UNSPLASH]';
    ConfigData[1] := 'ACCESS_KEY=' + ConfigPage.Values[0];
    ConfigData[2] := '';
    ConfigData[3] := '[OPENAI]';
    ConfigData[4] := 'API_KEY=' + ConfigPage.Values[1];
    ConfigData[5] := '';
    ConfigData[6] := '[SETTINGS]';
    ConfigData[7] := 'DATA_DIR=' + DataDirPage.Values[0];
    ConfigData[8] := 'DEFAULT_LANGUAGE=' + ConfigPage.Values[2];
    ConfigData[9] := 'FIRST_RUN=true';
    ConfigData[10] := 'CACHE_SIZE=100';
    ConfigData[11] := 'AUTO_SAVE=true';
    
    SaveStringToFile(ConfigFile, ConfigData[0] + #13#10 + 
                               ConfigData[1] + #13#10 + 
                               ConfigData[2] + #13#10 + 
                               ConfigData[3] + #13#10 + 
                               ConfigData[4] + #13#10 + 
                               ConfigData[5] + #13#10 + 
                               ConfigData[6] + #13#10 + 
                               ConfigData[7] + #13#10 + 
                               ConfigData[8] + #13#10 + 
                               ConfigData[9] + #13#10 + 
                               ConfigData[10] + #13#10 + 
                               ConfigData[11], False);
    
    // Create user data directory
    CreateDir(DataDirPage.Values[0]);
    CreateDir(DataDirPage.Values[0] + '\sessions');
    CreateDir(DataDirPage.Values[0] + '\cache');
    CreateDir(DataDirPage.Values[0] + '\exports');
    CreateDir(DataDirPage.Values[0] + '\vocabulary');
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('Do you want to remove user data and configuration files?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
  begin
    // Remove user data
    DelTree(ExpandConstant('{userdocs}\{#MyAppName}'), True, True, True);
    
    // Remove configuration
    DeleteFile(ExpandConstant('{app}\config.ini'));
  end;
end;