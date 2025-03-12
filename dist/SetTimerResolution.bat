@echo off
echo Configurando resolucao de timer para jogos...
bcdedit /set useplatformclock true
bcdedit /set disabledynamictick yes
echo Timer do sistema otimizado para jogos
pause