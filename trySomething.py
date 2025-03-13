import scispacy
import spacy

# Ensure the correct SciSpaCy model is downloaded and installed before running
nlp = spacy.load("en_core_sci_sm")

text = """
Myeloid derived suppressor cells (MDSC) are immature 
myeloid cells with immunosuppressive activity. 
They accumulate in tumor-bearing mice and humans 
with different types of cancer, including hepatocellular 
carcinoma (HCC).
"""

text2 = """GATA46 directly activates HAND2 expression. 
GATA46 enhances HEY2 expression. 
IRX4 expression is lost by HAND2 knockout. 
IRX4 contributes to activating MYL2. 
IRX4 activates HAND2. 
NR2F2 represses IRX4 gene expression. 
NR2F2 represses MYL2. 
NR2F2 represses HEY2 gene. 
NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. 
Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. 
Expression of HEY2 is increased by NOTCH signalling.
"""

doc = nlp(text2)

# Print sentence segmentation
print(list(doc.sents))

# Print extracted entities
print([ent.text for ent in doc.ents])

# Dependency visualization
from spacy import displacy

# Render dependency parse
# If running in a Jupyter Notebook:
# displacy.render(next(doc.sents), style='dep', jupyter=True)

# If running as a script, use this instead:
displacy.serve(next(doc.sents), style='dep')
