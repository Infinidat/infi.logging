@echo off
call "C:\Program Files\Microsoft Visual Studio 9.0\VC\vcvarsall.bat" x86

set CL_OPTS=/c /GR- /Gm- /GS- /GA /W1 /D UNICODE /D _UNICODE /Od ..\..\message_dll.cpp
set LINK_OPTS=/DLL /NODEFAULTLIB:libcmt /DEF:..\..\message_dll.def message_dll.obj ..\message_dll.res msvcrt.lib

echo Creating build directories

mkdir bin
mkdir bin\x86
mkdir bin\amd64

cd bin

echo Creating messages.mc file
python ..\make_message_file.py > messages.mc

if %errorlevel% neq 0 goto fail

echo Compiling messages.mc file
mc -U -h . -r . messages.mc
if %errorlevel% neq 0 goto fail

echo Compiling resources file
rc -l 409 -r -fo message_dll.res ..\message_dll.rc
if %errorlevel% neq 0 goto fail

cd x86

cl %CL_OPTS% 
if %errorlevel% neq 0 goto fail

link %LINK_OPTS%
if %errorlevel% neq 0 goto fail
cd ..\amd64

call "C:\Program Files\Microsoft Visual Studio 9.0\VC\bin\x86_amd64\vcvarsx86_amd64.bat"

cl %CL_OPTS% 
if %errorlevel% neq 0 goto fail

link /MACHINE:x64 %LINK_OPTS%
if %errorlevel% neq 0 goto fail

cd ..\..

echo .
echo .
echo Make succeeded, check bin directory under this directory.
exit /b 0

:fail
echo .
echo .
echo Make FAILED, check error messages.
exit /b 1
