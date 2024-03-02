from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import shutil


# Class has self.fmu with the fmu
#          self.vrs with the variables references
#          self.unzipdir with the pointer the unzipdirectory so it can close
class FMUInterface:
    def __init__(self, fileName: str, startTime, instanceName="instance1") -> None:
        # TODO: Support reference by valueReference instead

        model_description = read_model_description(fileName)

        self.variables = {
            "input": {"Integer": {}, "Real": {}, "Boolean": {}, "String": {}},
            "output": {"Integer": {}, "Real": {}, "Boolean": {}, "String": {}},
        }
        self.inputs = self.variables["input"]  # Reference to the inputs
        self.outputs = self.variables["output"]  # Reference to the outputs

        # Categorize variable based on causality, type and index by name
        for variable in model_description.modelVariables:
            causality = variable.causality
            if not (causality == "input" or causality == "output"):
                raise Exception(
                    "Unhandled causality type"
                )  # Only support input and output for now
            self.variables[causality][variable.type][variable.name] = variable

        self.unzipdir = extract(fileName)

        self.fmu = FMU2Slave(
            guid=model_description.guid,
            unzipDirectory=self.unzipdir,
            modelIdentifier=model_description.coSimulation.modelIdentifier,
            instanceName=instanceName,
        )

        # Initialization of the FMU
        self.fmu.instantiate()
        self.fmu.setupExperiment(startTime=startTime)
        self.fmu.enterInitializationMode()
        self.fmu.exitInitializationMode()

    # Does a step
    #   time: starting time
    #   step_time: simulation time step
    def callback_doStep(self, time, step_time):
        # TODO: Make sure currentCommunicationPoint makes sense
        self.fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_time)

    def setInputs(self, vars: dict) -> None:
        """Takes the nested dict `vars` and assigns the values to the FMU inputs.
        vars: Nested dict with the format {type1: {varName1: value2, varName2: value2}, type2: {varname3: value3}}
        """
        for type, varsDict in vars.items():
            setMethod = getattr(self.fmu, f"set{type}")
            references = [
                self.inputs[type][name].valueReference for name in varsDict.keys()
            ]
            setMethod(references, varsDict.values())

    # Gets all the values
    def getValues(self):
        # TODO: Hardcoded to m2.fmu...
        return [
            self.fmu.getInteger(
                [
                    self.inputs["Integer"]["x1"].valueReference,
                    self.inputs["Integer"]["x2"].valueReference,
                    self.outputs["Integer"]["_output"].valueReference,
                ]
            )
        ]

    # Closes the fmu (REQUIRED)
    def close(self):
        self.fmu.terminate()
        self.fmu.freeInstance()
        shutil.rmtree(self.unzipdir, ignore_errors=True)
