@echo off
call "C:\Program Files\Microsoft Visual Studio 9.0\VC\vcvarsall.bat" x86

set LINK_OPTS=/DLL /NOENTRY ..\message_dll.res msvcrt.lib

echo Creating build directories

mkdir bin
mkdir bin\x86
mkdir bin\amd64

cd bin

echo Creating messages.mc file
python ..\make_message_file.py > messages.mc

if %errorlevel% neq 0 goto fail

echo Compiling messages.mc file
mc -U messages.mc
if %errorlevel% neq 0 goto fail

echo Compiling resources file
rc -r -fo message_dll.res ..\message_dll.rc
if %errorlevel% neq 0 goto fail

cd x86

link /MACHINE:x86 %LINK_OPTS%
if %errorlevel% neq 0 goto fail
cd ..\amd64

call "C:\Program Files\Microsoft Visual Studio 9.0\VC\bin\x86_amd64\vcvarsx86_amd64.bat"

link /MACHINE:x64 %LINK_OPTS%
if %errorlevel% neq 0 goto fail

cd ..\..

copy bin\x86\message_dll.dll ..\..\src\infi\logging\eventlog_x86.dll
if %errorlevel% neq 0 goto fail_copy

copy bin\amd64\message_dll.dll ..\..\src\infi\logging\eventlog_amd64.dll
if %errorlevel% neq 0 goto fail_copy

echo .
echo .
echo Make succeeded, check bin directory under this directory.
exit /b 0

:fail
echo .
echo .
echo Make FAILED, check error messages.
exit /b 1

:fail_copy
echo .
echo .
echo Failed to copy the DLL files into the src directory, please check that it exists (..\..\src\infi\logging) and
echo that you don't have any process opened with these DLLs (event viewer, etc.)
exit /b 2