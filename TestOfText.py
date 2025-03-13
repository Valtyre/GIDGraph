import spacy

# Load a scientific language model
nlp = spacy.load("en_core_sci_sm")  

text = """GATA46 directly activates HAND2 expression. 
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

# Process text
doc = nlp(text)

# Print out identified words and their types
for ent in doc.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}")

    
#for token in doc:
#    print(f"Word: {token.text}, Dependency: {token.dep_}, Head: {token.head.text}, POS: {token.pos_}")
