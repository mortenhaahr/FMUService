from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
# import numpy as np
import shutil



class FMUInterface:
    def __init__(self,filename,start_time) -> None:
        model_description = read_model_description(filename)

        self.vrs = {}
        # collect the value references
        for variable in model_description.modelVariables:
            self.vrs[variable.name] = variable.valueReference


        self.unzipdir = extract(filename)

        self.fmu = FMU2Slave(guid=model_description.guid,
                        unzipDirectory=self.unzipdir,
                        modelIdentifier=model_description.coSimulation.modelIdentifier,
                        instanceName='instance1')
        
        self.fmu.instantiate()
        self.fmu.setupExperiment(startTime=start_time)
        self.fmu.enterInitializationMode()
        self.fmu.exitInitializationMode()

    def callback_doStep(self, vars, time, step_time):
        self.fmu.setReal(self.vrs['input'], vars)
        self.fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_time)

    def getValues(self):
        return self.fmu.getReal(self.vrs)
    
    def close(self):
        self.fmu.terminate()
        self.fmu.freeInstance()
        shutil.rmtree(self.unzipdir, ignore_errors=True)
