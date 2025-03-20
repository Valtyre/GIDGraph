import spacy
from spacy.tokenizer import Tokenizer
import scispacy
import numpy as np
from spacy.tokens.doc import Doc
from nlp.biobert_genetic_ner import extract_genes
import re


"""
    IRX4 expression is lost by HAND2 knockout. 
    GATA46 enhances HEY2 expression. 
    GATA46 directly activates HAND2 expression. 
    IRX4 contributes to activating MYL2. 
    IRX4 activates HAND2. 
    NR2F2 represses IRX4 gene expression. 
    NR2F2 represses MYL2. 
    NR2F2 represses HEY2 gene. 
    NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells.
    Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. 
    Expression of HEY2 is increased by NOTCH signalling.
"""
"""TBX5 enhances GATA4 expression.
GATA6 directly activates NKX2-5 expression.
MEF2C contributes to activating HAND1.
HEY2 represses IRX3 gene expression.
NOTCH signaling activates JAG1 expression.
IRX3 represses HAND2.
NKX2-5 enhances MYH6 expression.
TBX20 binds to regulatory regions of MYL7 and promotes its expression.
Expression of HEY2 is repressed by TBX5.
Ectopic HAND2 expression is observed in GATA4 knockout embryonic hearts.
GATA4 and NKX2-5 synergistically activate BMP10 expression.
HEY2 expression is negatively regulated by MEIS1.
FOXC1 represses HAND1 gene expression.
GATA6 enhances BMP4 expression in cardiac progenitors.
Loss of TBX5 leads to decreased expression of NPPA.
BMP10 activates expression of HAND2 in cardiac development.
IRX4 and TBX5 cooperatively activate MYH7 expression.
NOTCH signaling inhibits TBX20 expression in the developing heart.
NR2F2 represses NKX2-5 transcription.
GATA4 directly activates MEF2C expression.
"""
def geneTokenizer(nlp):
    infix_re = re.compile(r'''[.\,\?\!\:\;\…]''')  # Keep default infix rules but remove hyphens splitting
    prefix_re = re.compile(r'''^[\(\[\{\<\']''')  # Keep default prefix rules
    suffix_re = re.compile(r'''[\)\]\}\>\'"]$''')  # Keep default suffix rules

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                     suffix_search=suffix_re.search,
                     infix_finditer=infix_re.finditer,
                     token_match=None)

def get_compound_phrase(head_token):
    # Collect tokens that form the compound: left children with dep "compound" or "amod"
    modifiers = [child for child in head_token.lefts if child.dep_ in ["compound", "amod"]]
    # Sort by their position in the sentence to maintain correct word order
    modifiers = sorted(modifiers, key=lambda t: t.i)
    # Return the full phrase including the head token
    return " ".join([t.text for t in modifiers] + [head_token.text])



def main_function(doc: Doc, gene_list: list) -> list[tuple[str, str, str, str]]:

        
    relationships: list[tuple[str, str, str, str]] = []

    for sent in doc.sents: 

        print("\nSentence:" , sent, "\n")

        root = sent.root.text
        actor = None 
        target = None
        flip = False

        for token in sent:
            print(token, token.dep_, token.head, token.pos_)

            # Gene list 
            if token.text in gene_list: 
                # Compound 
                if token.dep_ == "compound":
                    phrase = get_compound_phrase(token.head)
                    print(f"Compound phrase: {phrase}")
                    # print(f"Head token: '{token.head.text}' with dependency: {token.head.dep_}\n")
                    if actor is None and (token.dep_ in ["nsubj", "nsubjpass", "agent", "attr"] or token.head.dep_ in ["nsubj", "nsubjpass", "agent", "attr"]):
                        actor = phrase
                    elif target == None and token.head.dep_ in ["dobj", "attr", "prep", "nmod"]:
                        target = phrase

                # ACTOR 
                elif actor == None and token.dep_ in ["nsubj", "nsubjpass", "agent", "attr"] or token.head.dep_ in ["nsubj", "nsubjpass", "agent", "attr"]:
                    actor = token.text

                
                # TARGET 
                elif target == None and token.dep_ in ["dobj", "attr", "prep", "nmod"] or token.head.dep_ in ["dobj", "attr", "prep"]:
                    target = token.text


            # Extra cases
            if token.dep_ == "conj" and token.head.text in gene_list:
                actor = token.head.text + " and " + token.text

            elif token.dep_ == "advcl" and token.head.dep_ in ["ROOT", "contributes"]:
                root = token.text
            elif token.dep_ == "case":
                if token.text in ["by", "via", "in"]:
                    # Get the actual head token (e.g., "knockout" in "GENE knockout")
                    head_token = token.head

                    # Check if the head token has a compound that is in the gene list
                    gene_compound = next((child.text for child in head_token.lefts if child.dep_ == "compound" and child.text in gene_list), None)

                    # Flip if either the head itself is in gene_list or the compound gene exists
                    if head_token.text in gene_list or gene_compound:
                        flip = True
            elif token.dep_ == "advmod" and token.head.lemma_ in ["regulate", "control"]:
                if token.text in ["negatively"]:
                    root = "represses"
                if token.text in ["positivly"]:
                    root = "activates"

            elif token.dep_ == "appos" and token.head.text in gene_list:
                    actor = token.head.text
                
            elif token.dep_ == "relcl" and token.head.text in gene_list:
                    relationships.append((token.head.text, token.lemma_, target, sent))
                    continue

        if flip and actor and target:  
            actor, target = target, actor

             

        print([actor, root, target])
        relationships.append([actor, root, target, sent])

    return relationships
                


def entities(doc: Doc):

    entities = []
    for ent in doc.ents:
        print(ent.text, ent.label_)
        entities.append((ent.text, ent.label_))


    return entities



def to_parser(interactions: list[tuple[str, str, str, str]], gene_list: list[str]) -> list[tuple[str, str, str, str]]:
    """Processes interactions by ensuring multiple genes are handled correctly and normalizing verbs."""
    
    activation_verbs = {"activating", "activate", "enhances", "induces", "stimulates", "upregulates", "increased", "observed", "promotes"}
    repression_verbs = {"represses", "repressed", "inhibits", "downregulates", "suppresses", "lost"}

    parsed_interactions = []  # Store cleaned interactions

    for i in range(len(interactions)):
        knockout = False
        if None in interactions[i]:
            # parsed_interactions. append(interactions[i])
            continue

        a, r, t, extra = interactions[i]  # Unpack tuple

        print (a.split() + t.split())
        if "knockout" in a.split() + t.split():
            knockout = True

        # Handle multiple genes in subject (a) or target (t)
        a_genes = [gene for gene in gene_list if gene in a.split()]
        t_genes = [gene for gene in gene_list if gene in t.split()]

        # Standardize the relation type (r)
        if r in activation_verbs:
            r = "activates"
        elif r in repression_verbs:
            r = "inhibits"

        if knockout and r == "activates": 
            r = "inhibits"
        elif knockout and r == "inhibits":
            r = "activates"

        

        # Create separate interactions for each subject-target pair
        for a_gene in a_genes:
            for t_gene in t_genes:
                parsed_interactions.append((a_gene, r, t_gene, extra))
        
        inter = ''
        for i, interaction in enumerate(parsed_interactions): 
            if interaction[0] != None and interaction[1] in ["activates", "inhibits"] and interaction[2] != None:
                inter += f" {interaction[0]} {interaction[1]} {interaction[2]}. "
            # elif interaction != None: 
            #     print('\033[31m', f"Interaction {i+1}:", interaction[3],'\033[36m', interaction[0], interaction[1], interaction[2])

    return inter


def nlp_runner(text: str) -> str:
    nlp = spacy.load("en_ner_bionlp13cg_md")
    nlp.tokenizer = geneTokenizer(nlp)
    doc = nlp(text)

    genes = extract_genes(text)
    interactions =  to_parser(main_function(doc, genes), genes)

    return interactions


if __name__ == '__main__':

    nlp = spacy.load("en_ner_bionlp13cg_md")
    # nlp_model_1 = spacy.load("en_core_sci_scibert")

    nlp.tokenizer = geneTokenizer(nlp)

    text1 = """GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout.IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling."""

    text2 ="TBX5 enhances GATA4 expression. GATA6 directly activates NKX2-5 expression. MEF2C contributes to activating HAND1. HEY2 represses IRX3 gene expression. NOTCH signaling activates JAG1 expression. IRX3 represses HAND2. NKX2-5 enhances MYH6 expression. TBX20 binds to regulatory regions of MYL7 and promotes its expression. Expression of HEY2 is repressed by TBX5. Ectopic HAND2 expression is observed in GATA4 knockout embryonic hearts. GATA4 and NKX2-5 synergistically activate BMP10 expression. HEY2 expression is negatively regulated by MEIS1. FOXC1 represses HAND1 gene expression. GATA6 enhances BMP4 expression in cardiac progenitors. Loss of TBX5 leads to decreased expression of NPPA. BMP10 activates expression of HAND2 in cardiac development. IRX4 and TBX5 cooperatively activate MYH7 expression. NOTCH signaling inhibits TBX20 expression in the developing heart. NR2F2 represses NKX2-5 transcription. GATA4 directly activates MEF2C expression."
    
    text = text1
    doc = nlp(text)

    genes = extract_genes(text)



    interactions =  to_parser(main_function(doc, genes), genes)



    print(genes)
    print(interactions)
    # for i, interaction in enumerate(interactions): 
    #     if interaction[0] != None and interaction[1] in ["activates", "inhibits"] and interaction[2] != None:
    #         print('\033[0m', f"Interaction {i+1}:", interaction[0], interaction[1], interaction[2], "\t\tOriginal:", interaction[3])
    #     elif interaction != None: 
    #         print('\033[31m', f"Interaction {i+1}:", interaction[3],'\033[36m', interaction[0], interaction[1], interaction[2])