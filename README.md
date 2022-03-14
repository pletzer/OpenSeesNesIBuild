# OpenSeesNesIBuild
Instructions on how to build parallel OpenSees for Python on NeSI platform

## Build steps

Clone OpenSees Repo
```
git clone https://github.com/OpenSees/OpenSees
```

Clone this repo
```
git clone git@github.com:pletzer/OpenSeesNesIBuild.git
cd OpenSeesNesIBuild
```

Copy one of the Makefile.def files under `OpenSeesNesIBuild` to Makefile.def in OpenSees repo root
```
cp Makefile-MM.def ../OpenSees/Makefile.def
```

Load a few modules
```
. start_ml_MM.sh
```

Compile OpenSees for Python
```
cd ../OpenSees/
export CHOME=$(pwd)
mkdir lib
make python
```

# Error if rebuilding

UNANDESmaterials not listed in OpenSees/SRC/material/nD/Makefile wipe command

```
cd OpenSees/SRC/material/nD/UANDESmaterials/
make wipe
```
