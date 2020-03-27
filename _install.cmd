@echo off

REM The next two steps separate build an installation
REM The second step installs a development version. This version picks up changes from
REM changed source files immediately (but probably from new/renamed ones), 
REM but is prone to source file movement.

python setup.py sdist bdist_wheel 
python -m pip install -e .

REM This will install in the python distributions site-packages directory. (Dis-)Advantages
REM are inverse to the '-e' flag approach

REM python -m pip install .
