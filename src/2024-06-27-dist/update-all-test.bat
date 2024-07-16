@echo off
:BEGIN
CLS
CHOICE /N /C:123 /M "Who is this?  ( 1(Sarah), 2(Nathalie), 3(Margaret),)"%1
IF ERRORLEVEL ==3 GOTO MARGARET
IF ERRORLEVEL ==2 GOTO NATHALIE
IF ERRORLEVEL ==1 GOTO SARAH
GOTO END

:MARGARET
ECHO YOU HAVE PRESSED MARGARET
CHOICE /C YN /M "Is this ok? (Y or N)"%1

IF ERRORLEVEL ==2 GOTO END
IF ERRORLEVEL ==1 GOTO UPDATEM
:UPDATEM
ECHO UPDATING Repository - MARGARET
ECHO ...to era2023
xcopy "C:\Users\glendin\Rothamsted Research\e-RA - Documents\Data-docs repository\metadata" "\\INTRANET-SERVER\era\era2023\metadata" /s /i /f /y /d
ECHO ...to Live
xcopy "C:\Users\glendin\Rothamsted Research\e-RA - Documents\Data-docs repository\metadata" "\\internet-serv2\newera\metadata" /s /i /f /y /d
ECHO ...to Basset
xcopy "C:\Users\glendin\Rothamsted Research\e-RA - Documents\Data-docs repository\metadata" "\\basset\era\era2023\metadata" /s /i /f /y /d
ECHO .
GOTO NEXT
::UPDATEM

:NATHALIE
ECHO YOU HAVE PRESSED NATHALIE
CHOICE /C YN /M "Is this ok? (Y or N)"%1

IF ERRORLEVEL ==2 GOTO END
IF ERRORLEVEL ==1 GOTO UPDATEN
:UPDATEN
ECHO UPDATING Repository - NATHALIE
ECHO ...to internet-serv2\Live
xcopy "D:\OneDrive - Rothamsted Research\Documents - e-RA\Data-docs repository\metadata" "\\internet-serv2\newera\metadata" /s /i /f /y /d
ECHO ...to basset\Basset
xcopy "D:\OneDrive - Rothamsted Research\Documents - e-RA\Data-docs repository\metadata" "\\basset\era\era2023\metadata" /s /i /f /y /d
ECHO ...to INTRANET-SERVER\era2023
xcopy "D:\OneDrive - Rothamsted Research\Documents - e-RA\Data-docs repository\metadata" "\\INTRANET-SERVER\era\era2023\metadata" /s /i /f /y /d
ECHO .
::UPDATEN
GOTO NEXT
:SARAH
ECHO YOU HAVE PRESSED SARAH
CHOICE /C YN /M "Is this ok? (Y or N)"%1
IF ERRORLEVEL ==2 GOTO END
IF ERRORLEVEL ==1 GOTO UPDATES
:UPDATES
ECHO UPDATING Repository - SARAH
ECHO ...to era2023
::xcopy "C:\Users\perrymas\OneDrive - Rothamsted Research\@ e-RA Documents\Data-docs repository\metadata" "\\INTRANET-SERVER\era\era2023\metadata" /s /i /f /y /d
ECHO ...to Live
::xcopy "C:\Users\perrymas\OneDrive - Rothamsted Research\@ e-RA Documents\Data-docs repository\metadata" "\\internet-serv2\newera\metadata" /s /i /f /y /d
ECHO ...to Basset
::xcopy "C:\Users\perrymas\OneDrive - Rothamsted Research\@ e-RA Documents\Data-docs repository\metadata" "\\basset\era\era2023\metadata" /s /i /f /y /d
ECHO .
GOTO NEXT
::UPDATES

:NEXT

ECHO UPDATING metadata  
ECHO ...to internet-serv2\Live
xcopy "d:\eRAWebStage\eraGilbert05\metadata" "\\internet-serv2\newera\metadata" /s /i /f /y /d
ECHO ...to basset\Basset
xcopy "d:\eRAWebStage\eraGilbert05\metadata" "\\basset\era\era2023\metadata" /s /i /f /y /d
ECHO ...to INTRANET-SERVER\era2023
xcopy "d:\eRAWebStage\eraGilbert05\metadata" "\\INTRANET-SERVER\era\era2023\metadata" /s /i /f /y /d
ECHO .
ECHO UPDATING images
ECHO UPDATING images to Basset first 
xcopy "\\INTRANET-SERVER\era\era2023\images" "\\basset\era\era2023\images" /s /i /f /y /d
ECHO UPDATING images to internet from basset
xcopy "\\basset\era\era2023\images" "\\internet-serv2\newera\images" /s /i /f /y /d
ECHO .
ECHO UPDATING infofiles - only if they are already in destination
xcopy "\\INTRANET-SERVER\era\era2023\metadata\*.html" "\\basset\era\era2023\metadata" /s /i /f /y /u /d
xcopy "\\basset\era\era2023\metadata\*.html" "\\internet-serv2\newera\metadata" /s /i /f /y /u /d

GOTO END

:END
PAUSE