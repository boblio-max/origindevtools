#define MyAppName "Origin CLI"
#define MyAppNameLower "origin"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "Origin Labs"
#define MyAppExeName "origin.exe"
#define MyAppURL "https://github.com/boblio-max/origindevtools"
#define MyAppDocsURL "https://docs-origin.onrender.com"

[Setup]
AppId={{8F3C5A2E-4B71-4C0A-9D2E-OriginCLI}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\OriginCLI
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
AllowNoIcons=yes
OutputDir=C:\Users\smile\Downloads
OutputBaseFilename=OriginCLI-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ChangesEnvironment=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} Documentation"; Filename: "{#MyAppDocsURL}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
const
  EnvKey = 'Environment';

function IsInPath(PathToCheck: string): Boolean;
var
  Path: string;
  Needle: string;
begin
  Result := False;
  if RegQueryStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', Path) then
  begin
    Needle := ';' + Uppercase(PathToCheck) + ';';
    Result := Pos(Needle, ';' + Uppercase(Path) + ';') > 0;
  end;
end;

procedure AddToPath(PathToAdd: string);
var
  Path: string;
begin
  if RegQueryStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', Path) then
  begin
    if Pos(';' + Uppercase(PathToAdd) + ';', ';' + Uppercase(Path) + ';') = 0 then
    begin
      if Length(Path) > 0 then
        Path := Path + ';' + PathToAdd
      else
        Path := PathToAdd;
      RegWriteExpandStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', Path);
    end;
  end
  else
    RegWriteExpandStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', PathToAdd);
end;

procedure RemoveFromPath(PathToRemove: string);
var
  Path: string;
  NewPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', Path) then
    Exit;
  NewPath := Path;
  if CompareText(NewPath, PathToRemove) = 0 then
    NewPath := ''
  else
  begin
    StringChangeEx(NewPath, ';' + PathToRemove, '', True);
    StringChangeEx(NewPath, PathToRemove + ';', '', True);
  end;
  RegWriteExpandStringValue(HKEY_CURRENT_USER, EnvKey, 'Path', NewPath);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    AddToPath(ExpandConstant('{app}'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RemoveFromPath(ExpandConstant('{app}'));
end;
