cd ..\emsdk-master\
call .\emsdk activate latest

cd %1
for /f "delims=" %%a in ('dir /s /b *.cpp') do (
 call set concat=%%concat%% %%a
 )

em++ %concat% -o %2