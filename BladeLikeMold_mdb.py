# BladeLikeMold in Abaqus/CAE Composites Modeler with three courses
# Created by Christian Krogh, Department of Materials and Production,
# Aalborg University Denmark. Email: ck@mp.aau.dk

# The "magic line" that enables to retrieve coordinates explicitly
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

## Load Abaqus modules
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

### Set working directory ###
import os
os.chdir('./')

# Path to Abaqus Composites Modeler plugins (python), assuming C drive installation
# For Abaqus 2021 
CMAPluginsDir = 'C:/SIMULIA/EstProducts/2021/win_b64/code/python2.7/lib/abaqus_plugins/CMA'
# For Abaqus 2020
# CMAPluginsDir = 'C:/SIMULIA/EstProducts/2020/win_b64/code/python2.7/lib/abaqus_plugins/CMA'
# For Abaqus 2019
#CMAPluginsDir = 'C:/SIMULIA/CAE/2019/win_b64/code/python2.7/lib/abaqus_plugins/CMA'

## Settings
MoldElemSize = 0.04
PlyElemSize = 0.0125
CourseWidth = 0.5
CourseLength = 4.0
MaxShearStrain = 5

## Hard-coded data
RefNode = 4243
GeometrySetPt =  (0.511923, 1.99978, -0.78668) 
RightEdgePt = (0.670089, 0.999802, -0.651936) 
BotEdgePt = (-0.396898, -0.001162, -0.864639) 

## Short notation
Md = mdb.models['Model-1']

## Load .sat geometry
mdb.openAcis('BladeLikeMold.sat', scaleFromFile=OFF)
Md.PartFromGeometryFile(combine=False, dimensionality=THREE_D, 
    geometryFile=mdb.acis, name='BladeLikeMold', scale=0.001, type=DEFORMABLE_BODY)
    
## Seed mold globally and mesh
Md.parts['BladeLikeMold'].seedPart(deviationFactor=0.1, 
    minSizeFactor=0.1, size=MoldElemSize)
Md.parts['BladeLikeMold'].setMeshControls(elemShape=TRI, 
    regions=Md.parts['BladeLikeMold'].faces.findAt(
    (GeometrySetPt, )))
Md.parts['BladeLikeMold'].generateMesh()

## Create a geometry set
Md.parts['BladeLikeMold'].Set(faces=
    Md.parts['BladeLikeMold'].faces.findAt((GeometrySetPt, )), 
    name='GeometrySet')

## Create a coordinate system with the x axis oriented in the longitudinal direction
Md.parts['BladeLikeMold'].DatumCsysByThreePoints(
    coordSysType=CARTESIAN, name='NewCSYS', origin=(0.0, 0.0, 0.0), 
    point1=(0.0, 1.0, 0.0), point2=(-0.5, 0.5, 0.0))

## Create set of the right edge for a seed curve
Md.parts['BladeLikeMold'].Set(edges=
    Md.parts['BladeLikeMold'].edges.findAt((RightEdgePt, )), 
    name='EdgeSet')

## Create set of the bottom edge for a seed curve
Md.parts['BladeLikeMold'].Set(edges=
    Md.parts['BladeLikeMold'].edges.findAt((BotEdgePt, )), 
    name='BotEdgeSet')

## Make the seedpoint the corner node, i.e. RefNode at index RefNode-1
CourseSeedPt = Md.parts['BladeLikeMold'].nodes[RefNode-1].coordinates
nElements = len(Md.parts['BladeLikeMold'].elements)

## Load composites modeler
import sys
sys.path.append(CMAPluginsDir)    
    
import CMACommands
import CMACommandsMapMesh
import CMACommandsResults
import CMACommandsMaterials
import CMACommandsBoundingMeshes
CMACommands.InitialiseLayup()
from CMAConstants import *

## Create layup
# Create the .layup file
CMACommands.LayupCommandLayupFile(strCommand='LayupCommandNew', 
    strFilename='./BladeLikeMold.Layup', 
    strModel='Model-1', strPart='BladeLikeMold', strData='')
# Create material
CMACommands.LayupCommandUpdateMaterial(strModel='Model-1', 
    strPart='BladeLikeMold', material='Glass', oldmaterial='', 
    analysisMaterial='', type='Biaxial', thickness=0.001, maximumStrain=60.0, 
    warpWeftAngle=90.0)

## Create a geodesic course
PlyName1 = 'GeoCourse'
CMACommands.LayupCommandUpdatePly2(bPreview=OFF, model='Model-1', 
    part='BladeLikeMold', oldname='', name=PlyName1, type='Biaxial', 
    typeMethod='', material='Glass', stepLength=PlyElemSize, referenceAngle=0.0, 
    seedPoint=CourseSeedPt, applicationDirection=(0.0, -0.0, -1.0), 
    referenceDirection=(0.0, 1.0, 0.0), coordIsSet=1, coordOrigin=(0.0, 0.0, 
    0.0), coordName='NewCSYS', extensionType='Principle', axisType='Geodesic', 
    warpweftAngle=0, warpweftRatio=1, maximumStrain=MaxShearStrain, minWarp=1e-12, 
    maxWarp=CourseLength, minWeft=1e-12, maxWeft=CourseWidth, elementLabels=(0, ), 
    elementIDs=(('GeometrySet', ), ), elementTypes=('SETS', ), 
    smoothElementLabels=(0, ), smoothElementIDs=(('!', ), ), 
    smoothElementTypes=('ELEMENTS', ), singleSeedCurveElementIDs=(), 
    singleSeedCurveType='', singleSeedCurve=(), singleSeedCurveDirection='', 
    doubleSeedCurveElementIDs=(), doubleSeedCurve=(), doubleSeedCurveType='', 
    splitElementIDs=(), splitCurves=(), splitCurvesType=(), previewStates=(
    True, True, False, True, True, False, False, False, False, False, 5.0), 
    rosetteTransfer='ApplicationDirection', inadmissibleMode='Delete', 
    inadmissibleTolerance=1)

## Create a single steer course
PlyName2 = 'SteerCourseSingle'
CMACommands.LayupCommandUpdatePly2(bPreview=OFF, model='Model-1', 
    part='BladeLikeMold', oldname='', name=PlyName2, type='Biaxial', 
    typeMethod='', material='Glass', stepLength=PlyElemSize, referenceAngle=0.0, 
    seedPoint=CourseSeedPt, applicationDirection=(-0.0, -0.0, -1.0), 
    referenceDirection=(0.0, 1.0, 0.0), coordIsSet=1, coordOrigin=(0.0, 0.0, 
    0.0), coordName='NewCSYS', extensionType='Principle', axisType='Single', 
    warpweftAngle=90, warpweftRatio=1, maximumStrain=MaxShearStrain, minWarp=1e-12, 
    maxWarp=CourseLength, minWeft=1e-12, maxWeft=CourseWidth, elementLabels=(1, ), 
    elementIDs=(('!1:'+str(nElements), ), ), elementTypes=('ELEMENTS', ), 
    smoothElementLabels=(1, 0), smoothElementIDs=(('!', ), ('!', )), 
    smoothElementTypes=('ELEMENTS', 'ELEMENTS'), singleSeedCurveElementIDs=(), 
    singleSeedCurveType='SETS', singleSeedCurve=('EdgeSet', ), 
    singleSeedCurveDirection='Warp', 
    singleSeedCurveDirectionAngle=0, doubleSeedCurveElementIDs=(), 
    doubleSeedCurve=(), doubleSeedCurveType='', splitElementIDs=(), 
    splitCurves=(), splitCurvesType=(), previewStates=(False, True, True, 
    False, False, False, False, True, False, False, 5.0), 
    rosetteTransfer='ApplicationDirection', inadmissibleMode='Delete', 
    inadmissibleTolerance=1)

## Create a double steer course
PlyName3 = 'SteerCourseDouble' 
CMACommands.LayupCommandUpdatePly2(bPreview=OFF, model='Model-1', 
    part='BladeLikeMold', oldname='', name=PlyName3, 
    type='Biaxial', typeMethod='', material='Glass', stepLength=PlyElemSize, 
    referenceAngle=0.0, seedPoint=CourseSeedPt, applicationDirection=(
    -0.0, -0.0, -1.0), referenceDirection=(0.0, 1.0, 0.0), coordIsSet=1, 
    coordOrigin=(0.0, 0.0, 0.0), coordName='NewCSYS', extensionType='Principle', 
    axisType='Double', warpweftAngle=90, warpweftRatio=1, 
    maximumStrain=MaxShearStrain, minWarp=1e-12, maxWarp=CourseLength, 
    minWeft=1e-12, maxWeft=CourseWidth, elementLabels=(1, ), 
    elementIDs=(('!1:'+str(nElements), ), ), elementTypes=('ELEMENTS', ), 
    smoothElementLabels=(1, 0), smoothElementIDs=(('!', ), ('!', )), 
    smoothElementTypes=('ELEMENTS', 'ELEMENTS'), singleSeedCurveElementIDs=(), 
    singleSeedCurveType='SETS', singleSeedCurve=('EdgeSet', ), 
    singleSeedCurveDirection='', doubleSeedCurveElementIDs=(), 
    doubleSeedCurve=('BotEdgeSet', ), doubleSeedCurveType='SETS', 
    splitElementIDs=(), splitCurves=(), splitCurvesType=(), previewStates=(
    False, True, True, False, False, False, False, True, False, False, 5.0), 
    rosetteTransfer='ApplicationDirection', inadmissibleMode='Delete', 
    inadmissibleTolerance=1)
 
## Save .layup
CMACommands.LayupCommandSave(model='Model-1', part='BladeLikeMold')

## Export draped patterns
CMACommands.LayupCommandExportDrapedPatternVFP('GeoCourse',PlyName1,'Model-1','BladeLikeMold')
CMACommands.LayupCommandExportDrapedPatternVFP('SteerCourseSingle',PlyName2,'Model-1','BladeLikeMold')
CMACommands.LayupCommandExportDrapedPatternVFP('SteerCourseDouble',PlyName3,'Model-1','BladeLikeMold')