@echo off
chcp 65001 > nul
echo ========================================
echo  블아 택틱 도우미 v2 - 패키지 설치
echo ========================================
echo.

:: Python 설치 여부 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.10 이상을 설치해주세요.
    pause
    exit /b 1
)

echo Python 버전:
python --version
echo.

echo 패키지를 설치합니다...
echo.

pip install --upgrade pip
pip install keyboard mouse Pillow pyinstaller

echo.
echo ========================================
echo  설치 완료!
echo  이제 build_exe.bat 으로 exe를 빌드하거나
echo  python 블아공략창_v2.py 로 바로 실행하세요.
echo ========================================
pause
