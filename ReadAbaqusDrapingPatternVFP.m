clc
clear
close all

% This script processes an .vfp text file exported from Composites Modeler
% for Abaqus/CAE. The file contains the mold surface in an STL format, i.e. 
% with triangular facets defined by their vertices and the draped pattern.
%
% If quadrilateral elements are defined in Abaqus, it seems that the they
% are split in two for creating the triangular mold elements.
%
% The draped pattern is defined with 11 columns and a number of rows
% equivalent to the number of draped pattern nodes. The columns are:
% u, v, x, y, z, ood, order, elementId, strain(radians), thickness, and
% deviation(radians)
% Here:
% - u,v: row and column in the pattern grid (can be negative)
% - x,y,z: coordinate of the grid node
% - ood: ?
% - order: ? (probably the order in which nodes are placed in simulation)
% - elementId: mold element enclosing the current grid node
% - strain(radians): Shear angle at current grid node in radians
% - thickness: Thickness at current grid node (dependent on shear)
% - deviation(radians): deviations from nominal fiber angles (2 components) 
%
% Created by Christian Krogh, Department of Materials and Production,
% Aalborg University Denmark. Email: ck@mp.aau.dk
% August 2022
% MATLAB version: 2022a

% Select .vfp file to read and process
Filename = 'GeoCourse';
%Filename = 'SteerCourseSingle';
%Filename = 'SteerCourseDouble';

%% Get the mold data

% Read the entire file as a cell array of strings. One string for each line
FileID = fopen([Filename '.vfp'] ,'r');
Data = textscan(FileID,'%s','Delimiter','\n');
FileContents = Data{1};
clear Data
fclose(FileID);

% Get the mold vertices (lines that begin with "vertex")
MoldData_str = FileContents(strncmp(FileContents,'vertex',6),:);
% Get the numeric values, i.e. x,y,z coordinates while skipping "vertex"
MoldData = sscanf(char(MoldData_str)','%*s %f %f %f');

% Create arrays for plotting the mold facets as patches
XMold = reshape(MoldData(1:3:end),3,[]);
YMold = reshape(MoldData(2:3:end),3,[]);
ZMold = reshape(MoldData(3:3:end),3,[]);

%% Get the draped pattern

% Define string that identifies the beginning of the pattern section and
% retrieve its line number
PatternStr = '*PLY';
PatternStartLineNo = find(strcmp(FileContents,PatternStr));
% Define the number of lines to skip after '*PLY' to reach 1st line of data  
PatternSkipLines = 3;
% Read the draped pattern data directly from the .vfp file
DrapePattern = readmatrix([Filename '.vfp'],'FileType','Text',...
    'NumHeaderLines', PatternStartLineNo+PatternSkipLines);

clear FileContents    
    
% Use the "u" and "v" indices to build a grid (x,y,z and shear) that can 
% be plotted using the surf function

% Get the rows and columns, i.e. u and v
Row = DrapePattern(:,1);
Col = DrapePattern(:,2);
% Calculate the number of rows and columns
nRows = max(Row) - min(Row) + 1;
nCols = max(Col) - min(Col) + 1;
% Initialize arrays
XDrape = NaN(nRows,nCols);
YDrape = NaN(nRows,nCols);
ZDrape = NaN(nRows,nCols);
Shear = NaN(nRows,nCols);
% Build the grid
for i = 1:size(DrapePattern,1)   
    % Make the grid start in index 1,1
    ShiftRow = Row(i) - min(Row) + 1;
    ShiftCol = Col(i) - min(Col) + 1;
    
    % Fill in the x,y,z coords and shear in arrays
    % Notice the sign change in Shear, which depends on the coordinate
    % system used
    XDrape(ShiftRow,ShiftCol) = DrapePattern(i,3);
    YDrape(ShiftRow,ShiftCol) = DrapePattern(i,4);
    ZDrape(ShiftRow,ShiftCol) = DrapePattern(i,5);
    Shear(ShiftRow,ShiftCol) = -180/pi * DrapePattern(i,9);
end

%% Plot

figure
hold on
% Plot the mold in a gray-blue color
patch(XMold,YMold,ZMold,[0.6,0.7,0.8],'EdgeColor','none','FaceAlpha',0.5...
    ,'FaceLighting','Gouraud')
% Plot the draped pattern with interpolated shear color values
% Do a small z shift such that the ply pattern is above the mold when
% plotting
zShift = 1e-3;
surf(XDrape,YDrape,ZDrape+zShift,Shear,'FaceColor','interp',...
    'EdgeColor','interp')

% Format plot
axis equal
axis tight
colormap jet
c = colorbar;
c.Label.String = 'Shear angle [deg]';
xlabel('x'); ylabel('y'); zlabel('z');
view(3)