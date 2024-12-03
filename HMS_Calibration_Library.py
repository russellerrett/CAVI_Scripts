#from decimal                import Decimal
#from hec.data.cwmsRating    import RatingSet
#from hec.data.cwmsRating    import RatingSet
from hec.hecmath            import TimeSeriesMath
from hec.io                 import TimeSeriesContainer
from hec.heclib.dss         import HecDss
from hec.heclib.util        import HecTime
#from hec.dataui.tx          import TsContainerDataSourceList
#from hec.dataui.tx.awt      import VerifyDataDlg
#from hec.dataTable          import HecDataTableToExcel
#from hec.data.cwmsRating.io import TableRatingContainer
from hec.dssgui             import ListSelection
from hec.script             import MessageBox, Constants, Plot, Tabulate, AxisMarker
from java.awt               import BorderLayout, GridLayout, FlowLayout, Toolkit, GraphicsEnvironment, Rectangle, Color, Font
#from java.awt.event         import ActionListener, FocusListener
#from java.io                import FileOutputStream, IOException
#from java.lang              import System
#from java.text              import SimpleDateFormat
from java.util              import TimeZone
from javax.swing            import JDialog, JCheckBox, JComboBox, JPanel, JButton, JOptionPane, JScrollPane, BoxLayout, JLabel, JTextField, SwingConstants, ScrollPaneConstants
#from javax.swing.border     import EmptyBorder
#from rma.services           import ServiceLookup
#from rma.swing              import DateChooser
#from time                   import mktime, localtime
#from timeit                 import default_timer
from com.rma.client import Browser
from hec2.rts.script import RTS
import datetime, time, calendar, inspect, java, os, sys, traceback, math, shutil, logging, getpass, hec, wcds, glob
def output(msg="") :
	'''
	Output to console log
	'''
	print ("%s : %s" % (progname, msg))
def error(msg) :
	'''
	Outputs an error message and rasies an exception
	'''
	output(msg)
	raise Exception(msg)
	
def chktab(tab) :
	'''
	Checks that the "Modeling" tab is selected
	'''
	if tab.getTabTitle() != "Modeling" : 
		msg = "The Modeling tab must be selected"
		output("ERROR : %s" % msg)
		raise Exception(msg)
	 
def chkfcst(fcst) :
	'''
	Checks that a forecast is open
	'''
	if fcst is None : 
		msg = "A forecast must be open"
		output("ERROR : %s" % msg)
		raise Exception(msg)
try :
	try :
	
################## Stection-Start ####################################################################
## This section finds the current forecast.dss file (i.e. active forecast) ##
		
		## Get the current forecast ##
		frame = Browser.getBrowser().getBrowserFrame()
		proj = frame.getCurrentProject()
		pane = frame.getTabbedPane()
		tab = pane.getSelectedComponent()
		chktab(tab)
		fcst = tab.getForecast()
		chkfcst(fcst)
		dssfile = fcst.getOutDssPath()
		fcstTimeWindowString = str(fcst.getRunTimeWindow())
		cwmsFile = HecDss.open(dssfile)

		## Watershed name for use in defining base directory path
		Watershed = str(RTS.getWatershed())
		
		## print 'fcstTimeWindowString : %s' %(fcstTimeWindowString)
		important_times = [ i.strip(' ') for i in fcstTimeWindowString.split(';') ]
		start_time, forecast_time, end_time = important_times[0], important_times[1], important_times[2]
		
		## Forecast Time for default naming for exporting
		fcst_time = HecTime()
		fcst_time.set(forecast_time)
		fcst_time1 = fcst_time.dateAndTime(104)
		fcst_time_string1 = str(fcst_time1)
		fcst_time_string = fcst_time_string1.replace(",", "").replace(":", "")
		
		## Define forecast directory
		dssFileName = fcst.getForecastDSSFilename()
		forecastDirectory = str(os.path.dirname(dssFileName))
		
		## Find HMS active forecast calibration file
		ActiveFcst = tab.getActiveForecastRun()
		ActiveAlts = ActiveFcst.getModelAlternatives()
		ActiveHMSAlt = str(ActiveAlts.get(1))
		Current_HMS_fcstFileName1 = os.path.join(forecastDirectory,'hms\\forecast', ""+ActiveHMSAlt+".forecast")
		Current_HMS_fcstFileName2 = Current_HMS_fcstFileName1.replace("\\", "/")
		Current_HMS_fcstFileName = Current_HMS_fcstFileName2.replace(",", "")
		
		## Check is calibration_library folder exists in base hms/forecast directory
		Calibration_Library_Directory_os = os.path.join(forecastDirectory,'..\\..\\..\\watershed\\'+Watershed+'\\hms\\forecast\\calibration_library')
		Calibration_Library_Directory = Calibration_Library_Directory_os.replace("\\", "/")
		if os.path.exists(Calibration_Library_Directory) :
			print("calibration_library directory exists")
		else :
			print("calibration_library directory does not exists.  hms/forecast/calibration_library directory created in base watershed.")
			os.makedirs(Calibration_Library_Directory)
		
################## Stection-End ######################################################################
		
################## Stection-Start ####################################################################
############################################################################
####	Menu selection for Import or Export of HMS calibration flie		####
############################################################################
		selections = ["Import HMS Calibrations","Export HMS Calibrations"]
		HMSCalLibSelected = JOptionPane.showInputDialog(None,"Import or Export HMS Calibrations","Calibration Library",JOptionPane.PLAIN_MESSAGE,None,selections,selections[0])
		print HMSCalLibSelected
		
		if str(HMSCalLibSelected) == "None" :
			print("User canceled program")
		
################## Stection-End ######################################################################
		
################## Stection-Start ####################################################################
################################################################################################
####	Menu and dialogs for Importing HMS calibration flies from calibration library		####
################################################################################################
		if HMSCalLibSelected == "Import HMS Calibrations" :
			## Define calibration_library directory
			HMS_Calibration_Library_Directory_os = os.path.join(forecastDirectory,'..\\..\\..\\watershed\\'+Watershed+'\\hms\\forecast\\calibration_library')
			os.chdir(HMS_Calibration_Library_Directory_os)
			
			## Filter for calibration files that are only associated to active HMS alternative
			Available_HMS_Calibration_Files = glob.glob(''+ActiveHMSAlt+'*')
			if len(Available_HMS_Calibration_Files) == 0 :
				MessageBox.showError("No calibrations files for active HMS alternative avaiable in calibration library.", "HMS Calibration File Import")
			else :
				## Create dialog selecator of filtered calibration files
				HMSFcstCalSelected = JOptionPane.showInputDialog(None,"Select Calibration","HMS Archived Calibration",JOptionPane.PLAIN_MESSAGE,None,Available_HMS_Calibration_Files,Available_HMS_Calibration_Files[0])
				print HMSFcstCalSelected
				
				if str(HMSFcstCalSelected) == "None" :
					print("User canceled program")
				else :
					Selected_HMS_Calibration_File_os = os.path.join(forecastDirectory,'..\\..\\..\\watershed\\'+Watershed+'\\hms\\forecast\\calibration_library\\'+HMSFcstCalSelected+'')
					Selected_HMS_Calibration_File = Selected_HMS_Calibration_File_os.replace("\\", "/")
					
					## Close forecast, copy selecated calibration file to forecast directory, and then reopen forecast
					tab.closeForecast()
					shutil.copy2(Selected_HMS_Calibration_File, Current_HMS_fcstFileName)
					tab.openForecastAction()
					
					MessageBox.showInformation("HMS forecast calibration "+HMSFcstCalSelected+" file copied to active forecast.", "HMS Calibration File Import")
			
################## Stection-End ######################################################################
		
################## Stection-Start ####################################################################
############################################################################################
####	Menu and dialogs for Exporting HMS calibration flies to calibration library		####
############################################################################################
		elif HMSCalLibSelected == "Export HMS Calibrations" :
			## Dialog to assign name for calibration file
			Calibration_Name = JOptionPane.showInputDialog(
				None,
				"Calibration Name (default is forecast date & time)",
				"Save HMS Calibration to Library",
				JOptionPane.QUESTION_MESSAGE,None,None,fcst_time_string)
				
			if str(Calibration_Name) == "None" :
				print("User canceled program")
			else :
				HMS_Calibration_Library_Directory_os = os.path.join(forecastDirectory,'..\\..\\..\\watershed\\'+Watershed+'\\hms\\forecast\\calibration_library\\'+ActiveHMSAlt+'_'+Calibration_Name+'.forecast')
				HMS_Calibration_Library_Directory = HMS_Calibration_Library_Directory_os.replace("\\", "/")
				
				## Check if file name exists in calibration library directory 
				if os.path.exists(HMS_Calibration_Library_Directory) :
					FileExist = JOptionPane.showConfirmDialog(None, "A calibration file named "+Calibration_Name+" exist.  Overwrite existing file?","Calibration File Exists", JOptionPane.YES_NO_OPTION)
					if FileExist == 0 :
						shutil.copy2(Current_HMS_fcstFileName, HMS_Calibration_Library_Directory)
						MessageBox.showInformation("HMS forecast calibration file copied and replaced "+Calibration_Name+" in calibration library.", "HMS Calibration File")
						print("File overwritten")
					else :
						MessageBox.showError("HMS forecast calibration file NOT copied to calibration library.  Use another name different than "+Calibration_Name+".", "HMS Calibration File")
						print("File not copied")
				else :
					shutil.copy2(Current_HMS_fcstFileName, HMS_Calibration_Library_Directory)
					MessageBox.showInformation("HMS forecast calibration file copied to calibration library.", "HMS Calibration File")
		
################## Stection-End ######################################################################
		
	except Exception, e : 
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
		formatted_lines = traceback.format_exc().splitlines()
		TracebackStr = '\n'.join(formatted_lines)
		MessageBox.showError(TracebackStr, 'Python Error')
	except java.lang.Exception, e : 
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
		formatted_lines = traceback.format_exc().splitlines()
		TracebackStr = '\n'.join(formatted_lines)
		MessageBox.showError(TracebackStr, 'Java Error')
finally:
	cwmsFile.done()
