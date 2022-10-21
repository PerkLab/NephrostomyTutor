import os, sys
from __main__ import vtk, qt, ctk, slicer
from functools import partial

import pandas
from Guidelet import GuideletLoadable, GuideletLogic, GuideletTest, GuideletWidget
from Guidelet import Guidelet
import PythonMetricsCalculator
import logging
import time
import operator
import numpy

class NephrostomyTutor(GuideletLoadable):
  """Uses GuideletLoadable class, available at:
  """

  def __init__(self, parent):
    GuideletLoadable.__init__(self, parent)
    self.parent.title = "Nephrostomy Tutor"
    self.parent.categories = ["Training"]
    self.parent.dependencies = []
    self.parent.contributors = ["Rebecca Hisey, Leah Groves, Tamas Ungi"]
    self.parent.helpText = """  """
    self.parent.acknowledgementText = """  """

class NephrostomyTutorWidget(GuideletWidget):
  """Uses GuideletWidget base class, available at:
  """

  def __init__(self, parent = None):
    GuideletWidget.__init__(self, parent)

  def setup(self):
    GuideletWidget.setup(self)

  def addLauncherWidgets(self):
    GuideletWidget.addLauncherWidgets(self)

  def onConfigurationChanged(self, selectedConfigurationName):
    GuideletWidget.onConfigurationChanged(self, selectedConfigurationName)
    #settings = slicer.app.userSettings()

  def createGuideletInstance(self):
    return NephrostomyTutorGuidelet(None, self.guideletLogic, self.selectedConfigurationName)

  def createGuideletLogic(self):
    return NephrostomyTutorLogic()


class NephrostomyTutorLogic(GuideletLogic):
  """Uses GuideletLogic base class, available at:
  """ #TODO add path

  def __init__(self, parent = None):
    GuideletLogic.__init__(self, parent)

    self.addValuesToNo3DGuidanceConfiguration()
    self.addValuesToUltrasoundSliderConfiguration()
    self.addValuesToUltrasoundDualConfiguration()

  def addValuesToDefaultConfiguration(self):
    GuideletLogic.addValuesToDefaultConfiguration(self)
    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)

    settingsList = {
                   'StyleSheet' : os.path.join( moduleDir, 'Resources/StyleSheets/NephrostomyTutorStyle.qss' ), #overwrites the default setting param of base
                   'TestMode' : 'False',
                   'RecordingFilenamePrefix' : 'NephrostomyTutorRec-',
                   'UltraSoundBrightnessControl' : 'Slider',
                   'SavedScenesDirectory': os.path.join( moduleDir, 'SavedScenes' ),
                   'ProcedureLayout': Guidelet.VIEW_ULTRASOUND_CAM_3D,
                   'ResultsLayout': Guidelet.VIEW_ULTRASOUND_CAM_3D, #overwrites the default setting param of base
           'PlusWebcamServerHostNamePort': 'localhost:18945',
                   }

    self.updateSettings(settingsList, 'Default')

  ## Set up a custom configuration   
  def addValuesToNo3DGuidanceConfiguration(self):
    settingsList = {}
    self.updateUserPreferencesFromSettings( settingsList, 'Default' ) # Copy values from the default configuration
    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)

    settingsList[ 'SavedScenesDirectory' ] = os.path.join( moduleDir, 'SavedScenes' )
    settingsList[ 'DisplayNeedleModel' ] = 'False'
    settingsList[ 'ProcedureLayout' ] = Guidelet.VIEW_ULTRASOUND
    settingsList[ 'ResultsLayout' ] = Guidelet.VIEW_ULTRASOUND_3D
    settingsList[ 'HideTargetViews' ] = "2D"

    self.updateSettings( settingsList, 'No 3D Guidance' )

  ## Set up a custom configuration
  def addValuesToUltrasoundSliderConfiguration(self):
    settingsList = {}
    self.updateUserPreferencesFromSettings(settingsList, 'Default')  # Copy values from the default configuration
    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)

    settingsList['SavedScenesDirectory'] = os.path.join(moduleDir, 'SavedScenes')
    settingsList[ 'ProcedureLayout' ] = Guidelet.VIEW_ULTRASOUND_CAM_3D
    settingsList[ 'ResultsLayout' ] = Guidelet.VIEW_ULTRASOUND_3D
    settingsList['UltrasoundBrightnessControl'] = 'Buttons'

    self.updateSettings(settingsList, 'Ultrasound Buttons')

  ## Set up a custom configuration
  def addValuesToUltrasoundDualConfiguration(self):
    settingsList = {}
    self.updateUserPreferencesFromSettings(settingsList, 'Default')  # Copy values from the default configuration
    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)

    settingsList['SavedScenesDirectory'] = os.path.join(moduleDir, 'SavedScenes')
    settingsList[ 'ProcedureLayout' ] = Guidelet.VIEW_ULTRASOUND_CAM_3D
    settingsList[ 'ResultsLayout' ] = Guidelet.VIEW_ULTRASOUND_3D
    settingsList['UltrasoundBrightnessControl'] = 'Dual'

    self.updateSettings(settingsList, 'Ultrasound Buttons and Slider')
  
  # This function allows us to conveniently copy settings from another configuration (e.g. Default)
  # TODO: Is there something like this already in the GuideletLogic class?
  def updateUserPreferencesFromSettings( self, settingsNameValueMap, configurationName = None ):
    settings = slicer.app.userSettings()

    if not configurationName:
      groupString = self.moduleName
    else:
      groupString = self.moduleName + '/Configurations/' + configurationName

    settings.beginGroup( groupString )
    for name in settings.allKeys():
      settingsNameValueMap[ name ] = settings.value( name )
    settings.endGroup()

class NephrostomyTutorTest(GuideletTest):
  """This is the test case for your scripted module.
  """

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    GuideletTest.runTest(self)
    #self.test_NephrostomyTutor1() #add applet specific tests here

class NephrostomyTutorGuidelet(Guidelet):

  def __init__(self, parent, logic, configurationName='Default'):
    self.resultsCollapsibleButton = None

    moduleDirectoryPath = slicer.modules.nephrostomytutor.path.replace('NephrostomyTutor.py', '')
    self.moduleDir = moduleDirectoryPath
    try:
     self.needleTipToNeedle = slicer.util.getNode('NeedleTipToNeedle')
    except slicer.util.MRMLNodeNotFoundException:
      needleTiptoNeedleFilePath = os.path.join(moduleDirectoryPath, 'Resources', 'NeedleTipToNeedle.h5')
      self.needleTipToNeedle = slicer.util.loadTransform(needleTiptoNeedleFilePath)
    try:
      self.needleToReference = slicer.util.getNode('NeedleToReference')
    except slicer.util.MRMLNodeNotFoundException:
      self.needleToReference = slicer.vtkMRMLLinearTransformNode()
      self.needleToReference.SetName('NeedleToReference')
      slicer.mrmlScene.AddNode(self.needleToReference)

    Guidelet.__init__(self, parent, logic, configurationName)

    logging.debug('NephrostomyTutorGuidelet.__init__')

    self.ultrasound.guideletParent.parameterNode.SetParameter('LiveUltrasoundNodeName','Image_Image')
    self.logic.addValuesToDefaultConfiguration()
    self.webcam1RGBConnectorNode = self.createWebcamPlusConnector()
    self.webcam1RGBConnectorNode.Start()

    try:
      self.webcam1DEPTHConnectorNode = slicer.util.getNode('DEPTH1Connector')
    except slicer.util.MRMLNodeNotFoundException:
      self.webcam1DEPTHConnectorNode = self.createRealSensePlusConnectors(1, 18948, 'DEPTH')
    self.webcam1DEPTHConnectorNode.RegisterIncomingMRMLNode(self.webcam1DEPTH)
    self.webcam1DEPTHConnectorNode.Start()

    try:
      self.webcam0RGBConnectorNode = slicer.util.getNode('RGB0Connector')
    except slicer.util.MRMLNodeNotFoundException:
      self.webcam0RGBConnectorNode = self.createRealSensePlusConnectors(0, 18949,'RGB')
    self.webcam0RGBConnectorNode.RegisterIncomingMRMLNode(self.webcam0RGB)
    self.webcam0RGBConnectorNode.Start()

    try:
      self.webcam0DEPTHConnectorNode = slicer.util.getNode('DEPTH0Connector')
    except slicer.util.MRMLNodeNotFoundException:
      self.webcam0DEPTHConnectorNode = self.createRealSensePlusConnectors(0, 18950, 'DEPTH')
    self.webcam0DEPTHConnectorNode.RegisterIncomingMRMLNode(self.webcam0DEPTH)
    self.webcam0DEPTHConnectorNode.Start()

    # Set up main frame.
    self.sliceletDockWidget.setObjectName('NephrostomyTutorPanel')
    self.sliceletDockWidget.setWindowTitle('Nephrostomy Tutor')
    self.mainWindow.setWindowTitle('NephrostomyTutor')
    self.mainWindow.windowIcon = qt.QIcon(moduleDirectoryPath + '/Resources/Icons/NephrostomyTutor.png')

    self.setupScene()

    self.navigationView = self.VIEW_ULTRASOUND_3D

    self.usMarkersPropertiesDict = {}
    self.setupSliceUSMarkers("Red")

    # Setting button open on startup.
    self.ultrasoundCollapsibleButton.setProperty('collapsed', False)
    self.ultrasoundCollapsibleButton.text = "Procedure"
    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)
    sceneSaveDirectory = os.path.join( moduleDir, 'SavedScenes' )
    self.logic.updateSettings({'SavedScenesDirectory': sceneSaveDirectory}, self.configurationName)
    node = self.logic.getParameterNode()
    self.logic.updateParameterNodeFromUserPreferences(node, {'SavedScenesDirectory': sceneSaveDirectory})
    self.createLoginPage()
    self.sliceletDockWidget.setWidget(self.loginPanel)

  def createLoginPage(self):
    self.loginPanel = qt.QFrame()
    self.loginPanelLayout = qt.QVBoxLayout(self.loginPanel)

    self.topPanelLayout = qt.QGridLayout(self.sliceletPanel)
    self.loginPanelLayout.addLayout(self.topPanelLayout)
    self.setupTopPanel()

    self.loginButtonLayout = qt.QFormLayout()

    self.spacer = qt.QLabel('\n\n\n\n\n\n')
    self.loginButtonLayout.addWidget(self.spacer)
    self.userIDLineEdit = qt.QLineEdit('User ID')
    self.loginButtonLayout.addWidget(self.userIDLineEdit)

    self.loginPushButton = qt.QPushButton('Login')
    self.loginButtonLayout.addWidget(self.loginPushButton)
    self.loginPushButton.connect('clicked()',self.onLoginClicked)

    self.loginPanelLayout.addLayout(self.loginButtonLayout)

  def onLoginClicked(self):
    self.sliceletDockWidget.setWindowTitle('User ID: ' + self.userIDLineEdit.text)
    node = self.logic.getParameterNode()
    #sceneSaveDirectory = node.GetParameter('SavedScenesDirectory')
    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)

    sceneSaveDirectory = os.path.join(moduleDir, 'SavedScenes')
    if self.userIDLineEdit.text != '' and self.userIDLineEdit.text != 'User ID':
      self.logic.updateSettings({'SavedScenesDirectory': sceneSaveDirectory}, self.configurationName)
      self.logic.updateParameterNodeFromUserPreferences(node, {'SavedScenesDirectory': sceneSaveDirectory})
      self.sliceletDockWidget.setWidget(self.sliceletPanel)
    else:
      moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)
      sceneSaveDirectory = os.path.join(moduleDir, 'SavedScenes')
      self.logic.updateSettings({'SavedScenesDirectory': sceneSaveDirectory}, self.configurationName)
      self.logic.updateParameterNodeFromUserPreferences(node, {'SavedScenesDirectory': sceneSaveDirectory})

  def createWebcamPlusConnector(self):
    try:
      webcamConnectorNode = slicer.util.getNode('WebcamPlusConnector')
    except slicer.util.MRMLNodeNotFoundException:
      webcamConnectorNode = slicer.vtkMRMLIGTLConnectorNode()
      webcamConnectorNode.SetName('WebcamPlusConnector')
      slicer.mrmlScene.AddNode(webcamConnectorNode)
      hostNamePort = self.parameterNode.GetParameter('PlusWebcamServerHostNamePort')
      [hostName, port] = hostNamePort.split(':')
      webcamConnectorNode.SetTypeClient(hostName, int(port))
      logging.debug('Webcam PlusConnector Created')
    return webcamConnectorNode

  def createRealSensePlusConnectors(self,cameraNumber,port,imageType):
    connectorNodeName = imageType + str(cameraNumber) + "Connector"
    try:
      realsenseConnectorNode = slicer.util.getNode(connectorNodeName)
    except slicer.util.MRMLNodeNotFoundException:
      # if not webcamConnectorNode:
      realsenseConnectorNode = slicer.vtkMRMLIGTLConnectorNode()
      realsenseConnectorNode.SetName(connectorNodeName)
      slicer.mrmlScene.AddNode(realsenseConnectorNode)
      hostName = "localhost"
      realsenseConnectorNode.SetTypeClient(hostName,int(port))
      logging.debug(connectorNodeName + ' Created')
    return realsenseConnectorNode


  def createFeaturePanels(self):
    # Create GUI panels.

    featurePanelList = Guidelet.createFeaturePanels(self)
    self.addRecordingsTableToUltrasoundPanel()
    self.addProcedureProgressToUltrasoundPanel()

    self.resultsCollapsibleButton = ctk.ctkCollapsibleButton()
    self.setupResultsPanel()

    featurePanelList[len(featurePanelList):] = [self.resultsCollapsibleButton]

    return featurePanelList

  def __del__(self):#common
    self.preCleanup()

  # Clean up when guidelet is closed
  def preCleanup(self):#common
    Guidelet.preCleanup(self)
    logging.debug('preCleanup')

  def setupConnections(self):
    logging.debug('ScoliUs.setupConnections()')
    Guidelet.setupConnections(self)
    #slicer.mrmlScene.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateRecordingsTable)
    #self.recordingsTable.connect('cellChanged(int, int)', self.updateSequenceBrowserNodeName)
    #self.saveRecordingsButton.connect('clicked()', self.saveAllRecordings)
    self.ultrasoundCollapsibleButton.connect('toggled(bool)', self.onUltrasoundPanelToggled)
    self.resultsCollapsibleButton.connect('toggled(bool)', self.onResultsPanelToggled)
    self.ultrasound.startStopRecordingButton.connect('clicked(bool)', self.onStartStopRecordingClicked)

    # Keyboard shortcuts
    if ( not hasattr( self, 'startStopShortcutPlus' ) or self.startStopShortcutPlus is None ):
      self.startStopShortcutPlus = qt.QShortcut( qt.QKeySequence( "+" ), self.sliceletDockWidget )
    self.startStopShortcutPlus.connect('activated()', self.ultrasound.startStopRecordingButton.click )


  def setupScene(self): #applet specific
    logging.debug('setupScene')
    moduleDirectoryPath = slicer.modules.nephrostomytutor.path.replace('NephrostomyTutor.py', '')
    try:
      self.referenceToRas = slicer.util.getNode('ReferenceToRas')
    except slicer.util.MRMLNodeNotFoundException:
      referenceToRasFilePath = os.path.join(moduleDirectoryPath, 'Resources', 'ReferenceToRas.h5')
      self.referenceToRas = slicer.util.loadTransform(referenceToRasFilePath)

    Guidelet.setupScene(self)

    # Transforms
    logging.debug('Create transforms')

    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)

    try:
      self.transdToReference = slicer.util.getNode('TransdToReference')
    except slicer.util.MRMLNodeNotFoundException:
      self.transdToReference = slicer.vtkMRMLLinearTransformNode()
      self.transdToReference.SetName("TransdToReference")
      m = self.logic.readTransformFromSettings('TransdToReference', self.configurationName)
      if m:
        self.transdToReference.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.transdToReference)

    try:
      self.probeToReference = slicer.util.getNode('ProbeToReference')
    except slicer.util.MRMLNodeNotFoundException:
      self.probeToReference = slicer.vtkMRMLLinearTransformNode()
      self.probeToReference.SetName("ProbeToReference")
      slicer.mrmlScene.AddNode(self.probeToReference)

    try:
      self.probeModelToProbe = slicer.util.getNode('ProbeModelToReference')
    except slicer.util.MRMLNodeNotFoundException:
      probeToReferenceFilePath = os.path.join(moduleDir, 'Resources', 'ProbeModelToProbe_L12.h5')
      self.probeModelToProbe = slicer.util.loadTransform(probeToReferenceFilePath)

    try:
      self.needleToReference = slicer.util.getNode('NeedleToReference')
    except slicer.util.MRMLNodeNotFoundException:
      self.needleToReference = slicer.vtkMRMLLinearTransformNode()
      self.needleToReference.SetName('NeedleToReference')
      slicer.mrmlScene.AddNode(self.needleToReference)

    try:
      self.needleTipToNeedle = slicer.util.getNode('NeedleTipToNeedle')
    except slicer.util.MRMLNodeNotFoundException:
      needleTiptoNeedleFilePath = os.path.join(moduleDir, 'Resources', 'NeedleTipToNeedle.h5')
      self.needleTipToNeedle = slicer.util.loadTransform(needleTiptoNeedleFilePath)

    #for pre-recorded procedures only
    try:
      self.vesselToModel = slicer.util.getNode('VesselToModel')
    except slicer.util.MRMLNodeNotFoundException:
      try:
        vesselToModelPath = os.path.join(moduleDir, 'Resources', 'VesselToModel.h5')
        self.vesselToModel = slicer.util.loadTransform(vesselToModelPath)
      except RuntimeError:
        logging.info("Could not read vessel to model transform")

    try:
      self.imageToProbe = slicer.util.getNode('ImageToProbe')
    except slicer.util.MRMLNodeNotFoundException:
      transformFilePath = os.path.join(moduleDir,'Resources','ImageToProbe.h5')
      self.imageToProbe = slicer.util.loadTransform(transformFilePath)
      self.imageToProbe.SetName('ImageToProbe')
      slicer.mrmlScene.AddNode(self.imageToProbe)

    try:
      self.imageToReference = slicer.util.getNode('ImageToReference')
    except slicer.util.MRMLNodeNotFoundException:
      self.imageToReference = slicer.vtkMRMLLinearTransformNode()
      self.imageToReference.SetName('ImageToReference')
      m = self.logic.readTransformFromSettings('ImageToReference', self.configurationName)
      if m:
        self.imageToReference.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.imageToReference)

    try:
      self.imageToImage = slicer.util.getNode('ImageToImage')
    except slicer.util.MRMLNodeNotFoundException:
      self.imageToImage = slicer.vtkMRMLLinearTransformNode()
      self.imageToImage.SetName('ImageToImage')
      m = self.logic.readTransformFromSettings('ImageToImage', self.configurationName)
      if m:
        self.imageToImage.SetMatrixTransformToParent(m)
      slicer.mrmlScene.AddNode(self.imageToImage)

    # Models
    logging.debug('Create models')

    try:
      self.usProbeModel = slicer.util.getNode('UsProbe')
    except slicer.util.MRMLNodeNotFoundException:
    #if not self.usProbeModel:
      modelFilePath = os.path.join(moduleDir, 'Resources', 'Telemed_L12.stl')
      self.usProbeModel = slicer.util.loadModel(modelFilePath)
      self.usProbeModel.SetName('UsProbe')
      self.usProbeModel.GetDisplayNode().SetColor(0.9, 0.9, 0.9)

    try:
      self.needleModel = slicer.util.getNode('NeedleModel')
    except slicer.util.MRMLNodeNotFoundException:
    #if not self.needleModel:
      self.needleModel = slicer.modules.createmodels.logic().CreateNeedle(80, 1.0, 0, 0)
      self.needleModel.SetName('NeedleModel')

    print(sys.version)
    if sys.version.startswith('3'):
      try:
        self.probeTransform = slicer.util.getNode('Flip2')
      except slicer.util.MRMLNodeNotFoundException:
        transformFilePath = os.path.join(moduleDir, 'Resources', 'Flip2.h5')
        self.probeTransform = slicer.util.loadTransform(transformFilePath)
        self.probeTransform.SetName('Flip2')
    # Build transform tree
    logging.debug('Set up transform tree')

    self.transdToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.probeToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.imageToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.probeModelToProbe.SetAndObserveTransformNodeID(self.probeToReference.GetID())
    self.needleToReference.SetAndObserveTransformNodeID(self.referenceToRas.GetID())
    self.needleTipToNeedle.SetAndObserveTransformNodeID(self.needleToReference.GetID())
    self.imageToProbe.SetAndObserveTransformNodeID(self.probeToReference.GetID())
    self.imageToImage.SetAndObserveTransformNodeID(self.imageToProbe.GetID())
    self.needleModel.SetAndObserveTransformNodeID(self.needleTipToNeedle.GetID())
    if sys.version.startswith('3'):
      self.usProbeModel.SetAndObserveTransformNodeID(self.probeTransform.GetID())
      self.probeTransform.SetAndObserveTransformNodeID(self.probeModelToProbe.GetID())
    else:
      self.usProbeModel.SetAndObserveTransformNodeID(self.probeModelToProbe.GetID())
    #self.imageImage.SetAndObserveTransformNodeID(self.imageToProbe.GetID())
    image_reference = slicer.mrmlScene.GetNodesByClassByName('vtkMRMLScalarVolumeNode', 'Image_Image')
    self.image_reference = image_reference.GetItemAsObject(0)
    self.image_reference.SetAndObserveTransformNodeID(self.imageToProbe.GetID())

    # Watch if the active volume is changed - set it back to Image_Reference
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.AddObserver( vtk.vtkCommand.ModifiedEvent, self.updateAllBrowserNodes )

    # Ensure that the sequence browser toolbar(s) is not made visible
    sequenceBrowserToolBars = slicer.util.mainWindow().findChildren( "qMRMLSequenceBrowserToolBar" )
    for toolBar in sequenceBrowserToolBars:
      toolBar.connect('visibilityChanged(bool)', partial( self.setSequenceBrowserToolBarsVisible, False ) )

    # Show the slice intersections for the needle
    if( self.needleModel is not None and self.needleModel.GetDisplayNode() is not None ):
      if ( self.parameterNode.GetParameter('DisplayNeedleModel') == 'False' ):
        self.needleModel.GetDisplayNode().SetSliceIntersectionVisibility(False)
      else:
        self.needleModel.GetDisplayNode().SetSliceIntersectionVisibility(False)

    # Create the target node
    if ( not hasattr( self, 'targetFiducialNode' ) ):
      self.targetFiducialNode = slicer.vtkMRMLMarkupsFiducialNode()
      self.targetFiducialNode.SetName( "Target" )
      self.targetFiducialNode.SetScene( slicer.mrmlScene )
      slicer.mrmlScene.AddNode( self.targetFiducialNode )

    slicer.mrmlScene.AddObserver( slicer.mrmlScene.NodeAddedEvent, self.onNodeAdded )

    # Hide slice view annotations (patient name, scale, color bar, etc.) as they
    # decrease reslicing performance by 20%-100%
    logging.debug('Hide slice view annotations')
    import DataProbe
    dataProbeUtil=DataProbe.DataProbeLib.DataProbeUtil()
    dataProbeParameterNode=dataProbeUtil.getParameterNode()
    dataProbeParameterNode.SetParameter('showSliceViewAnnotations', '0')

    try:
      self.webcam1RGB = slicer.util.getNode('ImageRGB_ImageRGB')
    except slicer.util.MRMLNodeNotFoundException:
      # if not self.webcamReference:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam1RGB = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam1RGB.SetName('ImageRGB_ImageRGB')
      self.webcam1RGB.SetSpacing(imageSpacing)
      self.webcam1RGB.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam1RGB)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam1RGB.SetAndObserveDisplayNodeID(displayNode.GetID())

    try:
      self.webcam1DEPTH = slicer.util.getNode('ImageDEPTH_ImageDEPT')

    except slicer.util.MRMLNodeNotFoundException:
      # if not self.webcamReference:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam1DEPTH = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam1DEPTH.SetName('ImageDEPTH_ImageDEPT')
      self.webcam1DEPTH.SetSpacing(imageSpacing)
      self.webcam1DEPTH.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam1DEPTH)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam1DEPTH.SetAndObserveDisplayNodeID(displayNode.GetID())

    try:
      self.webcam0RGB = slicer.util.getNode('Image1RGB_Image1RGB')

    except slicer.util.MRMLNodeNotFoundException:
      # if not self.webcamReference:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam0RGB = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam0RGB.SetName('Image1RGB_Image1RGB')
      self.webcam0RGB.SetSpacing(imageSpacing)
      self.webcam0RGB.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam0RGB)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam0RGB.SetAndObserveDisplayNodeID(displayNode.GetID())

    try:
      self.webcam0DEPTH = slicer.util.getNode('Image1DEPTH_Image1DE')

    except slicer.util.MRMLNodeNotFoundException:
      # if not self.webcamReference:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam0DEPTH = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam0DEPTH.SetName('Image1DEPTH_Image1DE')
      self.webcam0DEPTH.SetSpacing(imageSpacing)
      self.webcam0DEPTH.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam0DEPTH)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam0DEPTH.SetAndObserveDisplayNodeID(displayNode.GetID())
    self.setupWebcamResliceDriver()

    # Set up 3D camera

    layoutManager = slicer.app.layoutManager()
    viewCount = layoutManager.threeDViewCount
    if viewCount < 1:
      logging.error('No 3D views found!')
      return

    self.first3dView = layoutManager.threeDWidget(0).threeDView()
    self.firstViewNode = self.first3dView.mrmlViewNode()
    renderer = self.first3dView.renderWindow().GetRenderers().GetItemAsObject(0)

    camerasLogic = slicer.modules.cameras.logic()
    firstCameraNode = camerasLogic.GetViewActiveCameraNode(self.firstViewNode)
    camera = firstCameraNode.GetCamera()

    camera.SetPosition(0.0, 800, 1400.0)  # 120 cm behind and 10 cm below neck
    camera.SetFocalPoint(0.0, 0.0, 0.0)
    camera.SetViewUp(0.0, 0.0, 1.0)  # Head up, looking towards A
    camera.SetRoll(0)  # Default in Slicer

    renderer.ResetCameraClippingRange()
    metricsDirectory = os.path.join(moduleDir, os.pardir, os.pardir, "Metrics", "metrics")
    self.setupMetrics(metricsDirectory)

  def setupTopPanel(self):
    buttonMinWidth = 48

    #self.topLayout = qt.QGridLayout()

    self.loadButton = qt.QPushButton()
    self.loadButton.setIcon(qt.QIcon(qt.QApplication.style().standardIcon(qt.QStyle.SP_DialogOpenButton)))
    self.loadButton.setMinimumWidth(buttonMinWidth)
    self.topPanelLayout.addWidget(self.loadButton, 0, 0)
    self.loadButton.connect('clicked()', self.onLoadButtonClicked)

    self.saveButton = qt.QPushButton()
    self.saveButton.setIcon(qt.QIcon(qt.QApplication.style().standardIcon(qt.QStyle.SP_DialogSaveButton)))
    self.saveButton.setMinimumWidth(buttonMinWidth)
    self.topPanelLayout.addWidget(self.saveButton, 0, 1)
    self.saveButton.connect('clicked()', self.saveAllRecordings)

    self.openSettingsButton = qt.QPushButton()
    self.openSettingsButton.toolTip = 'Settings'
    settingsIconPath = slicer.modules.nephrostomytutor.path.replace('NephrostomyTutor.py', "Resources/Icons/SettingsIcon.png")
    self.openSettingsButton.setIcon(qt.QIcon(settingsIconPath))
    self.openSettingsButton.setMinimumWidth(buttonMinWidth)
    self.topPanelLayout.addWidget(self.openSettingsButton, 0, 2)
    self.openSettingsButton.connect('clicked()', self.onOpenSettingsClicked)

    mainWindow = slicer.util.mainWindow()
    self.settingsWidget = qt.QDialog(mainWindow)
    self.settingsWidget.setStyleSheet("background-color:white")
    #self.settingsWidget.setWindowFlags(qt.Qt.WindowStaysOnTopHint)
    self.settingsWidget.setModal(True)
    self.settingsFrame = qt.QFrame(self.settingsWidget)
    self.settingsFrame.setFrameStyle(0x0006)
    self.settingsWidget.setWindowTitle('Nephrostomy Tutor Settings')
    self.settingsWidget.setWindowIcon(qt.QIcon(settingsIconPath))
    self.settingsPopupGeometry = qt.QRect()

    if mainWindow:
      mainWindowGeometry = mainWindow.geometry
      self.windowWidth = mainWindow.width * 0.35
      self.windowHeight = mainWindow.height * 0.35
      self.settingsPopupGeometry.setWidth(self.windowWidth)
      self.settingsPopupGeometry.setHeight(self.windowHeight)
      self.popupPositioned = False
      self.settingsWidget.setGeometry(self.settingsPopupGeometry)
      self.settingsFrame.setGeometry(self.settingsPopupGeometry)
      self.settingsWidget.move(mainWindow.width/2.0 - self.windowWidth,mainWindow.height/2 - self.windowHeight)

    self.logoutButton = qt.QPushButton()
    self.logoutButton.connect('clicked()',self.onLogoutButtonClicked)
    self.logoutButton.toolTip = 'Logout'
    self.topPanelLayout.addWidget(self.logoutButton,0,3)
    logoutIconPath = slicer.modules.nephrostomytutor.path.replace('NephrostomyTutor.py', '/Resources/Icons/ExitIcon.png')

    self.logoutButton.setIcon(qt.QIcon(logoutIconPath))

    self.exitButton = qt.QPushButton()
    self.exitButton.toolTip = 'Exit'
    exitIconPath = slicer.modules.nephrostomytutor.path.replace('NephrostomyTutor.py', '/Resources/Icons/closeIcon.png')

    self.exitButton.setIcon(qt.QIcon(exitIconPath))
    self.exitButton.setMinimumWidth(buttonMinWidth)
    self.topPanelLayout.addWidget(self.exitButton, 0, 4)
    self.exitButton.connect('clicked()', self.terminatePlusServer)
    #self.exitButton.connect('clicked()', self.onExitButtonClicked)


    self.recordingPlayWidget = slicer.qMRMLSequenceBrowserPlayWidget()
    self.topPanelLayout.addWidget(self.recordingPlayWidget,1,0,1,-1)

  def terminatePlusServer(self):
    logging.info('terminating plus')
    import subprocess
    batchFileLocation = slicer.modules.nephrostomytutor.path.replace('NephrostomyTutor/NephrostomyTutor/NephrostomyTutor.py', 'StopPlus.bat')
    p = subprocess.Popen(batchFileLocation,shell=True)
    self.onExitButtonClicked()

  def onExitButtonClicked(self):
      mainwindow = slicer.util.mainWindow()
      mainwindow.close()


  def onLogoutButtonClicked(self):
    self.sliceletDockWidget.setWindowTitle('Nephrostomy Tutor')
    node = self.logic.getParameterNode()
    self.sliceletDockWidget.setWidget(self.loginPanel)
    self.userIDLineEdit.setText('User ID')
    moduleDir = os.path.dirname(slicer.modules.nephrostomytutor.path)
    sceneSaveDirectory = os.path.join(moduleDir, 'SavedScenes')
    self.logic.updateSettings({'SavedScenesDirectory': sceneSaveDirectory}, self.configurationName)
    self.logic.updateParameterNodeFromUserPreferences(node, {'SavedScenesDirectory': sceneSaveDirectory})

  def onLoadButtonClicked(self):
    io = slicer.app.ioManager()
    params = {}
    io.openDialog("VolumeFile", slicer.qSlicerDataDialog.Read, params)

  def onViewChanged(self, caller):
    if self.viewSelectorComboBox.currentIndex == 0:
      view = self.VIEW_ULTRASOUND
    elif self.viewSelectorComboBox.currentIndex == 1:
      view = self.VIEW_ULTRASOUND_3D
    elif self.viewSelectorComboBox.currentIndex == 2:
      view = self.VIEW_3D_ULTRASOUND
    elif self.viewSelectorComboBox.currentIndex == 3:
      view = self.VIEW_ULTRASOUND_CAM_3D
    elif self.viewSelectorComboBox.currentIndex == 4:
      view = self.VIEW_ULTRASOUND_DUAL_3D
    elif self.viewSelectorComboBox.currentIndex == 5:
      view = self.VIEW_3D
    elif self.viewSelectorComboBox.currentIndex == 6:
      view = self.VIEW_DUAL_3D
    else:
      view = self.VIEW_TRIPLE_3D
    self.selectView(view)

  def setupSettingsConnections(self):
    self.newTrainingSessionButton.connect('clicked(bool)', self.onNewTrainingSession)
    self.showFullSlicerInterfaceButton.connect('clicked()', self.onShowFullSlicerInterfaceClicked)
    self.showFullSlicerInterfaceButton.connect('clicked()', self.onCloseSettingsClicked)
    self.showGuideletFullscreenButton.connect('clicked()', self.onShowGuideletFullscreenButton)
    self.saveSceneButton.connect('clicked()', self.onSaveSceneClicked)
    self.linkInputSelector.connect("nodeActivated(vtkMRMLNode*)", self.onConnectorNodeActivated)
    self.saveDirectoryLineEdit.connect('currentPathChanged(QString)', self.onSaveDirectoryPreferencesChanged)
    self.closeSettingsButton.connect('clicked(bool)', self.onCloseSettingsClicked)

  def onCloseSettingsClicked(self):
    self.settingsWidget.hide()


  def onOpenSettingsClicked(self):
    self.settingsLayout = qt.QVBoxLayout()
    self.settingsLayout.setContentsMargins(12, 4, 4, 4)
    self.settingsLayout.setSpacing(4)

    self.settingsButtonLayout = qt.QFormLayout()
    self.settingsButtonLayout.setContentsMargins(12, 4, 4, 4)
    self.settingsButtonLayout.setSpacing(4)

    self.newTrainingSessionButton = qt.QPushButton("Start New Training Session")
    self.settingsButtonLayout.addRow(self.newTrainingSessionButton)

    # Layout selection combo box
    self.viewSelectorComboBox = qt.QComboBox()
    self.settingsButtonLayout.addRow("Layout: ", self.viewSelectorComboBox)
    self.viewSelectorComboBox.connect("currentIndexChanged(int)",self.onViewChanged)

    #self.registerCustomLayouts()

    # OpenIGTLink connector node selection
    self.linkInputSelector = slicer.qMRMLNodeComboBox()
    self.linkInputSelector.nodeTypes = ("vtkMRMLIGTLConnectorNode", "")
    self.linkInputSelector.selectNodeUponCreation = True
    self.linkInputSelector.addEnabled = False
    self.linkInputSelector.removeEnabled = True
    self.linkInputSelector.noneEnabled = False
    self.linkInputSelector.showHidden = False
    self.linkInputSelector.showChildNodeTypes = False
    self.linkInputSelector.setMRMLScene(slicer.mrmlScene)
    self.linkInputSelector.setToolTip("Select connector node")
    self.settingsButtonLayout.addRow("OpenIGTLink connector: ", self.linkInputSelector)

    self.showFullSlicerInterfaceButton = qt.QPushButton()
    self.showFullSlicerInterfaceButton.setText("Show 3D Slicer user interface")
    self.settingsButtonLayout.addRow(self.showFullSlicerInterfaceButton)

    self.showGuideletFullscreenButton = qt.QPushButton()
    self.showGuideletFullscreenButton.setText("Show Guidelet in full screen")
    self.settingsButtonLayout.addRow(self.showGuideletFullscreenButton)

    self.saveSceneButton = qt.QPushButton()
    self.saveSceneButton.setText("Save Guidelet scene")
    self.settingsButtonLayout.addRow(self.saveSceneButton)

    self.saveDirectoryLineEdit = ctk.ctkPathLineEdit()
    node = self.logic.getParameterNode()
    sceneSaveDirectory = node.GetParameter('SavedScenesDirectory')
    logging.info(sceneSaveDirectory)
    self.saveDirectoryLineEdit.label = sceneSaveDirectory
    self.saveDirectoryLineEdit.currentPath = sceneSaveDirectory
    self.saveDirectoryLineEdit.filters = ctk.ctkPathLineEdit.Dirs
    self.saveDirectoryLineEdit.options = ctk.ctkPathLineEdit.DontUseSheet
    self.saveDirectoryLineEdit.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.saveDirectoryLineEdit.showHistoryButton = False
    self.saveDirectoryLineEdit.setMinimumWidth(100)
    self.saveDirectoryLineEdit.setMaximumWidth(500)

    saveLabel = qt.QLabel()
    saveLabel.setText("Save scene directory:")
    hbox = qt.QHBoxLayout()
    hbox.addWidget(saveLabel)
    hbox.addWidget(self.saveDirectoryLineEdit)
    self.settingsButtonLayout.addRow(hbox)

    self.closeSettingsButton = qt.QPushButton("Close")
    self.closeSettingsButtonBox = qt.QDialogButtonBox()
    self.closeSettingsButtonBox.addButton(self.closeSettingsButton,2)
    self.closeSettingsButton.setMaximumWidth(500)
    self.settingsButtonLayout.addRow(self.closeSettingsButtonBox)
    self.settingsLayout.addLayout(self.settingsButtonLayout)

    self.settingsFrame.setLayout(self.settingsLayout)

    self.setupSettingsConnections()

    self.settingsWidget.show()


  def setupWebcamResliceDriver(self):
    # Setup the volume reslice driver for the webcam.
    self.webcam1RGB = slicer.util.getNode('ImageRGB_ImageRGB')

    layoutManager = slicer.app.layoutManager()
    yellowSlice = layoutManager.sliceWidget('Yellow')
    yellowSliceLogic = yellowSlice.sliceLogic()
    yellowSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(self.webcam1RGB.GetID())

    resliceLogic = slicer.modules.volumereslicedriver.logic()
    if resliceLogic:
      yellowNode = slicer.util.getNode('vtkMRMLSliceNodeYellow')
      yellowNode.SetSliceResolutionMode(slicer.vtkMRMLSliceNode.SliceResolutionMatchVolumes)
      resliceLogic.SetDriverForSlice(self.webcam1RGB.GetID(), yellowNode)
      resliceLogic.SetModeForSlice(6, yellowNode)
      resliceLogic.SetFlipForSlice(False, yellowNode)
      #resliceLogic.SetRotationForSlice(180, yellowNode)
      yellowSliceLogic.FitSliceToAll()

  def setUpWebcamTracking(self):
    logging.debug('setUpWebcamTracking')
    try:
      self.webcam1RGB = slicer.util.getNode('ImageRGB_ImageRGB')

    except slicer.util.MRMLNodeNotFoundException:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam1RGB = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam1RGB.SetName('ImageRGB_ImageRGB')
      self.webcam1RGB.SetSpacing(imageSpacing)
      self.webcam1RGB.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam1RGB)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam1RGB.SetAndObserveDisplayNodeID(displayNode.GetID())

    try:
      self.webcam1DEPTH = slicer.util.getNode('ImageDEPTH_ImageDEPT')

    except slicer.util.MRMLNodeNotFoundException:
    #if not self.webcamReference:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam1DEPTH = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam1DEPTH.SetName('ImageDEPTH_ImageDEPT')
      self.webcam1DEPTH.SetSpacing(imageSpacing)
      self.webcam1DEPTH.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam1DEPTH)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam1DEPTH.SetAndObserveDisplayNodeID(displayNode.GetID())
      self.webcam1DEPTHConnectorNode = self.createRealSensePlusConnectors(1, 18948, 'DEPTH')
      self.webcam1DEPTHConnectorNode.RegisterIncomingMRMLNode(self.webcam1DEPTH)
      self.webcam1DEPTHConnectorNode.Start()

    try:
      self.webcam0RGB = slicer.util.getNode('Image1RGB_Image1RGB')

    except slicer.util.MRMLNodeNotFoundException:
      # if not self.webcamReference:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam0RGB = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam0RGB.SetName('Image1RGB_Image1RGB')
      self.webcam0RGB.SetSpacing(imageSpacing)
      self.webcam0RGB.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam0RGB)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam0RGB.SetAndObserveDisplayNodeID(displayNode.GetID())
      self.webcam0RGBConnectorNode = self.createRealSensePlusConnectors(1, 18949, 'DEPTH')
      self.webcam0RGBConnectorNode.RegisterIncomingMRMLNode(self.webcam0RGB)
      self.webcam0RGBConnectorNode.Start()

    try:
      self.webcam0DEPTH = slicer.util.getNode('Image1DEPTH_Image1DE')

    except slicer.util.MRMLNodeNotFoundException:
      # if not self.webcamReference:
      imageSpacing = [0.2, 0.2, 0.2]
      imageData = vtk.vtkImageData()
      imageData.SetDimensions(640, 480, 1)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder = vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.webcam0DEPTH = slicer.vtkMRMLStreamingVolumeNode()
      self.webcam0DEPTH.SetName('Image1DEPTH_Image1DE')
      self.webcam0DEPTH.SetSpacing(imageSpacing)
      self.webcam0DEPTH.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.webcam0DEPTH)
      displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      self.webcam0DEPTH.SetAndObserveDisplayNodeID(displayNode.GetID())
      self.webcam0DEPTHConnectorNode = self.createRealSensePlusConnectors(1, 18950, 'DEPTH')
      self.webcam0DEPTHConnectorNode.RegisterIncomingMRMLNode(self.webcam0DEPTH)
      self.webcam0DEPTHConnectorNode.Start()
    #self.objectTrackerLogic = ColourObjectTracker.ColourObjectTrackerLogic()
    self.webcamImageVolume = slicer.util.getNode('Image1RGB_Image1RGB')

  def webcamReferenceImageModified(self,caller,eventId):
    self.webcamImage.InvokeEvent(slicer.vtkMRMLVolumeNode.ImageDataModifiedEvent)

  def disconnect(self):#TODO see connect
    logging.debug('ScoliUs.disconnect()')
    Guidelet.disconnect(self)

    self.resultsCollapsibleButton.disconnect('toggled(bool)', self.onResultsPanelToggled)

    # Keyboard shortcuts
    self.startStopShortcutPlus.disconnect('activated()', self.ultrasound.startStopRecordingButton.click )

  def hideTargetFromViews( self ):
    views = slicer.mrmlScene.GetNodesByClass( "vtkMRMLAbstractViewNode" )
    for viewIndex in range( views.GetNumberOfItems() ):
      currentView = views.GetItemAsObject( viewIndex )
      if ( currentView.IsA( 'vtkMRMLSliceNode' ) ): # 2D slice view
        if ( "2D" in self.parameterNode.GetParameter('HideTargetViews')  ):
          self.targetFiducialNode.GetMarkupsDisplayNode().RemoveViewNodeID( currentView.GetID() )
        else:
          self.targetFiducialNode.GetMarkupsDisplayNode().AddViewNodeID( currentView.GetID() )
      if ( currentView.IsA( 'vtkMRMLViewNode' ) ): # 3D slice view
        if ( "3D" in self.parameterNode.GetParameter('HideTargetViews')  ):
          self.targetFiducialNode.GetMarkupsDisplayNode().RemoveViewNodeID( currentView.GetID() )
        else:
          self.targetFiducialNode.GetMarkupsDisplayNode().AddViewNodeID( currentView.GetID() )

  def onPlaceClicked(self, pushed):
    logging.debug('onPlaceClicked')
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    if pushed:
      # activate placement mode
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
      selectionNode.SetActivePlaceNodeID(self.patientSLandmarks_Reference.GetID())
      interactionNode.SetPlaceModePersistence(1)
      interactionNode.SetCurrentInteractionMode(interactionNode.Place)
    else:
      # deactivate placement mode
      interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)

  def onDeleteLastFiducialClicked(self):
    numberOfPoints = self.patientSLandmarks_Reference.GetNumberOfFiducials()
    self.patientSLandmarks_Reference.RemoveMarkup(numberOfPoints-1)
    if numberOfPoints<=1:
        self.deleteLastFiducialButton.setEnabled(False)
        self.deleteAllFiducialsButton.setEnabled(False)
        self.deleteLastFiducialDuringNavigationButton.setEnabled(False)

  def onDeleteAllFiducialsClicked(self):
    self.patientSLandmarks_Reference.RemoveAllMarkups()
    self.deleteLastFiducialButton.setEnabled(False)
    self.deleteAllFiducialsButton.setEnabled(False)
    self.deleteLastFiducialDuringNavigationButton.setEnabled(False)
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetRadius(0.001)
    self.tumorModel_Needle.SetPolyDataConnection(sphereSource.GetOutputPort())
    self.tumorModel_Needle.Modified()

  def addRecordingsTableToUltrasoundPanel(self):
    self.StartRecordingSeekWidget = slicer.qMRMLSequenceBrowserSeekWidget()

  def updateRecordingsTable(self, observer, eventid):
    # Disconnect the cell changed signal to prevent key errors
    self.recordingsTable.disconnect('cellChanged(int, int)', self.updateSequenceBrowserNodeName)

    numberOfNodes = slicer.mrmlScene.GetNumberOfNodesByClass("vtkMRMLSequenceBrowserNode")
    self.recordingsTable.setRowCount(numberOfNodes)
    self.sequenceBrowserNodeDict = {} # Keys are the row number in the table

    # If a change has been made to the scene with a new sequence browser node,
    # update the table, displaying the name of the node as well as a delete button
    # for that node. The connection is handled by the partial function that links
    # a unique removeSequenceBrowserNodeFromScene function with the generated button.
    for nodeNumber in range(numberOfNodes):
      aSequenceBrowserNode = slicer.mrmlScene.GetNthNodeByClass(nodeNumber,"vtkMRMLSequenceBrowserNode")
      recordingsTableItem = qt.QTableWidgetItem(aSequenceBrowserNode.GetName())
      deleteRecordingsTableButton = qt.QPushButton()
      deleteRecordingsTableButton.setIcon( slicer.app.style().standardIcon(qt.QStyle.SP_DialogDiscardButton) )
      deleteRecordingsTableButton.connect('clicked()', partial(self.removeSequenceBrowserNodeFromScene, nodeNumber))

      # Update the dictionary of sequence browser nodes with the new node
      self.sequenceBrowserNodeDict[nodeNumber] = aSequenceBrowserNode

      # Add items to the table
      self.recordingsTable.setItem(nodeNumber, 0, recordingsTableItem)
      self.recordingsTable.setCellWidget(nodeNumber, 1, deleteRecordingsTableButton)

    # Reconnect the cell changed signal
    self.recordingsTable.connect('cellChanged(int, int)', self.updateSequenceBrowserNodeName)

  def updateSequenceBrowserNodeName(self, row, col):
    newName = self.recordingsTable.item(row,col).text()
    self.sequenceBrowserNodeDict[row].SetName(newName)

  def removeSequenceBrowserNodeFromScene(self, row):
    # Get the list of synched sequence nodes from a selected sequence browser node for deletion
    browserNodeToDelete = self.sequenceBrowserNodeDict[row]

    syncedSequenceNodes = vtk.vtkCollection()
    browserNodeToDelete.GetSynchronizedSequenceNodes(syncedSequenceNodes, True)

    virtualOutputNodes = vtk.vtkCollection()
    browserNodeToDelete.GetAllVirtualOutputDataNodes(virtualOutputNodes)

    slicer.mrmlScene.RemoveNode(browserNodeToDelete) # Do this first, otherwise, it will remove all the virtual data nodes from the scene

    # Iterate through the synced sequence nodes to remove both them from the scene
    for nodeIndex in range (syncedSequenceNodes.GetNumberOfItems()):
      syncedSequenceNode = syncedSequenceNodes.GetItemAsObject(nodeIndex)
      slicer.mrmlScene.RemoveNode(syncedSequenceNode)

    # Iterate through the virtual output nodes to remove both them from the scene
    for nodeIndex in range (virtualOutputNodes.GetNumberOfItems()):
      virtualOutputNode = virtualOutputNodes.GetItemAsObject(nodeIndex)
      #slicer.mrmlScene.RemoveNode(virtualOutputNode) # Do not remove from scene, so the transform hierarchy is maintained

  def saveAllRecordings(self):    
    try:
      miLogic = slicer.modules.metafileimporter.logic()
    except:
      logging.debug( "saveAllRecordings: Could not find Metafile Importer logic." )

    savedScenesDirectory = self.parameterNode.GetParameter('SavedScenesDirectory')
    if ( not os.path.exists(savedScenesDirectory) ):
      os.makedirs(savedScenesDirectory) # Make the directory if it doesn't already exist

    logFilename = self.fileName + os.extsep + "csv"
    logFilename = os.path.join(savedScenesDirectory, logFilename)
    self.eventLog.to_csv(logFilename)

    recordingCollection = slicer.mrmlScene.GetNodesByClass( "vtkMRMLSequenceBrowserNode" )
    for nodeNumber in range( recordingCollection.GetNumberOfItems() ):
      browserNode = recordingCollection.GetItemAsObject( nodeNumber )
      filename = self.fileName + os.extsep + "sqbr"
      filename = os.path.join( savedScenesDirectory, filename )
      slicer.util.saveNode(browserNode, filename)
      #miLogic.WriteSequenceMetafile( filename, browserNode )

  def displayImageInSliceViewer(self, imageNodeID, sliceName, flip, rotate):
    # First, find the volume reslice driver logic
    sliceWidget = slicer.app.layoutManager().sliceWidget(sliceName)
    if (sliceWidget is None):
      return

    sliceNode = sliceWidget.sliceView().mrmlSliceNode()
    sliceLogic = sliceWidget.sliceLogic()
    if (sliceNode is None or sliceLogic is None):
      return

    vrdLogic = slicer.modules.volumereslicedriver.logic()
    if (vrdLogic is None):
      logging.error("LumbarTutorLogic::displayImageInSliceViewer could not find Volume Reslice Driver logic.")
      return

    sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(imageNodeID)

    sliceNode.SetSliceResolutionMode(slicer.vtkMRMLSliceNode.SliceResolutionMatchVolumes)

    vrdLogic.SetDriverForSlice(imageNodeID, sliceNode)
    vrdLogic.SetModeForSlice(slicer.vtkSlicerVolumeResliceDriverLogic.MODE_TRANSVERSE, sliceNode)
    vrdLogic.SetFlipForSlice(flip, sliceNode)
    vrdLogic.SetRotationForSlice(rotate, sliceNode)  # 180 degrees

    sliceLogic.FitSliceToAll()

  def addProcedureProgressToUltrasoundPanel(self):
    self.lastNeedleUpdateTimeSec = 0
    self.needleIntersectsUltrasoundPlane = 'No'
    self.needleTipObserver = self.needleToReference.AddObserver(slicer.vtkMRMLLinearTransformNode.TransformModifiedEvent, self.onNeedleMoved)
    self.procedureProgressLabel = qt.QLabel()
    self.procedureProgressLabel.setMinimumSize(200,20)
    self.lastUpdateTimeSec = 0

    self.currentStepLabel = qt.QLabel("")
    self.currentStepLabel.setMinimumSize(470, 60)

    self.setupStepsLayouts()

    # create scroll area for the step check boxes
    self.procedureProgressArea = qt.QScrollArea()
    self.procedureProgressArea.setWidget(self.StepsAreaGroup)
    self.procedureProgressArea.setWidgetResizable(True)
    self.procedureProgressLayout = qt.QVBoxLayout()
    self.procedureProgressLayout.setContentsMargins(12, 4, 4, 4)
    self.procedureProgressLayout.setSpacing(4)
    self.spacerLabel = qt.QLabel()

    self.procedureProgressLayout.addWidget(self.procedureProgressArea)
    #self.procedureProgressLayout.setSizeConstraint(1)

    self.resetCameraPositionButton = qt.QPushButton('Reset 3D View')
    self.resetCameraPositionButton.connect('clicked(bool)', self.onResetCameraPosition)
    self.resetCameraPositionButton.toolTip = "Reset the 3D viewer's camera position"
    self.ultrasoundLayout.addRow(self.resetCameraPositionButton)

    self.difficultyLabel = qt.QLabel("Difficulty ")
    self.beginnerCheckBox = qt.QPushButton("\tLevel 1")
    self.intermediateCheckBox = qt.QPushButton("\tLevel 2")
    self.advancedCheckBox = qt.QPushButton("\tLevel 3")

    self.difficultyLevelCheckBoxes = qt.QButtonGroup()
    self.difficultyLevelCheckBoxes.addButton(self.beginnerCheckBox)
    self.difficultyLevelCheckBoxes.addButton(self.intermediateCheckBox)
    self.difficultyLevelCheckBoxes.addButton(self.advancedCheckBox)
    self.difficultyLevelCheckBoxes.setExclusive(True)

    hbox = qt.QHBoxLayout()
    hbox.addWidget(self.difficultyLabel)
    hbox.addWidget(self.beginnerCheckBox)
    hbox.addWidget(self.intermediateCheckBox)
    hbox.addWidget(self.advancedCheckBox)
    hbox.setContentsMargins(12,4,4,4)
    self.ultrasoundLayout.addRow(hbox)


    self.beginnerCheckBox.connect('clicked(bool)', self.onBeginnerSelected)
    self.intermediateCheckBox.connect('clicked(bool)', self.onIntermediateSelected)
    self.advancedCheckBox.connect('clicked(bool)', self.onAdvancedSelected)


    self.vesselFidPosition = [0, 0, 0]

    self.ultrasoundLayout.addWidget(self.spacerLabel)
    self.ultrasoundLayout.addWidget(self.procedureProgressLabel)
    self.ultrasoundLayout.addWidget(self.currentStepLabel)
    self.procedureLayout.addLayout(self.procedureProgressLayout)

    self.hideAllSteps()
    self.currentStepLabel.visible = False
    self.procedureProgressLabel.visible = False
    self.procedureProgressArea.visible = False

    self.setUpWebcamTracking()

  def onResetCameraPosition(self):
    camerasLogic = slicer.modules.cameras.logic()
    firstCameraNode = camerasLogic.GetViewActiveCameraNode(self.firstViewNode)
    camera = firstCameraNode.GetCamera()

    camera.SetPosition(0.0, 800, 1400.0)  # 120 cm behind and 10 cm below neck
    camera.SetFocalPoint(0.0, 0.0, 0.0)
    camera.SetViewUp(0.0, 0.0, 1.0)  # Head up, looking towards A
    camera.SetRoll(0)  # Default in Slicer

  def setupStepsLayouts(self):
    degreeSymbol = u'\N{DEGREE SIGN}'
    # Create check box for each step
    #self.sterileGelCheckBox = qt.QCheckBox("\tApply sterile gel to ultrasound probe")
    self.scanVesselCrossSectionCheckBox = qt.QCheckBox("\tScan vessel cross section")
    self.identifyTargetVesselCheckBox = qt.QCheckBox("\tIdentify the target vessel\n\t\t\t\tin ultrasound image")
    self.identifyTargetVesselCheckBox.setMinimumSize(200, 60)

    self.identifyVesselCheckBox = qt.QCheckBox("\tIdentify vessel")

    #self.putDownUSProbeCheckBox = qt.QCheckBox("\tPut down ultrasound probe")
    self.applyLocalAnestheticCheckBox = qt.QCheckBox("\tApply local anesthetic")

    self.AnestheticCheckBox = qt.QCheckBox("\tAnesthetic")

    #self.scanVesselCrossSection2CheckBox = qt.QCheckBox("\tScan vessel cross section")
    self.insertNeedleCheckBox = qt.QCheckBox("\tInsert needle into vessel at 45" + degreeSymbol + " angle")

    self.NeedleCheckBox = qt.QCheckBox("\tNeedle in vessel")

    self.removeSyringeFromNeedleCheckBox = qt.QCheckBox("\tRemove syringe from needle")
    self.insertGuidewireCheckBox = qt.QCheckBox("\tInsert guidewire")

    self.GuidewireCheckBox = qt.QCheckBox("\tGuidewire")

    self.ScalpelCheckBox = qt.QCheckBox("\tScalpel")

    self.ScanVesselCrossSection3CheckBox = qt.QCheckBox("\tScan vessel cross section")
    self.ScanVesselLongAxisCheckBox = qt.QCheckBox("\tScan vessel long axis,\n\t\t\t\tEnsure guidewire is in vein")

    self.ScanVesselLongAxisCheckBox.setMinimumSize(200, 60)
    self.RemoveNeedleCheckBox = qt.QCheckBox("\tRemove the needle,\n\t\t\t\tleave guidewire in place")
    self.RemoveNeedleCheckBox.setMinimumSize(200, 60)
    self.makeIncisionCheckBox = qt.QCheckBox("\tMake small incision using scalpel")
    self.threadDilatorCheckBox = qt.QCheckBox("\tThread dilator over guidewire")
    self.removeDilatorCheckBox = qt.QCheckBox("\tRemove dilator")

    self.DilatorCheckBox = qt.QCheckBox("\tDilator")

    self.threadCatheterCheckBox = qt.QCheckBox("\tThread catheter over guidewire")

    self.CatheterCheckBox = qt.QCheckBox("\tCatheter")

    self.removeGuidewireCheckBox = qt.QCheckBox("\tRemove the guidewire (Show to camera)")



    # add check box for each step to the layout
    self.StepsLayout = qt.QFormLayout()
    #self.StepsLayout.addWidget(self.sterileGelCheckBox)
    self.StepsLayout.addWidget(self.scanVesselCrossSectionCheckBox)
    self.StepsLayout.addWidget(self.identifyTargetVesselCheckBox)
    self.StepsLayout.addWidget(self.identifyVesselCheckBox)
    self.StepsLayout.addWidget(self.applyLocalAnestheticCheckBox)
    self.StepsLayout.addWidget(self.AnestheticCheckBox)
    self.StepsLayout.addWidget(self.insertNeedleCheckBox)
    self.StepsLayout.addWidget(self.NeedleCheckBox)
    self.StepsLayout.addWidget(self.removeSyringeFromNeedleCheckBox)
    self.StepsLayout.addWidget(self.insertGuidewireCheckBox)
    self.StepsLayout.addWidget(self.GuidewireCheckBox)
    self.StepsLayout.addWidget(self.ScalpelCheckBox)
    self.StepsLayout.addWidget(self.RemoveNeedleCheckBox)
    self.StepsLayout.addWidget(self.ScanVesselCrossSection3CheckBox)
    self.StepsLayout.addWidget(self.ScanVesselLongAxisCheckBox)
    self.StepsLayout.addWidget(self.makeIncisionCheckBox)
    self.StepsLayout.addWidget(self.threadDilatorCheckBox)
    self.StepsLayout.addWidget(self.DilatorCheckBox)
    self.StepsLayout.addWidget(self.removeDilatorCheckBox)
    self.StepsLayout.addWidget(self.threadCatheterCheckBox)
    self.StepsLayout.addWidget(self.CatheterCheckBox)
    self.StepsLayout.addWidget(self.removeGuidewireCheckBox)

    self.StepsAreaGroup = qt.QFrame()
    self.StepsAreaGroup.setMinimumSize(430, 1000)

    self.StepsAreaGroup.setLayout(self.StepsLayout)
    self.procedureProgressLabel.setText("Current step:")
    self.setupStepConnections()


  def setupStepConnections(self):
    self.Steps = self.StepsAreaGroup.findChildren('QCheckBox')
    self.currentStepLabel.setText(self.Steps[0].text + '\n')
    for i in range(0, len(self.Steps)):
      self.Steps[i].connect('stateChanged(int)', self.onStepCompleted)

  def hideBeginnerSteps(self):
    self.identifyVesselCheckBox.visible = True
    self.AnestheticCheckBox.visible = True
    self.NeedleCheckBox.visible = True
    self.GuidewireCheckBox.visible = True
    self.ScalpelCheckBox.visible = True
    self.DilatorCheckBox.visible = True
    self.CatheterCheckBox.visible = True

    #self.sterileGelCheckBox.visible = False
    self.scanVesselCrossSectionCheckBox.visible = False
    self.identifyTargetVesselCheckBox.visible = False
    self.applyLocalAnestheticCheckBox.visible = False
    self.insertNeedleCheckBox.visible = False
    self.removeSyringeFromNeedleCheckBox.visible = False
    self.insertGuidewireCheckBox.visible = False
    self.RemoveNeedleCheckBox.visible = False
    self.ScanVesselCrossSection3CheckBox.visible = False
    self.ScanVesselLongAxisCheckBox.visible = False
    self.makeIncisionCheckBox.visible = False
    self.threadDilatorCheckBox.visible = False
    self.removeDilatorCheckBox.visible = False
    self.threadCatheterCheckBox.visible = False
    self.removeGuidewireCheckBox.visible = False

  def hideIntermediateSteps(self):
    self.identifyVesselCheckBox.visible = False
    self.AnestheticCheckBox.visible = False
    self.NeedleCheckBox.visible = False
    self.GuidewireCheckBox.visible = False
    self.ScalpelCheckBox.visible = False
    self.DilatorCheckBox.visible = False
    self.CatheterCheckBox.visible = False

    #self.sterileGelCheckBox.visible = True
    self.scanVesselCrossSectionCheckBox.visible = True
    self.identifyTargetVesselCheckBox.visible = True
    self.applyLocalAnestheticCheckBox.visible = True
    self.insertNeedleCheckBox.visible = True
    self.removeSyringeFromNeedleCheckBox.visible = True
    self.insertGuidewireCheckBox.visible = True
    self.RemoveNeedleCheckBox.visible = True
    self.ScanVesselCrossSection3CheckBox.visible = True
    self.ScanVesselLongAxisCheckBox.visible = True
    self.makeIncisionCheckBox.visible = True
    self.threadDilatorCheckBox.visible = True
    self.removeDilatorCheckBox.visible = True
    self.threadCatheterCheckBox.visible = True
    self.removeGuidewireCheckBox.visible = True

  def hideAllSteps(self):
    self.identifyVesselCheckBox.visible = False
    self.AnestheticCheckBox.visible = False
    self.NeedleCheckBox.visible = False
    self.GuidewireCheckBox.visible = False
    self.ScalpelCheckBox.visible = False
    self.DilatorCheckBox.visible = False
    self.CatheterCheckBox.visible = False

    #self.sterileGelCheckBox.visible = False
    self.scanVesselCrossSectionCheckBox.visible = False
    self.identifyTargetVesselCheckBox.visible = False
    self.applyLocalAnestheticCheckBox.visible = False
    self.insertNeedleCheckBox.visible = False
    self.removeSyringeFromNeedleCheckBox.visible = False
    self.insertGuidewireCheckBox.visible = False
    self.RemoveNeedleCheckBox.visible = False
    self.ScanVesselCrossSection3CheckBox.visible = False
    self.ScanVesselLongAxisCheckBox.visible = False
    self.makeIncisionCheckBox.visible = False
    self.threadDilatorCheckBox.visible = False
    self.removeDilatorCheckBox.visible = False
    self.threadCatheterCheckBox.visible = False
    self.removeGuidewireCheckBox.visible = False

  def onBeginnerSelected(self):
    self.navigationView = self.VIEW_ULTRASOUND_CAM_3D
    self.updateNavigationView()

    self.hideIntermediateSteps()

    self.currentStepLabel.visible = True
    self.procedureProgressLabel.visible = True
    self.procedureProgressArea.visible = True

    '''self.vesselModel.GetDisplayNode().SetColor(0, 0, 1)
    self.vesselModel.GetDisplayNode().SliceIntersectionVisibilityOn()
    self.vesselModel.GetDisplayNode().VisibilityOn()

    self.carotidModel.GetDisplayNode().SetColor(1, 0, 0)
    self.carotidModel.GetDisplayNode().SliceIntersectionVisibilityOn()
    self.carotidModel.GetDisplayNode().VisibilityOn()

    self.skinModel.GetDisplayNode().VisibilityOn()'''


  def onIntermediateSelected(self):
    self.navigationView = self.VIEW_ULTRASOUND_CAM_3D
    self.updateNavigationView()

    self.hideBeginnerSteps()

    self.currentStepLabel.visible = False
    self.procedureProgressLabel.visible = False
    self.procedureProgressArea.visible = True

    '''self.vesselModel.GetDisplayNode().SetColor(0.2, 0.2, 0.2)
    self.vesselModel.GetDisplayNode().SliceIntersectionVisibilityOff()
    self.vesselModel.GetDisplayNode().VisibilityOff()

    self.carotidModel.GetDisplayNode().SetColor(0.2, 0.2, 0.2)
    self.carotidModel.GetDisplayNode().SliceIntersectionVisibilityOff()
    self.carotidModel.GetDisplayNode().VisibilityOff()

    self.skinModel.GetDisplayNode().VisibilityOff()'''

  def onAdvancedSelected(self):
    self.navigationView = self.VIEW_ULTRASOUND
    self.updateNavigationView()

    self.hideAllSteps()

    self.currentStepLabel.visible = False
    self.procedureProgressLabel.visible = False
    self.procedureProgressArea.visible = False

  
  def onNewTrainingSession(self):
    logging.info('new training session started')
    for step in self.Steps:
        step.checked = False
        step.setStyleSheet("background-color:beige")
    self.procedureProgressArea.ensureWidgetVisible(self.Steps[0], 0, 5)
    self.removeAllObservers()
    self.hideAllSteps()
    self.currentStepLabel.visible = False
    self.procedureProgressLabel.visible = False
    self.procedureProgressArea.visible = False

  def findCornersOfUSImage(self):
    self.redSliceBounds = [0, 0, 0, 0, 0, 0]
    self.redSliceLogic.GetSliceBounds(self.redSliceBounds)
    SliceToRAS = slicer.util.getNode('vtkMRMLSliceNodeRed').GetSliceToRAS()
    # TODO find better names for the corners of the US image
    self.usImageCorner1 = [self.redSliceBounds[0], self.redSliceBounds[2], self.redSliceBounds[4], 0]
    self.usImageCorner1 = SliceToRAS.MultiplyFloatPoint(self.usImageCorner1)
    self.usImageCorner2 = [self.redSliceBounds[0], self.redSliceBounds[3], self.redSliceBounds[4], 0]
    self.usImageCorner2 = SliceToRAS.MultiplyFloatPoint(self.usImageCorner2)
    self.usImageCorner3 = [self.redSliceBounds[1], self.redSliceBounds[2], self.redSliceBounds[4], 0]
    self.usImageCorner3 = SliceToRAS.MultiplyFloatPoint(self.usImageCorner3)
    self.usImageCorner4 = [self.redSliceBounds[1], self.redSliceBounds[3], self.redSliceBounds[4], 0]
    self.usImageCorner4 = SliceToRAS.MultiplyFloatPoint(self.usImageCorner4)
    self.redSliceBounds[0] = min(self.usImageCorner1[0], self.usImageCorner2[0], self.usImageCorner3[0], self.usImageCorner4[0])
    self.redSliceBounds[1] = max(self.usImageCorner1[0], self.usImageCorner2[0], self.usImageCorner3[0], self.usImageCorner4[0])
    self.redSliceBounds[2] = min(self.usImageCorner1[1], self.usImageCorner2[1], self.usImageCorner3[1], self.usImageCorner4[1])
    self.redSliceBounds[3] = max(self.usImageCorner1[1], self.usImageCorner2[1], self.usImageCorner3[1], self.usImageCorner4[1])
    self.redSliceBounds[4] = min(self.usImageCorner1[2], self.usImageCorner2[2], self.usImageCorner3[2], self.usImageCorner4[2])
    self.redSliceBounds[5] = max(self.usImageCorner1[2], self.usImageCorner2[2], self.usImageCorner3[2], self.usImageCorner4[2])

  def findNeedleUsPlaneAngle(self):
    import math
    self.redSliceBounds = [0, 0, 0, 0, 0, 0]
    ImageNormal_Slice = [0, 0, 1, 0]
    ImagePlane_Slice = [1, 0, 0, 0]
    SliceToRAS = slicer.util.getNode('vtkMRMLSliceNodeRed').GetSliceToRAS()
    ImageNormal_RAS = SliceToRAS.MultiplyFloatPoint(ImageNormal_Slice)
    ImagePlane_RAS = SliceToRAS.MultiplyFloatPoint(ImagePlane_Slice)
    ImagePlane_RAS = ImagePlane_RAS/numpy.linalg.norm(ImagePlane_RAS)
    self.needleTipToWorldMatrix = vtk.vtkMatrix4x4()
    self.needleTipToNeedle.GetMatrixTransformToWorld(self.needleTipToWorldMatrix)
    needleTip_Needle = [0, 0, 0, 1]
    self.needleTip_RAS = self.needleTipToWorldMatrix.MultiplyFloatPoint(needleTip_Needle)
    self.needleTip_RAS = numpy.array(self.needleTip_RAS)
    secondNeedlePoint_Needle = [1, 0, 0, 1]
    secondNeedlePoint_RAS = self.needleTipToWorldMatrix.MultiplyFloatPoint(secondNeedlePoint_Needle)
    secondNeedlePoint_RAS = numpy.array(secondNeedlePoint_RAS)
    needleVector_RAS = secondNeedlePoint_RAS - self.needleTip_RAS
    needleVector_RAS = needleVector_RAS/numpy.linalg.norm(needleVector_RAS)
    usPlaneNeedleAngle = (numpy.arccos(numpy.dot(ImagePlane_RAS, needleVector_RAS)))
    usPlaneNeedleAngle = usPlaneNeedleAngle *180 / math.pi
    return usPlaneNeedleAngle

  def updateCheckBoxes(self,beginnerCheckBox,intermediateCheckBox):
    if beginnerCheckBox.styleSheet.find("background-color:red") != -1:
      beginnerCheckBox.setStyleSheet("background-color:yellow")
      intermediateCheckBox.setStyleSheet("background-color:yellow")
    beginnerCheckBox.checked = True
    intermediateCheckBox.checked = True

  def onStepCompleted(self):
    numSteps = len(self.Steps)
    currentStep = self.Steps[0].text
    i=0
    while i < numSteps and self.Steps[i].checked == True:
        isYellow = self.Steps[i].styleSheet.find("background-color:yellow")
        if isYellow == -1:
            self.Steps[i].setStyleSheet("background-color:#00ff2b")
        if i < numSteps - 1:
            currentStep = self.Steps[i + 1].text
            currentStep = currentStep.replace("\t\t\t","")
            if self.Steps[i+1].visible == True:
               self.procedureProgressArea.ensureWidgetVisible(self.Steps[i+1], 0, 5)

        i+=1

    #check for missed steps
    for j in range(i,numSteps):
      if self.Steps[j].checked == True:
        self.Steps[j].setStyleSheet("background-color:#00ff2b") #completed steps coloured green
        for k in range(i,j):
          if self.Steps[k].checked == False:
            self.Steps[k].setStyleSheet("background-color:red") #missed steps coloured red
        if j < numSteps - 1:
            currentStep = self.Steps[j + 1].text
            currentStep = currentStep.replace("\t\t\t", "")
            if self.Steps[j+1].visible:
               self.procedureProgressArea.ensureWidgetVisible(self.Steps[j + 1], 0, 20) #ensure that next step is visible
        i=j
    if self.Steps[numSteps-1].checked == True:
      currentStep = '\tProcedure complete!'
    self.currentStepLabel.setText(currentStep)

  def onNeedleMoved(self, caller, eventID):
    self.needleTipToWorldMatrix = vtk.vtkMatrix4x4()
    self.needleTipToNeedle.GetMatrixTransformToWorld(self.needleTipToWorldMatrix)
    pImageSlice = [0, 0, 0, 1]
    nImageSlice = [0, 0, 1, 0]
    SliceToRAS = slicer.util.getNode('vtkMRMLSliceNodeRed').GetSliceToRAS()
    pImageRAS = SliceToRAS.MultiplyFloatPoint(pImageSlice)
    pImageRASList = [pImageRAS[0], pImageRAS[1], pImageRAS[2]]
    nImageRAS = SliceToRAS.MultiplyFloatPoint(nImageSlice)
    nImageRASList = [nImageRAS[0], nImageRAS[1], nImageRAS[2]]
    pPatientRAS = [self.needleTipToWorldMatrix.GetElement(0, 3), self.needleTipToWorldMatrix.GetElement(1, 3),
                   self.needleTipToWorldMatrix.GetElement(2, 3)]
    #xminusp = map(operator.sub, pPatientRAS, pImageRASList[0:3])
    xminusp = numpy.array(pPatientRAS) - numpy.array(pImageRASList[0:3])
    distance = numpy.dot(xminusp, nImageRAS[0:3])
    if (distance < 0.2):
      self.needleIntersectsUltrasoundPlane = 'Yes'
      #self.insertNeedleCheckBox.setChecked(True)
    else:
      self.needleIntersectsUltrasoundPlane = 'No'

  def setupResultsPanel(self):
    logging.debug('setupResultsPanel')

    self.sliderTranslationDefaultMm = 0
    self.sliderTranslationMinMm     = -500
    self.sliderTranslationMaxMm     = 500
    self.sliderViewAngleDefaultDeg  = 30
    self.cameraViewAngleMinDeg      = 5.0  # maximum magnification
    self.cameraViewAngleMaxDeg      = 150.0 # minimum magnification

    self.sliderSingleStepValue = 1
    self.sliderPageStepValue   = 10

    self.resultsCollapsibleButton.setProperty('collapsedHeight', 20)
    self.resultsCollapsibleButton.text = "Results"
    self.sliceletPanelLayout.addWidget(self.resultsCollapsibleButton)

    self.resultsCollapsibleLayout = qt.QVBoxLayout(self.resultsCollapsibleButton)
    self.resultsCollapsibleLayout.setContentsMargins(12, 4, 4, 4)
    self.resultsCollapsibleLayout.setSpacing(4)

    self.resultsControlsLayout = qt.QFormLayout(self.resultsCollapsibleButton)
    self.resultsCollapsibleLayout.addLayout(self.resultsControlsLayout)

    self.recordingComboBox = slicer.qMRMLNodeComboBox()
    self.recordingComboBox.nodeTypes = ["vtkMRMLSequenceBrowserNode"]
    self.recordingComboBox.removeEnabled = False
    self.recordingComboBox.addEnabled = False
    self.recordingComboBox.renameEnabled = False
    self.recordingComboBox.setMRMLScene(slicer.mrmlScene)
    self.resultsControlsLayout.addRow("Select recording: ",self.recordingComboBox)
    self.recordingComboBox.connect('currentNodeChanged(bool)',self.onRecordingNodeSelected)

    self.recordingPlayWidget = slicer.qMRMLSequenceBrowserPlayWidget()
    self.resultsControlsLayout.addRow(self.recordingPlayWidget)

    self.recordingSeekWidget = slicer.qMRMLSequenceBrowserSeekWidget()
    self.resultsControlsLayout.addRow(self.recordingSeekWidget)

    self.calculateMetricsButton = qt.QPushButton("Calculate metrics")
    self.resultsControlsLayout.addRow(self.calculateMetricsButton)
    self.calculateMetricsButton.connect('clicked(bool)', self.onCalculateMetricsButtonClicked)

    self.metricsTableWidget = slicer.qSlicerMetricsTableWidget()
    self.metricsTableWidget.setMRMLScene(slicer.mrmlScene)
    self.metricsTableWidget.setMetricsTableSelectionRowVisible( False )
    self.metricsTableWidget.setExpandHeightToContents(False)

    self.viewFeedbackButton = qt.QPushButton("View Feedback")
    self.viewFeedbackButton.connect('clicked(bool)', self.onViewFeedbackClicked)
    self.createFeedbackWidget()

    self.resultsCollapsibleLayout.addWidget(qt.QLabel()) # Blank row for spacing between table and buttons.
    self.resultsCollapsibleLayout.addWidget(self.metricsTableWidget)
    self.resultsCollapsibleLayout.addWidget(qt.QLabel()) # Blank row for spacing between table and buttons.
    self.resultsCollapsibleLayout.addWidget(self.viewFeedbackButton)
    self.resultsCollapsibleLayout.addWidget(qt.QLabel()) # Blank row for spacing between table and buttons.


  def onViewFeedbackClicked(self):
    missedSteps = self.findMissedSteps()
    completedSteps = self.findCompletedSteps()
    incorrectSteps = self.findIncorrectSteps()
    numStepsOutOfOrder = self.findNumStepsOutOfOrder()
    self.generateFeedBackReport(missedSteps, incorrectSteps, numStepsOutOfOrder, completedSteps)
    self.feedbackWidget.show()

  def findMissedSteps(self):
    return

  def findCompletedSteps(self):
    return

  def findIncorrectSteps(self):
    return

  def findNumStepsOutOfOrder(self):
    return

  def generateFeedBackReport(self,missed,incorrect,numOutOfOrder,correct):
    return

  def createFeedbackWidget(self):
    self.feedbackWidget = qt.QDialog()
    self.feedbackWidget.setModal(True)
    self.feedbackFrame = qt.QFrame(self.feedbackWidget)
    self.feedbackFrame.setFrameStyle(0x0006)
    self.feedbackWidget.setWindowTitle('Procedure Feedback')
    #self.feedbackWidget.setWindowIcon(qt.QIcon(settingsIconPath))
    self.feedbackPopupGeometry = qt.QRect()
    mainWindow = slicer.util.mainWindow()
    if mainWindow:
      mainWindowGeometry = mainWindow.geometry
      self.feedbackWindowWidth = mainWindow.width * 0.60
      self.feedbackWindowHeight = mainWindow.height * 0.60
      self.feedbackPopupGeometry.setWidth(self.feedbackWindowWidth)
      self.feedbackPopupGeometry.setHeight(self.feedbackWindowHeight)
      self.popupPositioned = False
      self.feedbackWidget.setGeometry(self.feedbackPopupGeometry)
      self.feedbackFrame.setGeometry(self.feedbackPopupGeometry)
      self.feedbackWidget.move(mainWindow.width / 4.0 , mainWindow.height / 4 )

  def onRecordingNodeSelected(self):
    selectedNode = self.recordingComboBox.currentNode()
    self.stopSequenceBrowserPlayback()
    self.setPlaybackRealtime(selectedNode)
    self.recordingPlayWidget.setMRMLSequenceBrowserNode(selectedNode)
    self.recordingSeekWidget.setMRMLSequenceBrowserNode(selectedNode)
    self.setActiveVolumeFromSelection()

  def sequenceBrowserToTransformBuffer(self, sequenceBrowserNode, transformBufferNode, renameDict ):
    if ( sequenceBrowserNode is None or transformBufferNode is None ):
      return
    transformBufferNode.Clear()

    syncedSequenceNodes = vtk.vtkCollection()
    sequenceBrowserNode.GetSynchronizedSequenceNodes( syncedSequenceNodes, True )

    for i in range( syncedSequenceNodes.GetNumberOfItems() ):
      currSyncedSequenceNode = syncedSequenceNodes.GetItemAsObject( i )
      if ( currSyncedSequenceNode.GetNthDataNode( 0 ) is None ):
        return

      if ( ( not currSyncedSequenceNode.GetNthDataNode( 0 ).IsA( "vtkMRMLTransformNode" ) and not currSyncedSequenceNode.GetNthDataNode( 0 ).IsA( "vtkMRMLVolumeNode" ) )
        or currSyncedSequenceNode.GetIndexType() != slicer.vtkMRMLSequenceNode.NumericIndex ):
        continue

      deviceName = currSyncedSequenceNode.GetName()
      for key in renameDict:
        if ( key in currSyncedSequenceNode.GetName() ):
          deviceName = renameDict[ key ]
          # Implicit assumption that the sequence name only contains one key
          # Otherwise, it will just use the last key

      for j in range( currSyncedSequenceNode.GetNumberOfDataNodes() ):
        currDataNode = currSyncedSequenceNode.GetNthDataNode( j )
        currMatrix = vtk.vtkMatrix4x4()
        try:
          currTime = float( currSyncedSequenceNode.GetNthIndexValue( j ) )
        except:
          continue

        if ( currDataNode.IsA( "vtkMRMLTransformNode" ) ):
          currDataNode.GetMatrixTransformToParent( currMatrix )
        elif ( currDataNode.IsA( "vtkMRMLVolumeNode" ) ):
          currDataNode.GetIJKToRASMatrix( currMatrix )

        currTransformRecord = slicer.vtkTransformRecord()
        currTransformRecord.SetTransformMatrix( currMatrix )
        currTransformRecord.SetDeviceName( deviceName )
        currTransformRecord.SetTime( currTime )

        transformBufferNode.AddTransform( currTransformRecord )

    try:
      trLogic = slicer.modules.transformrecorder.logic()
      trLogic.ObserveAllRecordedTransforms( transformBufferNode )
    except:
      logging.debug( "SequenceBroswerToTransformBuffer: Could not find Transform Recorder logic." )

  def setupMetrics(self, metricsDirectory):
    # Import all of the metric scripts and create the metric instances
    peLogic = slicer.modules.perkevaluator.logic()
    if (peLogic is None):
      logging.error("UsNeedleTutorLogic::setupMetrics could not find Perk Evaluator logic.")
      return

    self.perkEvaluatorNode = slicer.vtkMRMLPerkEvaluatorNode()
    self.perkEvaluatorNode.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(self.perkEvaluatorNode)

    self.metricsTableNode = slicer.vtkMRMLTableNode()
    self.metricsTableNode.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(self.metricsTableNode)

    self.perkEvaluatorNode.SetMetricsTableID(self.metricsTableNode.GetID())
    self.metricsTableWidget.setMetricsTableNode(self.metricsTableNode)

    # These metrics are all shared
    # No need to create an instance - an instance is already created automatically
    # TODO: This behaviour may be changed. Metrics will eventually be non-shared by default.

    # Remove all pervasive metric instances and just recreate the ones for the relevant transforms
    metricInstanceNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMetricInstanceNode")
    for i in range(metricInstanceNodes.GetNumberOfItems()):
      node = metricInstanceNodes.GetItemAsObject(i)
      needleTipRole = node.GetRoleID("Any",
                                     slicer.vtkMRMLMetricInstanceNode.TransformRole) == self.needleTipToNeedle.GetID()
      probeRole = node.GetRoleID("Any", slicer.vtkMRMLMetricInstanceNode.TransformRole) == self.probeToReference.GetID()
      if (not needleTipRole and not probeRole):
        self.perkEvaluatorNode.RemoveMetricInstanceID(node.GetID())

    # Generic needle-plane distance/angle computation
    __, needlePlaneDistanceAngleScript = slicer.util.loadNodeFromFile(
      os.path.join(metricsDirectory, "NeedlePlaneDistanceAngle.py"), "Python Metric Script", {}, True)

    # Generic in-action computation
    __, inActionScript = slicer.util.loadNodeFromFile(os.path.join(metricsDirectory, "InAction.py"),
                                                      "Python Metric Script", {}, True)

    # Max/average needle-tip to ultrasound plane distance/angle
    __, maximumNeedlePlaneDistanceScript = slicer.util.loadNodeFromFile(
      os.path.join(metricsDirectory, "MaximumNeedlePlaneDistance.py"), "Python Metric Script", {}, True)
    __, averageNeedlePlaneDistanceScript = slicer.util.loadNodeFromFile(
      os.path.join(metricsDirectory, "AverageNeedlePlaneDistance.py"), "Python Metric Script", {}, True)
    __, maximumNeedlePlaneAngleScript = slicer.util.loadNodeFromFile(
      os.path.join(metricsDirectory, "MaximumNeedlePlaneAngle.py"), "Python Metric Script", {}, True)
    __, averageNeedlePlaneAngleScript = slicer.util.loadNodeFromFile(
      os.path.join(metricsDirectory, "AverageNeedlePlaneAngle.py"), "Python Metric Script", {}, True)

    # Distance to target
    __, distanceFromTargetScript = slicer.util.loadNodeFromFile(os.path.join(metricsDirectory, "DistanceFromTarget.py"),
                                                                "Python Metric Script", {}, True)

    # Everything should be OK with the same roles
    peLogic.SetMetricInstancesRolesToID(self.perkEvaluatorNode, self.needleTipToNeedle.GetID(), "Needle",
                                        slicer.vtkMRMLMetricInstanceNode.TransformRole)
    peLogic.SetMetricInstancesRolesToID(self.perkEvaluatorNode, self.imageToProbe.GetID(), "Ultrasound",
                                        slicer.vtkMRMLMetricInstanceNode.TransformRole)
    peLogic.SetMetricInstancesRolesToID(self.perkEvaluatorNode, self.metricsTableNode.GetID(), "Parameter",
                                        slicer.vtkMRMLMetricInstanceNode.AnatomyRole)
    peLogic.SetMetricInstancesRolesToID(self.perkEvaluatorNode, self.targetFiducialNode.GetID(), "Target",
                                        slicer.vtkMRMLMetricInstanceNode.AnatomyRole)
  def onCalculateMetricsButtonClicked(self):
    selectedSequenceBrowserNode = self.recordingComboBox.currentNode()
    self.perkEvaluatorNode.SetTrackedSequenceBrowserNodeID(selectedSequenceBrowserNode.GetID())

    peLogic = slicer.modules.perkevaluator.logic()
    if (peLogic is None):
      logging.error("UsNeedleTutorLogic::onCalculateMetricsButtonClicked could not find Perk Evaluator logic.")
      return

    peLogic.ComputeMetrics(self.perkEvaluatorNode)

  def onUltrasoundPanelToggled(self, toggled):
    logging.debug('onUltrasoundPanelToggled: {0}'.format(toggled))
    self.navigationView = self.parameterNode.GetParameter( "ProcedureLayout" )
    self.updateNavigationView()

    # The user may want to freeze the image (disconnect) to make contouring easier.
    # Disable automatic ultrasound image auto-fit when the user unfreezes (connect)
    # to avoid zooming out of the image.
    self.fitUltrasoundImageToViewOnConnect = not toggled

  def getCamera(self, viewName):
    """
    Get camera for the selected 3D view
    """
    camerasLogic = slicer.modules.cameras.logic()
    camera = camerasLogic.GetViewActiveCameraNode(slicer.util.getNode(viewName))
    return camera

  def getViewNode(self, viewName):
    """
    Get the view node for the selected 3D view
    """
    viewNode = slicer.util.getNode(viewName)
    return viewNode

  def updateNavigationView(self):
    if ( not self.navigationView == '' ): # Check first if the string is empty
      self.selectView(self.navigationView) # This automatically sets the view to ultrasound only if the string is empty. Here, we want it to do nothing.

    # Reset orientation marker
    if hasattr(slicer.vtkMRMLViewNode(),'SetOrientationMarkerType'): # orientation marker is not available in older Slicer versions
      v1=slicer.util.getNode('View1')
      v1.SetOrientationMarkerType(v1.OrientationMarkerTypeNone)


  def stopSequenceBrowserPlayback(self):
    sequenceBrowserNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSequenceBrowserNode")
    for i in range( sequenceBrowserNodes.GetNumberOfItems() ):
      currSequenceBrowserNode = sequenceBrowserNodes.GetItemAsObject( i )
      currSequenceBrowserNode.SetPlaybackActive(False)
      self.setPlaybackRealtime(currSequenceBrowserNode)

  def onResultsPanelToggled(self, toggled):
    logging.debug('onResultsPanelToggled: {0}'.format(toggled))
    self.navigationView = self.parameterNode.GetParameter( "ResultsLayout" )
    self.updateNavigationView()

    if ( self.ultrasound.startStopRecordingButton.checked ):
      self.ultrasound.startStopRecordingButton.click() # Simulate the user clicking the stop button before the panel is toggled
      # This will stop all the recording etc.

    # Also stop the playback
    self.stopSequenceBrowserPlayback()
    try:
      if ( self.connectorNode is None ):
        return
    except AttributeError:
      return

    try:
      if self.webcamConnectorNode is None:
        return
    except AttributeError:
      return

    # If we are in the "Results" panel, stop the connection so we can replay
    if ( toggled ):
      self.connectorNode.Stop()
      self.webcamConnectorNode.Stop()
    else:
      self.connectorNode.Start()
      self.webcamConnectorNode.Start()

    self.setActiveVolumeFromSelection()

  def setupSliceUSMarkers(self, sliceName):
    sliceView = slicer.app.layoutManager().sliceWidget( sliceName ).sliceView()
    displayableManagers = vtk.vtkCollection()
    sliceView.getDisplayableManagers( displayableManagers )
    rulerDisplayableManager = None
    for i in range( displayableManagers.GetNumberOfItems() ):
      if ( displayableManagers.GetItemAsObject( i ).IsA( "vtkMRMLRulerDisplayableManager" ) ):
        rulerDisplayableManager = displayableManagers.GetItemAsObject( i ) #Borrow the ruler displayable manager
    if ( rulerDisplayableManager is None ):
      return
    sliceRenderer = rulerDisplayableManager.GetRenderer()

    sliceNode = sliceView.mrmlSliceNode()
    sliceLogic = slicer.app.applicationLogic().GetSliceLogic( sliceNode )
    sliceBackgroundLogic = sliceLogic.GetBackgroundLayer()

    if ( sliceRenderer is None or sliceNode is None or sliceLogic is None or sliceBackgroundLogic is None ):
      return

    usMarkersProperties = {}
    usMarkersProperties[ "Renderer" ] = sliceRenderer
    usMarkersProperties[ "Node" ] = sliceNode
    usMarkersProperties[ "Logic" ] = sliceLogic
    usMarkersProperties[ "BackgroundLogic" ] = sliceBackgroundLogic
    usMarkersProperties[ "Spheres" ] = {}
    usMarkersProperties[ "Actors" ] = {}
    usMarkersProperties[ "MarkActor" ] = None
    self.usMarkersPropertiesDict[ sliceName ] = usMarkersProperties

    usMarkersProperties[ "Node" ].AddObserver( vtk.vtkCommand.ModifiedEvent, self.displaySliceUSMarkers )

  def displaySliceUSMarkers(self, node, eventid):
    for sliceName, usMarkersProperties in self.usMarkersPropertiesDict.items():
      if ( usMarkersProperties[ "Node" ] is not node ):
        continue # Only update the modified slice node (otherwise we will have unnecessary updates, possibly compromising performance)

      xyToIJKTransform = usMarkersProperties[ "BackgroundLogic" ].GetXYToIJKTransform()
      ijkToXYTransform = vtk.vtkGeneralTransform()
      ijkToXYTransform.DeepCopy( xyToIJKTransform )
      ijkToXYTransform.Inverse()

      self.xyToRASTransform = vtk.vtkGeneralTransform()
      self.xyToRASTransform.Concatenate( usMarkersProperties[ "Node" ].GetXYToRAS() )

      self.ijkToRASTransform = vtk.vtkGeneralTransform()
      self.ijkToRASTransform.DeepCopy( ijkToXYTransform )
      self.ijkToRASTransform.PostMultiply()
      self.ijkToRASTransform.Concatenate( self.xyToRASTransform )

      # Scale between RAS and IJK
      unitVector_IJK = [ 0, 1, 0 ] # Since the dots go in the j-direction
      unitVector_RAS = [ 0, 0, 0 ]
      self.ijkToRASTransform.TransformVectorAtPoint( [ 0, 0, 0 ], unitVector_IJK, unitVector_RAS )
      scale = vtk.vtkMath.Norm( unitVector_RAS )

      if ( usMarkersProperties[ "BackgroundLogic" ].GetVolumeNode() is None ):
       continue
      volumeDimensions = usMarkersProperties[ "BackgroundLogic" ].GetVolumeNode().GetImageData().GetDimensions()

      DOT_SPACING = 5 #mm
      DOT_RADIUS = 6 #pixels # This is the big dot radius, the small do radius should be half of this
      DOT_COLOR = [ 0, 1, 1 ] # Same as the default IGT needle color

      dotIndex = 0
      while( dotIndex < volumeDimensions[ 1 ] * float( scale ) / DOT_SPACING ):
        # Create the sphere source and actor if necessary
        if ( dotIndex not in usMarkersProperties[ "Actors" ] or dotIndex not in usMarkersProperties[ "Spheres" ] ):
          sphereSource = vtk.vtkSphereSource()
          actor2D = vtk.vtkActor2D()
          mapper2D = vtk.vtkPolyDataMapper2D()
          mapper2D.SetInputConnection( sphereSource.GetOutputPort() )
          actor2D.SetMapper( mapper2D )
          actor2D.GetProperty().SetColor( DOT_COLOR )
          usMarkersProperties[ "Renderer" ].AddActor( actor2D )

          usMarkersProperties[ "Spheres" ][ dotIndex ] = sphereSource
          usMarkersProperties[ "Actors" ][ dotIndex ] = actor2D

        # Find the location in the XY frame
        dotPosition_IJK = [ 0, dotIndex * DOT_SPACING / scale, 0 ]
        dotPosition_XY = [ 0, 0, 0 ]
        ijkToXYTransform.TransformPoint( dotPosition_IJK, dotPosition_XY )

        usMarkersProperties[ "Spheres" ][ dotIndex ].SetCenter( dotPosition_XY )
        usMarkersProperties[ "Spheres" ][ dotIndex ].SetRadius( DOT_RADIUS - DOT_RADIUS * ( dotIndex % 2 ) / 2.0 )

        dotIndex = dotIndex + 1

      # Remove anything unncessary from the renderer and dictionaries
      sphereIndices = usMarkersProperties[ "Spheres" ].keys()
      for index in sphereIndices:
        if ( index >= dotIndex ):
          usMarkersProperties[ "Renderer" ].RemoveActor( usMarkersProperties[ "Actors" ][ index ] )
          del usMarkersProperties[ "Actors" ][ index ]
          del usMarkersProperties[ "Spheres" ][ index ]

      # Add the text for the Marked side of the probe
      if ( usMarkersProperties[ "MarkActor" ] is None ):
        usMarkersProperties[ "MarkActor" ] = vtk.vtkTextActor()
        usMarkersProperties[ "MarkActor" ].SetInput( "M" )
        usMarkersProperties[ "MarkActor" ].GetProperty().SetColor( DOT_COLOR )
        usMarkersProperties[ "Renderer" ].AddActor( usMarkersProperties[ "MarkActor" ] )

      mPosition_IJK = [ volumeDimensions[ 0 ], 0, 0 ] # Assumes MF ultrasound orientation
      mPosition_XY = [ 0, 0, 0 ]
      ijkToXYTransform.TransformPoint( mPosition_IJK, mPosition_XY )
      usMarkersProperties[ "MarkActor" ].SetPosition( mPosition_XY[ 0 ], mPosition_XY[ 1 ] )

      # Rendering is already taken care of

  def updateAllBrowserNodes(self, caller, eventid):
    # Two things to take care of:
    # Set the sequences' virtual output nodes to be correct
    # Restore the appropriate active volume node
    sequenceSyncDict = {
      "NeedleToReference": self.needleToReference, # If the sequence name contains the key, make the virtual node same the value node
      "ProbeToReference": self.probeToReference,
      "Image": self.ultrasound.liveUltrasoundNode_Reference
    }

    browserCollection = slicer.mrmlScene.GetNodesByClass( "vtkMRMLSequenceBrowserNode" )
    for browserIndex in range( browserCollection.GetNumberOfItems() ):
      browserNode = browserCollection.GetItemAsObject( browserIndex )
      if ( browserNode.GetAttribute( "Recorded" ) is not None ):
        continue

      browserNode.SetOverwriteTargetNodeName(False)
      browserNode.SetDeepCopyVirtualNodes(True)

      sequenceCollection = vtk.vtkCollection()
      browserNode.GetSynchronizedSequenceNodes( sequenceCollection, True )
      for sequenceIndex in range( sequenceCollection.GetNumberOfItems() ):
        sequenceNode = sequenceCollection.GetItemAsObject( sequenceIndex )
        virtualNode = browserNode.GetVirtualOutputDataNode( sequenceNode )
        if ( virtualNode == None ):
          continue

        # Check if the virtual node is already one of the acceptable output nodes
        virtualNodeAcceptable = False
        for key, value in sequenceSyncDict.iteritems():
          if ( virtualNode.GetID() == value.GetID() ):
            virtualNodeAcceptable = True
        if ( virtualNodeAcceptable ):
          continue

        # Otherwise, replace it with an acceptable virtual node
        for key, value in sequenceSyncDict.iteritems():
          if ( key in virtualNode.GetName() ):
            browserNode.RemoveSynchronizedSequenceNode( sequenceNode.GetID() ) # Need to fully remove the virtual node from the scene

            originalProxyNodeName = value.GetName()

            sequenceBrowserLogic = slicer.modules.sequencebrowser.logic()
            sequenceBrowserLogic.AddSynchronizedNode( sequenceNode, value, browserNode ) #Re-add the sequence with the correct virtual node
            browserNode.SetOverwriteProxyName( sequenceNode, False ) # Must set this after re-adding the sequence node (the setting is dropped when the sequence node is removed)

            value.SetName( originalProxyNodeName )

            slicer.mrmlScene.RemoveNode( virtualNode ) # Declutter the scene

    self.setActiveVolumeFromSelection()

  def setActiveVolumeFromSelection(self):
    # First, find the selection node and volume reslice driver logic
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    if ( selectionNode is None ):
      return
    vrdLogic = slicer.modules.volumereslicedriver.logic()
    if ( vrdLogic is None ):
      return
  
    selectedRecording = self.recordingComboBox.currentNode()
    activeVolumeID = self.ultrasound.liveUltrasoundNode_Reference.GetID()
    if ( self.resultsCollapsibleButton.checked
         and selectedRecording is not None
         and selectedRecording.GetAttribute( "Recorded" ) is None ):
      activeVolumeID = self.ultrasound.liveUltrasoundNode_Reference.GetID()

    selectionNode.SetActiveVolumeID( activeVolumeID )
    selectionNode.SetReferenceActiveVolumeID( activeVolumeID )

    appLogic = slicer.app.applicationLogic()
    if ( appLogic is not None ):
      appLogic.PropagateVolumeSelection()
      appLogic.FitSliceToAll()

    redSliceNode = slicer.util.getNode( "vtkMRMLSliceNodeRed" )
    redSliceNode.SetSliceResolutionMode( slicer.vtkMRMLSliceNode.SliceFOVMatchVolumesSpacingMatch2DView ) # This works when the image is scaled by a transform (the previous does not)
    if ( redSliceNode is not None ):
      vrdLogic.SetDriverForSlice( activeVolumeID, redSliceNode )

    self.setupWebcamResliceDriver()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded( self, scene, eventid, node ):
    if ( node is None ):
      return

  def onFiducialPointAdded( self, node, eventid ):
    if ( node is None or not node.IsA( "vtkMRMLMarkupsFiducialNode" ) ):
      return
  
    if ( node.GetNumberOfFiducials() > 0 ):
      targetPosition = [ 0, 0, 0 ]
      node.GetNthFiducialPosition( 0, targetPosition )

      self.targetFiducialNode.RemoveAllMarkups()
      self.targetFiducialNode.AddFiducialFromArray( targetPosition )

      node.RemoveObserver( slicer.vtkMRMLMarkupsNode.PointModifiedEvent )
      slicer.mrmlScene.RemoveNode( node )
  
  def setSequenceBrowserToolBarsVisible(self, visible, wasVisible = False):
    sequenceBrowserToolBars = slicer.util.mainWindow().findChildren( "qMRMLSequenceBrowserToolBar" )
    for toolBar in sequenceBrowserToolBars:
      toolBar.setVisible( visible )

  def setPlaybackRealtime(self, browserNode):
    try: # Update the playback fps rate
      sequenceNode = browserNode.GetMasterSequenceNode()
      numDataNodes = sequenceNode.GetNumberOfDataNodes()
      startTime = float( sequenceNode.GetNthIndexValue( 0 ) )
      stopTime = float( sequenceNode.GetNthIndexValue( numDataNodes - 1 ) )
      frameRate = numDataNodes / ( stopTime - startTime )
      browserNode.SetPlaybackRateFps( frameRate )
    except:
      logging.debug( "setPlaybackRealtime:: ", str(sys.exc_info()[0] ))

  def startSequenceBrowserRecording(self, browserNode):

    if (browserNode is None):
      return
  
    # Indicate that this node was recorded, not loaded from file
    browserNode.SetName( slicer.mrmlScene.GetUniqueNameByString( "Recording" ) )
    browserNode.SetAttribute( "Recorded", "True" )
    # Create and populate a sequence browser node if the recording started
    browserNode.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(browserNode)
    sequenceBrowserLogic = slicer.modules.sequencebrowser.logic()

    modifiedFlag = browserNode.StartModify()
    sequenceBrowserLogic.AddSynchronizedNode(None, self.needleToReference, browserNode)
    sequenceBrowserLogic.AddSynchronizedNode(None, self.probeToReference, browserNode)
    sequenceBrowserLogic.AddSynchronizedNode(None, self.ultrasound.liveUltrasoundNode_Reference, browserNode)
    sequenceBrowserLogic.AddSynchronizedNode(None, self.webcam0RGB, browserNode)
    sequenceBrowserLogic.AddSynchronizedNode(None, self.webcam0DEPTH, browserNode)
    sequenceBrowserLogic.AddSynchronizedNode(None, self.webcam1RGB, browserNode)
    sequenceBrowserLogic.AddSynchronizedNode(None, self.webcam1DEPTH, browserNode)

    # Stop overwriting and saving changes to all nodes
    browserNode.SetRecording( None, True )
    browserNode.SetOverwriteProxyName( None, False )
    browserNode.SetSaveChanges( None, False )
    browserNode.EndModify( modifiedFlag )

    self.recordingStartTime = vtk.vtkTimerLog.GetUniversalTime()
    print (self.recordingStartTime)
    self.scanVesselCrossSection() #start looking for steps to be completed

    browserNode.SetRecordingActive(True)

    self.StartRecordingSeekWidget.setMRMLSequenceBrowserNode(browserNode)

  def stopSequenceBrowserRecording(self, browserNode):
    if (browserNode is None):
      return

    browserNode.SetRecordingActive(False)
    browserNode.SetRecording( None, False )
    self.setPlaybackRealtime(browserNode)
    self.fileName = self.userIDLineEdit.text + "-" + time.strftime("%Y%m%d-%H%M%S")
    self.saveAllRecordings()

  def onStartStopRecordingClicked(self):
    if self.ultrasound.startStopRecordingButton.isChecked():
      self.recordingStartTime = vtk.vtkTimerLog.GetUniversalTime()
      self.needleTutorSequenceBrowserNode = slicer.vtkMRMLSequenceBrowserNode()
      self.startSequenceBrowserRecording(self.needleTutorSequenceBrowserNode)
    else:
      self.stopSequenceBrowserRecording(self.needleTutorSequenceBrowserNode)



