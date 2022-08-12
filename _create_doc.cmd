@echo off
REM Builds doc in doc/sphinx
REM entry point: doc\sphinx\_build\html\index.html
echo "Adjust (absolute) sys.path in doc\sphinx\conf.py if documentation creation fails"
setlocal EnableDelayedExpansion 
pushd %CD%
sphinx-apidoc -F -H "mbeex" -A "Michael" -o doc/sphinx mbeex
cd doc/sphinx
.\make.bat html
popd
endlocal

