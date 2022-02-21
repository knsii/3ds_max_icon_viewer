@echo off

mode con: cols=70 lines=10

set package_name=icon_viewer

echo - cleanup package folder
del /s *.pyc >nul 2>&1
for /d /r %%g in ("__pycache__") do (
    if exist %%g (
        rd %%g
    )
)
echo.

echo - packing zip
powershell -Command "Compress-Archive 'icon_viewer','installer/*' -CompressionLevel 'Optimal' -DestinationPath '%package_name%.zip' -Force"
echo.

echo - rename to mzp
if exist %package_name%.mzp (
    del %package_name%.mzp
)
ren %package_name%.zip %package_name%.mzp
echo.

echo - done, installer saved to %package_name%.mzp
echo.

ping 127.0.0.1 -n 5 > nul