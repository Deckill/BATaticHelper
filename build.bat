@echo off
chcp 65001 > nul
echo ========================================
echo  블아 택틱 도우미 v2 - EXE 빌드
echo ========================================
echo.

:: PyInstaller 설치 여부 확인
pyinstaller --version > nul 2>&1
if errorlevel 1 (
    echo [오류] PyInstaller가 설치되어 있지 않습니다.
    echo install.bat 을 먼저 실행해주세요.
    pause
    exit /b 1
)

echo PyInstaller 버전:
pyinstaller --version
echo.

echo EXE 빌드를 시작합니다...
echo (처음 빌드 시 1~3분 정도 소요됩니다)
echo.

:: --windowed 제거 → 콘솔 창에서 [DBG] 로그 확인 가능
:: 디버그 확인 후 --windowed 다시 추가하면 콘솔 창 없어짐
pyinstaller ^
  --onefile ^
  --name "BA_Tactic_Helper" ^
  --icon NONE ^
  --hidden-import PIL ^
  --hidden-import PIL.Image ^
  --hidden-import PIL.ImageTk ^
  --hidden-import keyboard ^
  --hidden-import mouse ^
  main.py

if errorlevel 1 (
    echo.
    echo [오류] 빌드 실패. 위 오류 메시지를 확인해주세요.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  빌드 완료!
echo  dist\BA_Tactic_Helper.exe 파일을 사용하세요.
echo ========================================

:: dist 폴더의 exe를 현재 폴더로 복사
if exist "dist\BA_Tactic_Helper.exe" (
    copy /Y "dist\BA_Tactic_Helper.exe" "BA_Tactic_Helper.exe"
    echo  현재 폴더에 BA_Tactic_Helper.exe 복사 완료.
)

pause