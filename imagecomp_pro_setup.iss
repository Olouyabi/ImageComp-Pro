; Script Inno Setup pour ImageComp Pro

[Setup]
AppName=ImageComp Pro
AppVersion=2.1.0
DefaultDirName={userpf}\ImageCompPro
DefaultGroupName=ImageComp Pro
UninstallDisplayIcon={app}\main.exe
OutputDir=dist
OutputBaseFilename=ImageCompProSetup
Compression=lzma
SolidCompression=yes
SetupIconFile=resources\icons\app_icon.ico

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ImageComp Pro"; Filename: "{app}\main.exe"; IconFilename: "{app}\resources\icons\app_icon.ico"
Name: "{userdesktop}\ImageComp Pro"; Filename: "{app}\main.exe"; IconFilename: "{app}\resources\icons\app_icon.ico"

[Run]
Filename: "{app}\main.exe"; Description: "Lancer ImageComp Pro"; Flags: nowait postinstall skipifsilent