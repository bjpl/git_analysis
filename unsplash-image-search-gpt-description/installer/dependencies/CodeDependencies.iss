; CodeDependencies.iss - Dependency installer for Inno Setup
; This file handles automatic downloading and installation of prerequisites
; Requires IDP (Inno Download Plugin) to be installed

[Code]
// Dependency installation functions

function Framework48IsNotInstalled(): Boolean;
var
  bSuccess: Boolean;
  regVersion: Cardinal;
begin
  // Check if .NET Framework 4.8 is installed
  bSuccess := RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\', 'Release', regVersion);
  Result := not bSuccess or (regVersion < 528040);
end;

function VCRedist2019IsNotInstalled(): Boolean;
var
  regKey: string;
begin
  // Check for Visual C++ Redistributable 2019
  if IsWin64 then
    regKey := 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64'
  else
    regKey := 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86';
    
  Result := not RegKeyExists(HKLM, regKey);
end;

function DirectXIsNotInstalled(): Boolean;
var
  regVersion: string;
begin
  // Check for DirectX
  Result := not RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\DirectX', 'Version', regVersion) or 
            (CompareVersion(regVersion, '4.09.00.0904') < 0);
end;

function GetDotNetFrameworkUrl(): string;
begin
  Result := 'https://download.microsoft.com/download/d/d/3/dd35cc25-6e9c-484c-9d4c-11b2e20e6dda/dotnetfx48.exe';
end;

function GetVCRedistUrl(): string;
begin
  if IsWin64 then
    Result := 'https://aka.ms/vs/16/release/vc_redist.x64.exe'
  else
    Result := 'https://aka.ms/vs/16/release/vc_redist.x86.exe';
end;

function GetDirectXUrl(): string;
begin
  Result := 'https://download.microsoft.com/download/1/7/1/1718CCC4-6315-4D8E-9543-8E28A4E18C4C/dxwebsetup.exe';
end;

// Initialize dependency checks and downloads
procedure InitializeWizard;
begin
  // Check and download dependencies
  if Framework48IsNotInstalled() then
  begin
    Log('Adding .NET Framework 4.8 to download queue');
    AddDependency('dotnetfx48.exe',
      '/quiet /norestart',
      '.NET Framework 4.8',
      GetDotNetFrameworkUrl(),
      '', False, False);
  end;

  if VCRedist2019IsNotInstalled() then
  begin
    Log('Adding Visual C++ Redistributable to download queue');
    AddDependency('vcredist_' + GetArchitectureString + '.exe',
      '/quiet /norestart',
      'Microsoft Visual C++ Redistributable',
      GetVCRedistUrl(),
      '', False, False);
  end;

  if DirectXIsNotInstalled() then
  begin
    Log('Adding DirectX to download queue');
    AddDependency('dxwebsetup.exe',
      '/Q',
      'Microsoft DirectX',
      GetDirectXUrl(),
      '', False, False);
  end;
end;

// Dependency management functions (requires IDP plugin)
procedure AddDependency(FileName, Parameters, Title, URL, Checksum: string; ForceInstall, Restart: Boolean);
begin
  if not FileExists(ExpandConstant('{tmp}\') + FileName) then
  begin
    Log('Downloading dependency: ' + Title);
    idpAddFile(URL, ExpandConstant('{tmp}\') + FileName);
  end;
  
  // Add to installation queue
  RegWriteStringValue(HKCU, 'SOFTWARE\UnsplashImageSearch\Dependencies', 
                      FileName, Parameters + '|' + Title + '|' + BoolToStr(Restart));
end;

function BoolToStr(Value: Boolean): string;
begin
  if Value then
    Result := 'True'
  else
    Result := 'False';
end;

// Install queued dependencies
procedure InstallDependencies();
var
  DependencyKey: string;
  Names: TArrayOfString;
  I: Integer;
  Values, Parts: TArrayOfString;
  FileName, Parameters, Title: string;
  RequiresRestart: Boolean;
  ResultCode: Integer;
begin
  DependencyKey := 'SOFTWARE\UnsplashImageSearch\Dependencies';
  
  if RegGetValueNames(HKCU, DependencyKey, Names) then
  begin
    for I := 0 to GetArrayLength(Names) - 1 do
    begin
      if RegQueryStringValue(HKCU, DependencyKey, Names[I], Values[0]) then
      begin
        // Parse dependency info
        Parts := StrSplit(Values[0], '|');
        if GetArrayLength(Parts) >= 3 then
        begin
          FileName := Names[I];
          Parameters := Parts[0];
          Title := Parts[1];
          RequiresRestart := Parts[2] = 'True';
          
          // Install dependency
          Log('Installing dependency: ' + Title);
          StatusLabel.Caption := 'Installing ' + Title + '...';
          
          if Exec(ExpandConstant('{tmp}\') + FileName, Parameters, '', SW_HIDE, 
                  ewWaitUntilTerminated, ResultCode) then
          begin
            Log('Successfully installed: ' + Title);
            if RequiresRestart then
            begin
              Log('Restart required after installing: ' + Title);
            end;
          end
          else
          begin
            Log('Failed to install: ' + Title + ' (Error: ' + IntToStr(ResultCode) + ')');
            MsgBox('Failed to install required component: ' + Title + #13#10 +
                   'The application may not function correctly.', mbError, MB_OK);
          end;
        end;
      end;
    end;
  end;
  
  // Clean up registry
  RegDeleteKeyIncludingSubkeys(HKCU, DependencyKey);
end;

// Custom step to install dependencies
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    InstallDependencies();
  end;
end;

// Utility functions for dependency checking
function CompareVersion(V1, V2: string): Integer;
var
  P, N1, N2: Integer;
begin
  Result := 0;
  while (Result = 0) and ((V1 <> '') or (V2 <> '')) do
  begin
    P := Pos('.', V1);
    if P > 0 then
    begin
      N1 := StrToInt(Copy(V1, 1, P - 1));
      Delete(V1, 1, P);
    end
    else if V1 <> '' then
    begin
      N1 := StrToInt(V1);
      V1 := '';
    end
    else
      N1 := 0;
      
    P := Pos('.', V2);
    if P > 0 then
    begin
      N2 := StrToInt(Copy(V2, 1, P - 1));
      Delete(V2, 1, P);
    end
    else if V2 <> '' then
    begin
      N2 := StrToInt(V2);
      V2 := '';
    end
    else
      N2 := 0;
      
    if N1 < N2 then
      Result := -1
    else if N1 > N2 then
      Result := 1;
  end;
end;

function GetArchitectureString(): string;
begin
  if IsWin64 then
    Result := 'x64'
  else
    Result := 'x86';
end;

// Check if a specific Windows version is installed
function IsWindowsVersionAtLeast(Major, Minor: Integer): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  Result := (Version.Major > Major) or 
            ((Version.Major = Major) and (Version.Minor >= Minor));
end;

// Check system requirements
function CheckSystemRequirements(): Boolean;
var
  MemoryMB: Cardinal;
  DiskSpaceGB: Extended;
begin
  Result := True;
  
  // Check Windows version (minimum Windows 7 SP1)
  if not IsWindowsVersionAtLeast(6, 1) then
  begin
    MsgBox('This application requires Windows 7 SP1 or later.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Check available memory (minimum 2GB recommended)
  MemoryMB := GetTotalMemory() div (1024 * 1024);
  if MemoryMB < 1024 then
  begin
    if MsgBox('Warning: This system has less than 1GB of RAM. ' +
              'The application may run slowly. Continue anyway?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
  
  // Check disk space (minimum 500MB)
  DiskSpaceGB := GetSpaceOnDisk(ExtractFileDrive(ExpandConstant('{app}')), False) / (1024 * 1024 * 1024);
  if DiskSpaceGB < 0.5 then
  begin
    MsgBox('Insufficient disk space. At least 500MB of free space is required.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  Log('System requirements check passed');
  Log('RAM: ' + IntToStr(MemoryMB) + 'MB');
  Log('Free disk space: ' + FloatToStr(DiskSpaceGB) + 'GB');
end;

function GetTotalMemory(): Cardinal;
var
  MS: TMemoryStatus;
begin
  MS.dwLength := SizeOf(TMemoryStatus);
  GlobalMemoryStatus(MS);
  Result := MS.dwTotalPhys;
end;

// Initialize setup with system checks
function InitializeSetup(): Boolean;
begin
  Result := CheckSystemRequirements();
  
  if Result then
  begin
    Log('System requirements satisfied, proceeding with installation');
  end
  else
  begin
    Log('System requirements not met, aborting installation');
  end;
end;