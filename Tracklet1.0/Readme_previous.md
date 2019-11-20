# LongVM and Tracklet 1.0
This file describes older versions of the code. 


### Tracklet LongVM

The master configuration file for long VM project is wires.input.longVM_sector

* Generate reduced LongVM project configuration if needed:

      ./SubProject_longVM.py -r <region> -s <seedings>

      ./SubProject_longVM.py -h  for help

   It by default reads the master config file 'wires.input.longVM_sector' and generates a smaller scale project configuration 'wires.reduced', based on the user specified detector region (via option -r) and seeding pairs (via option -s).
   Choices for argument <region> are: 'A' (entire tracker), 'L' (barrel only), 'D' (disk only), 'H' (hybrid region).
   Choices for argument <seedings> are: 'L1L2', 'L3L4', 'L5L6', 'D1D2', 'D3D4', 'D1L1', 'D1L2', as well as any combinations of them. Note that in case the specified detector region is not entire detector, only seedings feasible in that region are allowed.

* Create connections for LongVM project:

       ./WiresLongVM.py <wires>

   Its input file <wires> could be either wires.input.longVM_sector for a full project or wires.reduced generated from previous step for a smaller scale project.
   This script will produce three output files: wires.dat, memorymodules.dat and processingmodules.dat. They could be used either as configuration files in emulation or in the next step to generate top level processing verilog modules for firmware.

* To generate verilog top level module:
   
       ./generator_longVM.py

       ./generator_longVM.py -h  for help

   It reads in wires.dat, memorymodules.dat and processingmodules.dat by default, and generates a verilog module by default named Tracklet_processing.v
   Copy Tracklet_processing.v to firmware/TrackletProject/SourceCode/ in order to implement it in firmware project.

-----------------------------------------------------------------

### Tracklet 1.0

* Reduce the project if needed:

      python SubProject.py D3 (or D3D4, D5D6, D3D4D5D6, etc.)

   This will generate an output file: wires.reduced   


* Create the connections:

      python Wires.py wires.input.D3

(or some other input file like wires.input.fullsector or wires.reduced generated from the previous step)


* To generate verilog top level code:

      python generator.py D3(or D3D4, D5, etc.)

-----------------------------------------------------------------
