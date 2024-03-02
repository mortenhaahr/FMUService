from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from collections import OrderedDict
import shutil


# Class has self.fmu with the fmu
#          self.vrs with the variables references
#          self.unzipdir with the pointer the unzipdirectory so it can close
class FMUInterface:
    def __init__(self, filename, start_time) -> None:
        model_description = read_model_description(filename)

        self.inputs = OrderedDict()
        self.outputs = OrderedDict()
        for variable in model_description.modelVariables:
            if variable.causality == "input":
                self.inputs[variable.name] = variable
            elif variable.causality == "output":
                self.outputs[variable.name] = variable
            else:
                raise Exception("Unhandled causality type")

        self.unzipdir = extract(filename)

        self.fmu = FMU2Slave(
            guid=model_description.guid,
            unzipDirectory=self.unzipdir,
            modelIdentifier=model_description.coSimulation.modelIdentifier,
            instanceName="instance1",
        )

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
        mappedInputs = self.mapInputsToValues(vars)

        # Call the correct setMethod for each input type that was provided
        for inputTypeDict in filter(lambda kv: kv[1] != {}, mappedInputs.items()):
            setMethod = getattr(self.fmu, f"set{inputTypeDict[0]}")
            fmuVarsDict = inputTypeDict[1]
            setMethod(fmuVarsDict.keys(), fmuVarsDict.values())

        self.fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_time)

    def mapInputsToValues(self, values):
        # TODO: Would be smarter to do this on __init__ and then only update the values...
        res = {"Integer": {}, "Real": {}, "Boolean": {}, "String": {}}
        for pair in zip(self.inputs.values(), values):
            type = pair[0].type
            valueReference = pair[0].valueReference
            res[type][valueReference] = pair[1]
        return res

    # Gets all the values
    def getValues(self):
        # TODO: Hardcoded to m2.fmu...
        return [
            self.fmu.getInteger(
                [
                    self.inputs["x1"].valueReference,
                    self.inputs["x2"].valueReference,
                    self.outputs["_output"].valueReference,
                ]
            )
        ]

    # Closes the fmu (REQUIRED)
    def close(self):
        self.fmu.terminate()
        self.fmu.freeInstance()
        shutil.rmtree(self.unzipdir, ignore_errors=True)
