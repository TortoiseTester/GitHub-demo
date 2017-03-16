#----------------------------------------------------------
# Module Name        : Stability Test
# Objective          : SWC Stability Test..
# TC ID              : 09
# TC Path            : Ford_Automation_Gen3/Stability
# Squish Version     : Squish-5.0.2
# QT Version         : QT-5.2.0
# Python version     : Python 2.7.6
# Author             : Aditya Mishra and MANAS and Sumantha and Poorna
# Date of creation   : 24-March-2015
# -------------------------------------------------------- 
import __builtin__
import ExceptionHandler
import General
import CommonCAN
import HMINavigation
import Stability
import time
import Entertainment
import VoiceCommon
import LongHaul
import os
import Logger
import Security
import threading
import squish

     
def precondition():
    testSettings.logScreenshotOnError = True
    testSettings.logScreenshotOnFail = True
    global stTestcaseID, iExecutionTime, iPowerCycles, iIterate_exception
    stTestcaseID, iExecutionTime, iPowerCycles, iIterate_exception = Stability.globalPreCondition()
    #liActiveProcessList = Stability.getActiveProcessList()
    #Security.setSecurityGlobals()
    #Security.nsLogInit(General.getRootPath()+"Shared\\Log\\", str(stTestcaseID) +"_LivePasDebugLog.log")

def setup_environment():
    General.launchApplication()
    
    HMINavigation.goToHome()

def main():   
    try:
        global iIterate_exception, iPowerCycles, analyzer_thread
        start_flag = True
        test_complete_flag = False
        precondition()
        # Rerun iterator
        analyzer_thread = None
        iIterate_exception = 1
        iterator = 0
        fCurrentTime = time.time()
        strCurrentTime = time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime(fCurrentTime))
        tc_root_folder = os.path.join(TC_LOG_PATH, stTestcaseID + "_" + strCurrentTime)
        tc_log_folder = None
        while(iPowerCycles > 0):
            iPowerCycles -= 1
            fCurrentTime = time.time()
            test.log("Execution Starting time",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fCurrentTime)))
            while (time.time() - fCurrentTime <= iExecutionTime):   
                try:
                    iterator+=1
                    if start_flag:
                        setup_environment()
                        test.log("Start iteration: " + str(iIterate_exception) + "\n")
                        tc_log_folder = os.path.join(tc_root_folder, time.strftime('%Y-%m-%d_%H.%M.%S_', time.localtime(time.time())) + str(iIterate_exception))

                        iIterate_exception += 1
                        analyzer_thread = AnalyzerLogThread(threading.current_thread(),
                                                            tc_log_folder)
                        analyzer_thread.start()
                        test.log("Start to run analyzer thread......")
                        start_flag = False
                    # Test actions
                    Stability.stabiltyNavigation()
                    
                    # This section checks if there is an exception occured in Sync and resets in case there is an exception
                    #######################################################################################################################################
                    #bExceptionFound = Security.findIfErrorPresent(str(stTestcaseID) +"_LivePasDebugLog.log", General.getRootPath()+"Shared\\Log\\", ["Some Exception String"])
                    #if bExceptionFound:
                        #raise Exception("Raising a flag, as an exception was found in the log stream")
                    #Stability.telnetAndHMICrashCheck(fCurrentTime, iIterate)
                    #Stability.screenFreezeCheck(fCurrentTime, iIterate)
                    #Stability.activeProcessesCheck(liActiveProcessList, fCurrentTime, iIterate)
                    #######################################################################################################################################
                    
                    # Logging CPU usage
                    #stCPUUSed, stMemoryUsed = Stability.captureCPUUsage(General.getRootPath()+"Shared\\Log\\", "StabilityCpuUsage.log")
                    #Stability.writeToStabilityCSV("stabiltySWC", stTestcaseID, iPowerCycles, iIterate, "Pass", stCPUUSed, stMemoryUsed, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "StabilityCSV")
                    if analyzer_thread.get_event_count() > 0:
                        if analyzer_thread.detected_stopcase_event():
                            test.fail("Sync3EventAnalyzer detected FatalError and Stop test case!\n")
                            handleLogFatalEvent(analyzer_thread, tc_log_folder)
                            start_flag = True
                            test_complete_flag = True
                            break
                        else:
                            test.fail("Sync3EventAnalyer detected Fatal error!")
                            handleLogFatalEvent(analyzer_thread, tc_log_folder)
                            start_flag = True
                            continue
                        
                except FatalError as e:
                    test.fail('Sync3EventAnalyer detected FatalError!')
                    handleLogFatalEvent(analyzer_thread, tc_log_folder)
                    start_flag = True      
                
                except StopCaseError as tce:
                    test.fail("Sync3EventAnalyzer detected FatalError and Stop test case!\n")
                    handleLogFatalEvent(analyzer_thread, tc_log_folder)
                    start_flag = True
                    test_complete_flag = True
                    # not finish here, just break inside while loop
                    break

                except Exception as e:
                    analyzer_thread.enable_raise_exception_again(False)
                    test.log("Test Case Exception %s captured!\n" % e.args)
                    custom_sleep(5)
                    if analyzer_thread.get_event_count() > 0:
                        if analyzer_thread.detected_stopcase_event():
                            test.fail("Sync3EventAnalyzer detected FatalError and Stop test case!\n")
                            handleLogFatalEvent(analyzer_thread, tc_log_folder)
                            start_flag = True                            
                            test_complete_flag = True
                            break                                                      
                        else:
                            test.fail("Sync3EventAnalyer detected Fatal error!")
                            handleLogFatalEvent(analyzer_thread, tc_log_folder)
                            start_flag = True
                            continue
                    if e:
                       ExceptionHandler.doException(e.args)
                    General.launchApplication()   
                    analyzer_thread.enable_raise_exception_again(True)
#                 except Exception as e:
#                     ExceptionHandler.doException(e.args)
#                     if bExceptionFound:
#                         stCPUUSed, stMemoryUsed = Stability.exceptionChecks(fCurrentTime, liActiveProcessList, iIterate)
#                     else:
#                         Security.findIfErrorPresent(str(stTestcaseID) +"_LivePasDebugLog.log", General.getRootPath()+"Shared\\Log\\", ["Some Exception String"])
#                         stCPUUSed, stMemoryUsed = Stability.exceptionChecks(fCurrentTime, liActiveProcessList, iIterate)
#                     Stability.writeToStabilityCSV("stabiltySWC", stTestcaseID, iPowerCycles, iIterate, "Fail", stCPUUSed, stMemoryUsed, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "StabilityCSV")
#                     analyzer_thread.enable_raise_exception_again(True)
    except Exception as e:
        ExceptionHandler.doException(e.args)
            
    finally:
        if analyzer_thread and not test_complete_flag:
            analyzer_thread.stop()
            test.log("Sync3EventAnalyzer reset test environment for log copy!")
            _reset_environment(analyzer_thread)
            
            test.log("Sync3EventAnalyzer Copy target logs now!")
            log_transfer = LogFolderTransfer()
            log_transfer.download_log_folder(dest=tc_log_folder)
            test.log("Sync3EventAnalyzer Copy target logs finished!") 
        Logger.stopLog()        
        test.log("All Test Cycles Complete")
        
def handleLogFatalEvent(analyzer_thread, target_log_dest):
    # Disable exception raise from S3EA to avoid the exception raise again to interrupt this handle.
    analyzer_thread.enable_raise_exception_again(False)
    
    s = analyzer_thread.get_current_fatalerror()
    test.log("Structure of detected fatal errors show as below: \n{0}\n".format(s)) 
    
    analyzer_thread.stop()
    
    test.log("Sync3EventAnalyzer Reset SYNC for target log copy without any telnet connection problem!\n") 
    _reset_environment(analyzer_thread)
    
    test.log("Sync3EventAnalyzer Copy target logs now!")
    log_transfer = LogFolderTransfer()
    log_transfer.download_log_folder(dest=target_log_dest)
    test.log("Sync3EventAnalyzer Copy target logs finished!")    
    
    test.log("Sync3EventAnalyzer Reset SYNC for environment cleanup!------done finished\n") 
    _reset_environment(analyzer_thread) 
    
def _reset_environment(analyzer_thread):
    # cleanup will reset APIM
    try:
        
        hAppContext = squish.applicationContext("fordhmi")
        bStatus = hAppContext.isRunning
        #Check for the application status (Calling attachToApplication API on already attached application will raise exception) 
        if (bStatus == True):
            hAppContext.detach()
    
        test.log("Sync3EventAnalyzer Reset SYNC Now!\n") 
        CommonCAN.resetECU()
        
        test.log("Sync3EventAnalyzer Wait for target IP available!\n") 
        # Wait for SYNC launch
        RemoteTarget().wait_ip_available(30)
    except Exception as e:
        test.log("reset_environment Exception: %s" % str(e))
    
def custom_sleep(time_in_seconds):
    while time_in_seconds >= 0:
        time.sleep(1)
        time_in_seconds -= 1    
