from fmuinterface import FMUInterface

f = FMUInterface('m2.fmu', 0)
print(f.getValues())
f.callback_doStep([25,26],0, 1)
print(f.getValues())
f.callback_doStep([25,135],0, 1)
print(f.getValues())
f.close()