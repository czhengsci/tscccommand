from pymacy.fireworks.md_workflows import MDWorkflowManager
from pymatgen.transformations.standard_transformations import SupercellTransformation
from pymatgen.transformations.site_transformations import RemoveSitesTransformation
from fireworks.core.launchpad import LaunchPad
import os

wfm = MDWorkflowManager(49, category="tscc-condo")
wf = wfm.add_temperature([1], [900])
lpad = LaunchPad.from_file(os.path.join(os.environ["HOME"], ".fireworks", "my_launchpad.yaml"))
lpad.add_wf(wf)
