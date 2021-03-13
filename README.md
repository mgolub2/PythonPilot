# PythonPilot
Re-implement the Phase One Capture Pilot HTTP Interface in Python

Supports Getting and setting different parameters (Shutter Speed, ISO, File Format, etc.) from any IQ series back with Wifi. 
Supports a low level async functional API 
Supports a simple object based interface to a DB as well. 

## Usage

### PythonPilot API:

#### Installation
Is simple, simply create a virtual environment in a folder of your choosing, install the requirements from the requirements.txt file, and
then you can start developing with the API. An actual python package is still WIP. 
```
python -m venv venv
source venv/bin/activate  # or . venv/bin/activate.fish if you are a cool person.
pip install -r requirements.txt
```

#### Usage

WIP


## Future Goals

* Actual python package
* Multi-platform app via kivy
* Support Image downloading
* Support modifying more settings/Different objects other than the DB that the CapturePilot server normally supports
* But pre built apps on app store to support older IQ backs as CapturePilot is now no longer developed.