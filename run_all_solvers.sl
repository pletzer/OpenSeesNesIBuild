#!/bin/bash
srun -ntasks=python example_truss_gen.py ParallelProfileSPD
srun -ntasks=python example_truss_gen.py Mumps
srun -ntasks=python example_truss_gen.py MPIDiagonal
python example_truss_gen.py BandGeneral
python example_truss_gen.py SparseGeneral
python example_truss_gen.py SparseSYM
python example_truss_gen.py FullGeneral
python example_truss_gen.py UmfPack
python example_truss_gen.py SuperLU
python example_truss_gen.py SProfileSPD
python example_truss_gen.py ProfileSPD
