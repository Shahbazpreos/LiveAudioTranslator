#define MyAppName "Live Audio Translator"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Shabbi"
#define MyAppExeName "LiveAudioTranslator.exe"

[Setup]
AppId={{B5F91BC2-8B6B-4C6D-91F2-7E6D9238B427}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\Live Audio Translator
DefaultGroupName=Live Audio Translator

DisableProgramGroupPage=yes

OutputDir=installer_output
OutputBaseFilename=LiveAudioTranslator-Setup

SetupIconFile=LiveAudioTranslator.ico

Compression=lzma2
SolidCompression=yes

WizardStyle=modern
PrivilegesRequired=admin

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\LiveAudioTranslator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Live Audio Translator"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Live Audio Translator"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Live Audio Translator"; Flags: nowait postinstall skipifsilent