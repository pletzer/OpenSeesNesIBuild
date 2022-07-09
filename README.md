# OpenSeesNesIBuild
Instructions on how to build parallel OpenSees for Python on NeSI platform

## Build steps

Clone OpenSees Repo
```
git clone https://github.com/OpenSees/OpenSees
```

Clone this repo
```
git clone https://github.com/pletzer/OpenSeesNesIBuild.git
cd OpenSeesNesIBuild
```

Copy one of the Makefile.def files under `OpenSeesNesIBuild` to Makefile.def in OpenSees repo root
```
cp Makefile-mahuika.def ../OpenSees/Makefile.def
```

If on mahuika, load a few modules
```
ml purge
source start_mahuika.sh
```

Decide which python to use, e.g.
```
ml Python/3.9.9-gimkl-2020a
```

Compile OpenSees for Python
```
cd ../OpenSees/
mkdir lib
```

To clean the directory from a previous build (optional):
```
make wipe CHOME=$(pwd)
```

Now build:
```
make python -j 4 CHOME=$(pwd)
```

# Installing the Python OpenSees package

```
cd ..
cp OpenSeesNesIBuild/setup.py OpenSees/SRC/interpreter/
mkdir -p OpenSees/SRC/interpreter/custom_openseespy
mv OpenSees/SRC/interpreter/opensees.so OpenSees/SRC/interpreter/custom_openseespy/
pip install -e OpenSees/SRC/interpreter/
python -c "from custom_openseespy import opensees"
```

# Running more comprehensive tests

```
cd OpenSeesNesIBuild
srun --ntasks=2 python example_mpi_paralleltruss_explicit.py
```

To test that the parallel MUMPS solver works:
```
srun --ntasks=2 python example_mpi_paralleltruss_cen_diff.py
```

More tests:
```
srun --ntasks=2 python speed_test.py central_difference 2
srun --ntasks=2 python speed_test.py explicit_difference 2
```

Note: you may have to 
```
pip install sfsimodels --user
pip install o3seespy --user
```

# Error if rebuilding

UNANDESmaterials not listed in OpenSees/SRC/material/nD/Makefile wipe command

```
cd OpenSees/SRC/material/nD/UANDESmaterials/
make wipe
```
