
import pya
import numpy as np
import math
#-------------------------------------
#  Library definition

class TestPCell(pya.PCellDeclarationHelper):
  def __init__(self):
    super(TestPCell, self).__init__()
    self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("r", self.TypeDouble, "Radius", default = 1.0)
    self.param("n", self.TypeInt, "Number of points", default = 64)
  def display_text_impl(self):
    return "Circle (l=%s,r=%.12g,n=%d)" % (str(self.l), self.r, self.n)
  def produce_impl(self):
    self.cell.shapes(self.l_layer).insert(pya.DPolygon.ellipse(pya.DBox(-self.r, -self.r, self.r, self.r), self.n))
class TestLib(pya.Library):
  def __init__(self):
    self.description = "Test library"
    self.layout().register_pcell("Circle", TestPCell())
    self.register("TestLib")
# create and register the library
lib = TestLib()
# --------------------------------------------------------
#  Client code starts here. We are creating a layout instance.
lay = pya.Layout()
# The lengths are in micron, thus a focus length of 8000.0 corresponds to 8000um=8mm.
lensFocusLength=8000.0 
lensOperationWavelength=10.0
unitCellPeriod=2.0 
cellArraySize=1500
# The placement of unit cells are in polar coordinates, 
# radius=unitCellPeriod*cellArraySize
lensDiameter=2*cellArraySize*unitCellPeriod

PI=math.pi
unitCellSizeArray=np.linspace(0.4, 1.6, num=16)*0.5
phaseShiftArray=np.linspace(0.0, 2*PI, num=17)

# Full phase range(2*pi) is sampled with various size of unit cells.
# Unit Cell Declerations are as follows: Circles with radius r
pcellArray=[]
for unitCellSize in unitCellSizeArray:
  para = { "l": pya.LayerInfo(1, 0), "r":unitCellSize, "n": 64 }
  pcell= lay.create_cell("Circle", "TestLib", para)
  pcellArray.append(pcell)

cellRadiusRange= np.arange(400.0,lensDiameter/2,unitCellPeriod)
# The complete lens is constructed from a base pie structure with certain angle,
# thus we can exploit the symmetry. The symmetry dictates that we can form the full circular lens structure
# from a smaller angle pie. E.g, 360 degree structure can be constructed from angle pies of 10 degrees. 
# We need 36 of them to replicate and reposition to construct the complete circular lens.
top = lay.create_cell("angle")  
for cellRadius in cellRadiusRange:
  Tf=np.ceil(2*math.pi*cellRadius/unitCellPeriod)+0.0001
  # For this case the certain angle is 10 degrees, since Tf is divided by 36.
  T=(Tf/36).astype(int)
  thetaArray=np.linspace(0,2*math.pi/36,T)
  for theta in thetaArray:
    cellPosX=cellRadius*math.cos(theta)
    cellPosY=cellRadius*math.sin(theta)
    phaseTarget=2*PI*(math.sqrt(cellPosX**2+cellPosY**2+lensFocusLength**2)-lensFocusLength)/lensOperationWavelength
    phaseTargetReduced=phaseTarget%(2*PI)
    cellPosTrans = pya.DCplxTrans.new(1, 0, False, cellPosX,cellPosY) # mag,rot,mirror, D
    cellPos=2*math.sqrt(cellPosX**2+cellPosY**2)
    # The outer frame of the complete lens structure should be circle.
    if (cellPos<=lensDiameter):
      phaseDiffArray=(phaseTargetReduced-phaseShiftArray)
      phaseArrayIndex=(np.abs(phaseDiffArray)).argmin()
      if (np.sign(phaseDiffArray[phaseArrayIndex])>0.0):
        phaseArrayIndex=phaseArrayIndex+1
      else:
        pass 
      top.insert(pya.DCellInstArray(pcellArray[phaseArrayIndex-1].cell_index(), cellPosTrans))
    else:
     continue
# The complete lens structure is formed from a pie with certain angle by repositioning
full= lay.create_cell("Full")
for angleIndex in np.arange(36): 
  trans = pya.DCplxTrans.new(1, angleIndex*10.0, False,0,0)
  cellIndex=lay.cell_by_name("angle")
  full.insert(pya.DCellInstArray(cellIndex, trans))


top=full
cellRadiusRange= np.arange(0.0,400,unitCellPeriod)  
for cellRadius in cellRadiusRange:
  Tf=np.ceil(2*math.pi*cellRadius/unitCellPeriod)+0.0001
  T=(Tf).astype(int)
  thetaArray=np.linspace(0,2*math.pi,T)
  for theta in thetaArray:
    cellPosX=cellRadius*math.cos(theta)
    cellPosY=cellRadius*math.sin(theta)
    phaseTarget=2*PI*(math.sqrt(cellPosX**2+cellPosY**2+lensFocusLength**2)-lensFocusLength)/lensOperationWavelength
    phaseTargetReduced=phaseTarget%(2*PI)
    cellPosTrans = pya.DCplxTrans.new(1, 0, False, cellPosX,cellPosY) # mag,rot,mirror, D
    cellPos=2*math.sqrt(cellPosX**2+cellPosY**2)
    if (cellPos<=lensDiameter):
      phaseDiffArray=(phaseTargetReduced-phaseShiftArray)
      phaseArrayIndex=(np.abs(phaseDiffArray)).argmin()
      if (np.sign(phaseDiffArray[phaseArrayIndex])>0.0):
        phaseArrayIndex=phaseArrayIndex+1
      else:
        pass 
      top.insert(pya.DCellInstArray(pcellArray[phaseArrayIndex-1].cell_index(), cellPosTrans))
    else:
     continue
# re-configure the file-path to determine where the file should be saved in your device.
# Use double slash (\\) instead of single slash.
lay.write("C:\\Users\\User\\Desktop\\metalens_mask.gds")
#print(thetaArray)
print("The mask is constructed !")



