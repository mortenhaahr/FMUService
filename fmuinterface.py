from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
# import numpy as np
import shutil


#Class has self.fmu with the fmu
#          self.vrs with the variables references
#          self.unzipdir with the pointer the unzipdirectory so it can close
class FMUInterface:
    def __init__(self,filename,start_time) -> None:
        model_description = read_model_description(filename)

        self.vrs = {}
        for variable in model_description.modelVariables:
            self.vrs[variable.name] = variable.valueReference


        self.unzipdir = extract(filename)
        
        self.fmu = FMU2Slave(guid=model_description.guid,
                        unzipDirectory=self.unzipdir,
                        modelIdentifier=model_description.coSimulation.modelIdentifier,
                        instanceName='instance1')
        
        # Initialization of the FMU
        self.fmu.instantiate()
        self.fmu.setupExperiment(startTime=start_time)
        self.fmu.enterInitializationMode()
        self.fmu.exitInitializationMode()

    # Does a step 
    #   vars: array of int
    #   time: starting time
    #   step_time: simulation time step
    def callback_doStep(self, vars, time, step_time):
        self.fmu.setInteger([self.vrs['x1'],self.vrs['x2']], vars)
        self.fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_time)

    # Sets some values
    #   vars: array
    def setValues(self, vars):
        self.fmu.setInteger([self.vrs['x1'],self.vrs['x2']], vars)


    # Gets all the values
    def getValues(self):
        return [self.fmu.getInteger([self.vrs['x1'],self.vrs['x2'],self.vrs['_output']])]
    
    # Closes the fmu (REQUIRED)
    def close(self):
        self.fmu.terminate()
        self.fmu.freeInstance()
        shutil.rmtree(self.unzipdir, ignore_errors=True)
