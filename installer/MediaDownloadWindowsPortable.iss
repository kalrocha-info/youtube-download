#define MyAppName "CASR Media Download"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "kalrocha-info"
#define MyAppExeName "CASR_Media_Download.exe"

[Setup]
AppId={{4B9F4246-33F4-4695-87F2-89A2B01DCA21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\CASR Media Download
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=no
UsePreviousAppDir=no
LicenseFile=..\LICENSE
OutputDir=..\release
OutputBaseFilename=CASRMediaDownloadSetup_v1.0.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\resources\casr_media_download.ico
CloseApplications=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
const
  UninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{4B9F4246-33F4-4695-87F2-89A2B01DCA21}_is1';

var
  ExistingAppDir: string;
  ExistingUninstaller: string;
  ReinstallInSameDir: Boolean;

function ReadExistingInstallation(): Boolean;
begin
  Result := RegQueryStringValue(HKLM, UninstallKey, 'Inno Setup: App Path', ExistingAppDir);
  if Result then
    RegQueryStringValue(HKLM, UninstallKey, 'UninstallString', ExistingUninstaller)
  else
  begin
    Result := RegQueryStringValue(HKCU, UninstallKey, 'Inno Setup: App Path', ExistingAppDir);
    if Result then
      RegQueryStringValue(HKCU, UninstallKey, 'UninstallString', ExistingUninstaller);
  end;
end;

function GetUninstallerPath(CommandLine: string): string;
var
  ClosingQuote: Integer;
  SpacePosition: Integer;
begin
  CommandLine := Trim(CommandLine);
  if (Length(CommandLine) > 0) and (CommandLine[1] = '"') then
  begin
    Delete(CommandLine, 1, 1);
    ClosingQuote := Pos('"', CommandLine);
    if ClosingQuote > 0 then
      Result := Copy(CommandLine, 1, ClosingQuote - 1)
    else
      Result := CommandLine;
  end
  else
  begin
    SpacePosition := Pos(' ', CommandLine);
    if SpacePosition > 0 then
      Result := Copy(CommandLine, 1, SpacePosition - 1)
    else
      Result := CommandLine;
  end;
end;

function InitializeSetup(): Boolean;
var
  Answer: Integer;
begin
  Result := True;
  if not ReadExistingInstallation() then
    Exit;

  ExistingUninstaller := GetUninstallerPath(ExistingUninstaller);
  if (ExistingUninstaller = '') or not FileExists(ExistingUninstaller) then
  begin
    MsgBox('Foi detectada uma instalacao anterior, mas nao foi possivel localizar o desinstalador. A instalacao foi cancelada.',
      mbError, MB_OK);
    Result := False;
    Exit;
  end;

  Answer := MsgBox(
    'Foi detectada uma instalacao em:' + #13#10 + ExistingAppDir + #13#10 + #13#10 +
    'Sim: remover e reinstalar na mesma pasta.' + #13#10 +
    'Nao: remover a instalacao atual e escolher outra pasta.' + #13#10 + #13#10 +
    'Deseja continuar?',
    mbConfirmation, MB_YESNOCANCEL);

  if Answer = IDYES then
    ReinstallInSameDir := True
  else if Answer = IDNO then
    ReinstallInSameDir := False
  else
    Result := False;
end;

procedure InitializeWizard();
begin
  if ExistingAppDir <> '' then
  begin
    if ReinstallInSameDir then
      WizardForm.DirEdit.Text := ExistingAppDir
    else
      WizardForm.DirEdit.Text := ExpandConstant('{autopf}\CASR Media Download - Nova instalacao');
  end;
end;

function NormalizePath(Path: string): string;
begin
  Result := Lowercase(ExpandFileName(Path));
  while (Length(Result) > 3) and (Result[Length(Result)] = '\') do
    Delete(Result, Length(Result), 1);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if (CurPageID = wpSelectDir) and (ExistingAppDir <> '') and
    not ReinstallInSameDir and
    (NormalizePath(WizardDirValue) = NormalizePath(ExistingAppDir)) then
  begin
    MsgBox('Escolha uma pasta diferente da instalacao atual.', mbError, MB_OK);
    Result := False;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): string;
var
  ExitCode: Integer;
begin
  Result := '';
  if ExistingAppDir = '' then
    Exit;

  if not Exec(ExistingUninstaller, '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART',
    '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
  begin
    Result := 'Nao foi possivel iniciar a remocao da instalacao anterior.';
    Exit;
  end;

  if ExitCode <> 0 then
    Result := 'A remocao da instalacao anterior falhou. A nova instalacao foi cancelada.';
end;
