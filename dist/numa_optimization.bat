@echo off
echo Otimizando afinidade de CPU para jogos via nós NUMA
echo Para usar: numa_optimization.bat [PID do jogo]

if "%~1"=="" (
  echo Por favor, forneça o PID do jogo.
  echo Uso: numa_optimization.bat PID
  exit /b
)

powershell -Command "& {$process = Get-Process -Id %1; $process.ProcessorAffinity = [Int64]::MaxValue; Write-Host ('Afinidade de CPU otimizada para processo ' + $process.ProcessName)}"
pause