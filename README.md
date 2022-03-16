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
cp Makefile-mahuika.def ../OpenSees/Makefile.def
```

Load a few modules
```
. start_ml_MM.sh
```

Decide which python to use, e.g.
```
ml Miniconda3
```

Compile OpenSees for Python
```
cd ../OpenSees/
export CHOME=$(pwd)
mkdir lib
```

To clean the directory from a previous build (optional):
```
make wipe
```

Now build:
```
make python -j 4
```

Test that you can import the `opensees` module:
```
export PYTHONPATH=$(pwd)/SRC/interpreter/:$PYTHONPATH
python -c "import opensees"
```

Test that MP functionality works
```
cp ../OpenSeesNesIBuild/example_mpi_paralleltruss_explicit.py .
cp ../OpenSeesNesIBuild/run_p2nt.sl .
sbatch run_p2nt.sl example_mpi_paralleltruss_explicit.py
```

# Error if rebuilding

UNANDESmaterials not listed in OpenSees/SRC/material/nD/Makefile wipe command

```
cd OpenSees/SRC/material/nD/UANDESmaterials/
make wipe
```
