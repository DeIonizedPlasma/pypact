import os
import subprocess
import pypact as pp
import matplotlib.pyplot as plt


files_filename = "files"
input_filename = "run.i"
fluxes_filename = "fluxes"
group = 709
inventory = [('Fe', 0.89), ('Se', 0.11)]
fispact_exe = os.getenv('FISPACT', os.path.join(os.sep, 'opt', 'fispact', 'bin', 'fispact'))
nuclear_data_base = os.getenv('NUCLEAR_DATA', os.path.join(os.sep, 'opt', 'fispact', 'nuclear_data'))

# files file
ff = pp.FilesFile(base_dir=nuclear_data_base)
ff.setXS('TENDL2015')
ff.setFissionYield('GEFY52')
ff.setProbTab('TENDL2015')
ff.setDecay('DECAY')
ff.setRegulatory('DECAY')
ff.setGammaAbsorb('DECAY')
ff.fluxes = fluxes_filename
for invalid in ff.invalidpaths():
    print("FilesFile:: missing file: {}".format(invalid))

# input file
id = pp.InputData(name=input_filename.strip('.i'))
id.overwriteExisting()
id.enableJSON()
id.approxGammaSpectrum()
#id.collapse(group)
#id.condense()
id.outputHalflife()
id.outputHazards()
id.useNeutron()
id.enableMonitor()
id.outputInitialInventory()
id.setLogLevel(pp.LOG_SEVERITY_ERROR)
id.setAtomsThreshold(1.0e-3)
id.setDensity(7.875)
id.setMass(1.0e-3)
for e, r in inventory:
    id.addElement(e, percentage=r*100.0)
id.addIrradiation(300.0, 1.1e12)
id.addCooling(10.0)
id.addCooling(100.0)
id.addCooling(1000.0)
id.addCooling(10000.0)
id.addCooling(100000.0)
id.validate()

# fluxes file
# set monoenergetic flux at 14 MeV for group 709
flux = pp.FluxesFile(name="14 MeV (almost) monoenergetic", norm=1.0)
flux.setGroup(group)
flux.setValue(12.0e6, 0.1)
flux.setValue(13.0e6, 0.4)
flux.setValue(14.0e6, 1.0)
flux.validate()

# write all files
pp.serialize(id, input_filename)
pp.serialize(ff, files_filename)
pp.serialize(flux, fluxes_filename)

# run fispact
proc = subprocess.check_call("{} {} {}".format(fispact_exe, input_filename.strip('.i'), files_filename), shell=True)

# check for log file
logfile = "{}.log".format(input_filename.strip('.i'))
if not os.path.isfile(logfile):
    raise RuntimeError("No log file produced.")

# plot the final inventory ignoring the initial elements
elements = {}
outfile = "{}.json".format(input_filename.strip('.i'))
with pp.Reader(outfile) as output:
    ignore_elements = list(map(list, zip(*inventory)))[0]
    print(ignore_elements)
    for n in output[-1].nuclides:
        if n.element not in ignore_elements:
            if n.element in elements:
                elements[n.element] += n.grams
            else:
                elements[n.element] = n.grams

    total_grams = sum([g for e, g in elements.items()])
    for e, g in elements.items():
        print("{} {:.2f}%".format(e, g*100.0/total_grams))

    labels, values = list(zip(*(list(elements.items()))))
    plt.pie(list(values), labels=list(labels), autopct='%2.2f%%', shadow=False)
    plt.show()
