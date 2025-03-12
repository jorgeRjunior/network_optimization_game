@echo off
echo Iniciando monitoramento de processos de jogos...

:check_steam_exe
tasklist /FI "IMAGENAME eq steam.exe" 2>NUL | find /I /N "steam.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="steam.exe" CALL setpriority "high priority"
  echo Prioridade elevada para steam.exe
)

:check_epicgameslauncher_exe
tasklist /FI "IMAGENAME eq epicgameslauncher.exe" 2>NUL | find /I /N "epicgameslauncher.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="epicgameslauncher.exe" CALL setpriority "high priority"
  echo Prioridade elevada para epicgameslauncher.exe
)

:check_origin_exe
tasklist /FI "IMAGENAME eq origin.exe" 2>NUL | find /I /N "origin.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="origin.exe" CALL setpriority "high priority"
  echo Prioridade elevada para origin.exe
)

:check_battle_net_exe
tasklist /FI "IMAGENAME eq battle.net.exe" 2>NUL | find /I /N "battle.net.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="battle.net.exe" CALL setpriority "high priority"
  echo Prioridade elevada para battle.net.exe
)

:check_GalaxyClient_exe
tasklist /FI "IMAGENAME eq GalaxyClient.exe" 2>NUL | find /I /N "GalaxyClient.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="GalaxyClient.exe" CALL setpriority "high priority"
  echo Prioridade elevada para GalaxyClient.exe
)

:check_RiotClientServices_exe
tasklist /FI "IMAGENAME eq RiotClientServices.exe" 2>NUL | find /I /N "RiotClientServices.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="RiotClientServices.exe" CALL setpriority "high priority"
  echo Prioridade elevada para RiotClientServices.exe
)

:check_LeagueClient_exe
tasklist /FI "IMAGENAME eq LeagueClient.exe" 2>NUL | find /I /N "LeagueClient.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="LeagueClient.exe" CALL setpriority "high priority"
  echo Prioridade elevada para LeagueClient.exe
)

:check_valorant_exe
tasklist /FI "IMAGENAME eq valorant.exe" 2>NUL | find /I /N "valorant.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="valorant.exe" CALL setpriority "high priority"
  echo Prioridade elevada para valorant.exe
)

:check_csgo_exe
tasklist /FI "IMAGENAME eq csgo.exe" 2>NUL | find /I /N "csgo.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="csgo.exe" CALL setpriority "high priority"
  echo Prioridade elevada para csgo.exe
)

:check_dota2_exe
tasklist /FI "IMAGENAME eq dota2.exe" 2>NUL | find /I /N "dota2.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="dota2.exe" CALL setpriority "high priority"
  echo Prioridade elevada para dota2.exe
)

:check_gta5_exe
tasklist /FI "IMAGENAME eq gta5.exe" 2>NUL | find /I /N "gta5.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="gta5.exe" CALL setpriority "high priority"
  echo Prioridade elevada para gta5.exe
)

:check_FortniteClient-Win64-Shipping_exe
tasklist /FI "IMAGENAME eq FortniteClient-Win64-Shipping.exe" 2>NUL | find /I /N "FortniteClient-Win64-Shipping.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="FortniteClient-Win64-Shipping.exe" CALL setpriority "high priority"
  echo Prioridade elevada para FortniteClient-Win64-Shipping.exe
)

:check_r5apex_exe
tasklist /FI "IMAGENAME eq r5apex.exe" 2>NUL | find /I /N "r5apex.exe" >NUL
if "%ERRORLEVEL%"=="0" (
  wmic process where name="r5apex.exe" CALL setpriority "high priority"
  echo Prioridade elevada para r5apex.exe
)

timeout /t 30
goto check_steam_exe
