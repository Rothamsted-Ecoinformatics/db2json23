@echo off
:BEGIN
CLS
ECHO  . 
ECHO  .. 
ECHO  this will update the metadata, repository and images - special for SARAH 
ECHO  . 
ECHO  .. 
CHOICE /C YN /M "Is this ok? (Y or N)"%1

IF ERRORLEVEL ==2 GOTO END
IF ERRORLEVEL ==1 GOTO UPDATE
GOTO END

:UPDATE
ECHO UPDATING metadata  
ECHO ...to era2023
xcopy "d:\eRAWebStage\eraGilbert01\metadata" "\\INTRANET-SERVER\era\era2023\metadata" /s /i /f /y /d
ECHO ...to Live
xcopy "d:\eRAWebStage\eraGilbert01\metadata" "\\internet-serv2\newera\metadata" /s /i /f /y /d
ECHO .
ECHO UPDATING Repository
ECHO ...to era2023
xcopy "C:\Users\perrymas\OneDrive - Rothamsted Research\@ e-RA Documents\Data-docs repository\metadata" "\\INTRANET-SERVER\era\era2023\metadata" /s /i /f /y /d
ECHO ...to Live
xcopy "C:\Users\perrymas\OneDrive - Rothamsted Research\@ e-RA Documents\Data-docs repository\metadata" "\\internet-serv2\newera\metadata" /s /i /f /y /d
ECHO .
ECHO UPDATING images
xcopy "\\INTRANET-SERVER\era\era2023\images" "\\internet-serv2\newera\images" /s /i /f /y /d
ECHO .
ECHO UPDATING infofiles - only if they are already in destination
xcopy "\\INTRANET-SERVER\era\era2023\metadata" "\\internet-serv2\newera\metadata" /s /i /f /y /u /d
GOTO END
::UPDATE

:END
timeout /t -1