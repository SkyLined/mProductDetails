@ECHO OFF
SETLOCAL

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Find Python
IF DEFINED PYTHON (
  CALL :CHECK_PYTHON
  IF ERRORLEVEL 1 (
    ENDLOCAL
    EXIT /B 1
  )
) ELSE (
  REM Try to detect the location of python automatically
  FOR /F "usebackq delims=" %%I IN (`where "python" 2^>nul`) DO SET PYTHON="%%~I"
  IF NOT DEFINED PYTHON (
    REM Check if python is found in its default installation path.
    SET PYTHON="%SystemDrive%\Python27\python.exe"
    CALL :CHECK_PYTHON
    IF ERRORLEVEL 1 (
      ENDLOCAL
      EXIT /B 1
    )
  )
)

CALL %PYTHON% "%~dpn0\%~n0.py" %*
IF ERRORLEVEL 2 GOTO :ERROR
IF ERRORLEVEL 1 (
  REM Version information updated
  ENDLOCAL
  EXIT /B 1
)

ENDLOCAL
EXIT /B 0

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Find Python helper
:CHECK_PYTHON
  REM Make sure path is quoted and check if it exists.
  SET PYTHON="%PYTHON:"=%"
  IF NOT EXIST %PYTHON% (
    ECHO - Cannot find Python at %PYTHON%.
    ECHO   Please set the "PYTHON" environment variable to the correct path.
    EXIT /B 1
  )
  EXIT /B 0

:ERROR
  ECHO   - Error %ERRORLEVEL%.
  ENDLOCAL
  EXIT /B %ERRORLEVEL%
