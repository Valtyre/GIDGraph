import spacy
from spacy.tokenizer import Tokenizer
import scispacy
import numpy as np
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from .biobert_genetic_ner import extract_genes
import re

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




def matcher(doc: Doc, gene_list: list) -> list[tuple[str, str, str, Span]]:

        
    relationships: list[tuple[str, str, str, str]] = []

    for sent in doc.sents: 

        print("\nSentence:" , sent, "\n")

        root = sent.root.lemma_
        actor = None 
        target = None
        flip = False


        for token in sent:
            # print(token, '\033[31m', token.dep_, '\033[32m', token.head, '\033[93m', token.pos_, '\033[95m', token.lemma_, "CHILDREN:", [child.text for child in token.children],'\033[0m' )

            # Gene list 
            if token.text in gene_list: 
                # Compound 
                if token.dep_ == "compound":
                    phrase = get_compound_phrase(token.head)
                    # print("Compound phrase:", '\033[36m', phrase, '\033[0m')
                    if (actor == None or token.text == actor) and (token.dep_ in ["nsubj", "nsubjpass", "agent", "attr"] or token.head.dep_ in ["nsubj", "nsubjpass", "agent", "attr"]):
                        actor = phrase
                    elif (target == None or token.text == target) and (token.head.dep_ in ["dobj", "attr", "prep", "nmod"]):
                        target = phrase

                # ACTOR 
                elif actor == None and (token.dep_ in ["nsubj", "nsubjpass", "agent", "attr"] or token.head.dep_ in ["nsubj", "nsubjpass", "agent", "attr"]):
                    actor = token.text

                # TARGET 
                elif target == None and (token.dep_ in ["dobj", "attr", "prep", "nmod"] or token.head.dep_ in ["dobj", "attr", "prep"]):
                    target = token.text


            # Extra cases
            if token.dep_ == "conj" and token.head.text in gene_list:
                if actor != None and token.head.text in actor:
                    actor += " and " + token.text
                elif target != None and token.head.text in target:
                    target += " and " + token.text
            
            elif (token.dep_ == "neg" and token.head.text in root.split()):
                temp = ""
                for verb in root.split():
                    if token.head.text in root.split():
                        temp += f" not {verb}"
                    else: temp += verb
                root = temp

            elif token.dep_ == "amod" and token.head.lemma_ == "expression":
                if token.head.head.dep_ == "ROOT":
                    if token.text in ["reduced"]:
                        root = "inhibit"


            elif token.dep_ == "advcl" and token.head.dep_ in ["ROOT", "contributes"]:
                root += f" {token.lemma_}"

            elif token.dep_ == "case":
                if token.text in ["by", "via", "in"]:
                    head_token = token.head
                    gene_compound = next((child.text for child in head_token.lefts if child.dep_ == "compound" and child.text in gene_list), None)

                    if head_token.text in gene_list or gene_compound:
                        flip = True
            elif token.dep_ == "advmod" and token.head.lemma_ in ["regulate", "control"]:
                if token.text in ["negatively", "reduced"]:
                    root = "repress"
                else:
                    root = "activate"

            elif token.dep_ == "appos" and token.head.text in gene_list:
                    actor = token.head.text
                
            elif token.dep_ == "relcl" and token.head.text in gene_list:
                    relationships.append((token.head.text, token.lemma_, target, sent))
                    continue
            
            elif token.dep_ == "conj" and token.pos_ == "VERB": 
                root += f" {token.lemma_}"

        if flip and actor and target:  
            actor, target = target, actor


        # Shortest path
        if None in [actor, root, target]:
            if actor == None and target == None:
                continue
            if actor == None:
                for token in sent:
                    if token.text in gene_list:
                        actor = token.text
                        continue
            if target == None: 
                for token in sent:
                    if token.text in gene_list:
                        target = token.text
                        continue
                

        relationships.append([actor, root, target, sent])

    return relationships
          


def entities(doc: Doc):

    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))

    return entities



def to_parser(interactions: list[tuple[str, str, str, str]], gene_list: list[str]) -> str:
    """Processes interactions by ensuring multiple genes are handled correctly and normalizing verbs."""
    
    activation_verbs = {"activate", "activation", "enhance", "upregulation", "induce", "stimulate", "upregulate", "increase", "observe", "promote", "auto-activating", "necessary", "regulate"}
    repression_verbs = { "repress", "inhibit", "inhibition", "downregulate", "downregulation", "suppress", "loose", "inactive", "diminish", "lost", "lose"}
    
    parsed_interactions = []  # Store cleaned interactions
    

    for i in range(len(interactions)):
        knockout = False

        a, r, t, sent = interactions[i]  # Unpack tuple

        if "knockout" in a.split() + t.split():
            knockout = True

        # Handle multiple genes in subject (a) or target (t)
        a_genes = [gene for gene in gene_list if gene in a.split()]
        t_genes = [gene for gene in gene_list if gene in t.split()]

        # Standardize the relation type (r)
        for i, verb in enumerate(r.split()):
            if (verb in activation_verbs and r.split()[i-1] != "not") or (verb in repression_verbs and r.split()[i-1] == "not"):
                r = "activates"
            elif verb in repression_verbs and r.split()[i-1] != "not" or (verb in activation_verbs and r.split()[i-1] == "not"):
                r = "inhibits"
            else: 
                for token in sent:
                    if token.lemma_ in activation_verbs:
                        r = "activates"
                    elif token.lemma_ in repression_verbs:
                        r = "inhibits"

        if knockout and r == "activates": 
            r = "inhibits"
        elif knockout and r == "inhibits":
            r = "activates"


        # Create separate interactions for each subject-target pair
        for a_gene in a_genes:
            for t_gene in t_genes:
                parsed_interactions.append((a_gene, r, t_gene, sent))
        
    inter = ''
    for i, interaction in enumerate(parsed_interactions): 
        if interaction[0] != None and interaction[1] in ["activates", "inhibits"] and interaction[2] != None:
            inter += f" {interaction[0]} {interaction[1]} {interaction[2]}. "

    for i, interaction in enumerate(parsed_interactions): 
        if interaction[0] != None and interaction[1] in ["activates", "inhibits"] and interaction[2] != None:
            print('\033[0m', f"Interaction {i+1}:", interaction[0], interaction[1], interaction[2], "    \tOriginal:", interaction[3])
        elif interaction != None: 
            print('\033[31m', f"Interaction {i+1}:", interaction[3],'\033[36m', interaction[0], interaction[1], interaction[2])


    return inter


def nlp_runner(text: str) -> str:
    text = re.sub(r"\.(?!\s)", "-", text)
    nlp = spacy.load("en_ner_bionlp13cg_md")
    nlp.tokenizer = geneTokenizer(nlp)
    doc = nlp(text)

    genes = extract_genes(text)
    print(genes)
    interactions =  to_parser(matcher(doc, genes), genes)

    return interactions


if __name__ == '__main__':

    nlp = spacy.load("en_ner_bionlp13cg_md")
    # nlp_model_1 = spacy.load("en_core_sci_scibert")

    nlp.tokenizer = geneTokenizer(nlp)

    text1 = """If TBX5 knockout is active, then GATA46 is not repressed. GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout.IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling."""

    text2 ="TBX5 does not enhance GATA4 expression. NKE2 activates GATA3 and NTR32. NKE2 and GATA3 activate NTR32. GATA6 directly activates NKX2-5 expression. MEF2C contributes to activating HAND1. HEY2 represses IRX3 gene expression. NOTCH signaling activates JAG1 expression. IRX3 represses HAND2. NKX2-5 enhances MYH6 expression. TBX20 binds to regulatory regions of MYL7 and promotes its expression. Expression of HEY2 is repressed by TBX5. Ectopic HAND2 expression is observed in GATA4 knockout embryonic hearts. GATA4 and NKX2-5 synergistically activate BMP10 expression. HEY2 expression is negatively regulated by MEIS1. FOXC1 represses HAND1 gene expression. GATA6 enhances BMP4 expression in cardiac progenitors. Loss of TBX5 leads to decreased expression of NPPA. BMP10 activates expression of HAND2 in cardiac development. IRX4 and TBX5 cooperatively activate MYH7 expression. NOTCH signaling inhibits TBX20 expression in the developing heart. NR2F2 represses NKX2-5 transcription. GATA4 directly activates MEF2C expression."
    
    text3 = """Gene A activates Gene B. Gene C inhibits the expression of Gene D. Gene E and Gene F cooperatively activate Gene G. Gene H represses Gene I, but only in the presence of Gene J. Gene K is auto-activating. Gene L represses both Gene M and Gene N. Gene O is activated by Gene P but repressed by Gene Q. Gene R is only activated when Gene S is inactive. Gene T and Gene U form a mutual inhibition loop. Gene V is constitutively expressed and not regulated by other genes."""
    
    text4 = "Gene W activates its own expression and that of Gene X. Gene Y represses Gene Z through an intermediate signaling cascade. Gene A1 is activated by Gene B1 only when Gene C1 is also present. Gene D1 represses Gene E1 in response to environmental stress. Gene F1 forms a positive feedback loop with Gene G1. Gene H1 inhibits Gene I1, preventing its expression under normal conditions. Gene J1 activates Gene K1, which in turn represses Gene J1. Gene L1 and Gene M1 both repress Gene N1 independently. Gene O1 is activated by Gene P1 but only after a time delay. Gene Q1 requires both Gene R1 and Gene S1 to be inactive for its expression. Gene T1 indirectly activates Gene U1 by repressing its inhibitor Gene V1. Gene W1 and Gene X1 form a toggle switch where each represses the other. Gene Y1 is regulated by Gene Z1 in a concentration-dependent manner. Gene A2 is activated by Gene B2 during the early stages of development. Gene C2 represses Gene D2 after cell differentiation."
    
    text5 = "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. IRX contributes to activating ventricular genes and supressing atrial genes. IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1. In atrial cells derived by human induced embryonic stem cells, COUP-TFII, a transcription factor encoded by the NR2F2 gene, is robustly upregulated in response to RA during directed atrial differentiation. In mice cardiac cells, COUP-TFII represses IRX4 gene expression in CMs via direct binding to COUP-TFII response elements at the IRX4 genomic loci [39]. In mice cardiac cells, COUP-TFII represses MYL2 gene expression through binding to multiple chromatin sites. In mice cardiac cells, COUP-TFII represses HEY2 gene expression in CMs via direct binding to COUP-TFII response elements at the HEY2 genomic loci. In mice cardiac cells, COUP-TFII binds to genomic loci of MYL7 and expression is lost in COUP-TFII knockout cells. In mice cells, ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. In mice cells, expression of HEY2 is increased by NOTCH signalling."

    text = text5
    doc = nlp(text)

    genes = extract_genes(text)



    interactions =  to_parser(matcher(doc, genes), genes)



    print(genes)