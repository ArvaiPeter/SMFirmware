# Simultaenous Multihead Firmware
The SM fimware is a Klipper fork modified to be able to run multiple printheads in parallel. Klipper - due to its host-client separation, and RPC-like communication - provides a solid base for printers with multiple independent printheads, however the host software needs some redesign.

## Modifications
 - ### Printer Objects
    Functional components (printer objects) of the host software are stored at the topmost (printer) object in a list. This architecture is fine for conventional printers, but some printer objects need to defined per printhead (for example the gcode_move object, which stores the position of the toolhead)  
    Printher objects should be restructured into a tree-like stucture  
      
    > printer  
    &emsp; > gcode, reactor, ...  
    &emsp; > tool 1  
    &emsp;&emsp; > gcode_move, bed_mesh, ...  
    &emsp; > tool 2  
    &emsp;&emsp; > gcode_move, bed_mesh, ...  
    &emsp; > environment  
    &emsp;&emsp; > printbed, heating, ...  

    
