title Nephrostomy Tutor

START /MIN C:\Users\perkl\PlusApp-2.8.0.20191105-Telemed-Win32\bin\PlusServerLauncher.exe --connect --device-set-configuration-dir="C:\Users\perkl\Documents\NephrostomyTutor\Config" --config-file=Telemed-60mm-L12_Ascension.xml
START /MIN C:\Users\perkl\PlusApp-2.9.0.20201217-Win32\bin\PlusServerLauncher.exe --connect --device-set-configuration-dir="C:\D\NephrostomyTutor-main\Config" --config-file=PlusDeviceSet_Server_IntelRealSenseVideo.xml

cd "C:\Users\perkl\AppData\Local\NA-MIC\Slicer 5.0.2"
START Slicer.exe --python-code "slicer.modules.nephrostomytutor.widgetRepresentation();slicer.modules.NephrostomyTutorWidget.launchGuideletButton.click()"

REM cd %HOMEPATH%\Anaconda3\condabin
REM call conda activate kerasGPUEnv
REM cd %HOMEPATH%
REM call python .\Documents\CentralLineTutor\WorkflowAnalysis\kerasClassifier.py --cnn_model_name=mobileNetv2_cnn_lovo_3 --lstm_model_name=LSTM_parallel_TBME_lovo_50f4ds_3 --model_directory=C:/Users/perk/Documents/CentralLineTutor/CentralLineTutor/CentralLineTutor/Resources/Networks
REM call conda deactivate