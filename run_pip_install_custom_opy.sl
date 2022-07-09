cp setup.py ../OpenSees/SRC/interpreter/
mkdir -p ../OpenSees/SRC/interpreter/custom_openseespy
mv ../OpenSees/SRC/interpreter/opensees.so ../OpenSees/SRC/interpreter/custom_openseespy/
pip install -e ../OpenSees/SRC/interpreter/