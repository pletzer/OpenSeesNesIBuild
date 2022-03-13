# OpenSeesNesIBuild
Instructions on how to build parallel OpenSees for Python on NeSI platform

## Build steps

Clone OpenSees Repo
Clone this repo
Copy Makefile to Makefile.def in OpenSees repo root
run: `. start_ml_MM.sl`
cd OpenSees/
mkdir lib
make python
