
# coding: utf-8

# In[10]:

from pymatgen.core.structure import Structure
from pymatgen.io.vaspio.vasp_output import Vasprun
from pymatgen.alchemy.filters import SpecieProximityFilter
import operator

structuredic = {}
for i in range(61):
    vobj = Vasprun("Na6Co8O16_%d/vasprun.xml.relax2.gz"%i)
    structuredic[('Na6Co8O16_%d'%i)]=(vobj.final_energy/30)
        
#Sort and return structure list based on the order of each structure's energy per atom 
structuredicsorted = sorted(structuredic.items(),key=operator.itemgetter(1))

#Return the structure file ID with lowest energy per atom
print structuredicsorted[0][0]


# In[ ]:



