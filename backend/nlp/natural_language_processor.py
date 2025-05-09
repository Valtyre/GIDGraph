import spacy
from spacy.tokenizer import Tokenizer
import scispacy
import numpy as np
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token
from .biobert_genetic_ner import extract_genes
import re

printer = True

def geneTokenizer(nlp):
    infix_re = re.compile(r'''[.\,\?\!\:\;\…]''')  # Keep default infix rules but remove hyphens splitting
    prefix_re = re.compile(r'''^[\(\[\{\<\']''')  # Keep default prefix rules
    suffix_re = re.compile(r'''[\)\]\}\>\'"]$''')  # Keep default suffix rules

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                     suffix_search=suffix_re.search,
                     infix_finditer=infix_re.finditer,
                     token_match=None)

def get_compound_phrase(head_token: Token):
    # Collect tokens that form the compound: left children with dep "compound" or "amod"
    modifiers = [child for child in head_token.lefts if child.dep_ in ["compound", "amod"]]
    # Sort by their position in the sentence to maintain correct word order
    modifiers = sorted(modifiers, key=lambda t: t.i)

    # Return the full phrase including the head token
    return " ".join([t.text for t in modifiers] + [head_token.text])


def matcher(doc: Doc, gene_list: list) -> list[tuple[str, str, str, Span]]:

    for e in doc.ents:
        if e.label_ == "GENE_OR_GENE_PRODUCT": 
            gene_list.append(e.text.upper())
    gene_list = list(set(gene_list))
        
    relationships: list[tuple[str, str, str, str, list[float], list[float]]] = []

    for i, sent in enumerate(doc.sents): 

        if i == 0:
            activate = sent[1]
            continue
        elif i == 1:
            inhibit = sent[1]
            continue


        if (printer): print("\nSentence:" , sent, "\n")

        root = [sent.root]
        actor = None 
        target = None

        for token in sent:


            if (printer): print(token.text, '\033[31m', token.dep_, '\033[32m', token.head, '\033[93m', token.pos_, '\033[95m', token.lemma_, "CHILDREN:", [child.text for child in token.children],'\033[0m' )

            # Gene list 
            if token.text.upper() in gene_list: 
                # Compound 
                if token.dep_ == "compound" or token.dep_ == "amod":
                    phrase = get_compound_phrase(token.head)
                    if (printer): print("Compound phrase:", '\033[36m', phrase, '\033[0m')
                    if (actor == None or token.text == actor) and (token.head.dep_ in ["nsubj", "nmod"]):
                        actor = phrase
                    elif (target == None or token.text == target) and (token.head.dep_ in ["dobj", "nsubjpass", "nmod"]):
                        target = phrase

                # ACTOR 
                elif actor == None and (token.dep_ in ["nsubj", "nmod"]) and (token.dep_ not in ["nmod"] and token.head.dep_ != "nsubjpass"):
                    actor = token.text

                # TARGET 
                elif target == None and (token.dep_ in ["dobj", "nsubjpass", "nmod"]):
                    target = token.text

            # Extra cases
            if token.dep_ == "conj":
                if actor != None and token.head.text in actor:
                    actor += " and " + token.text
                elif target != None and token.head.text in target:
                    target += " and " + token.text         
                elif token.pos_ == "VERB" and all(token.text not in r.text for r in root): 
                    root.append(token)
            
            elif (token.dep_ == "neg" and token.head in [sent.root]):
                temp = []
                d = token.doc
                start = min(token.i, token.head.i)
                end = max(token.i, token.head.i) + 1 

                phrase = d[start:end]
                root.remove(token.head)
                root.append(phrase)

            elif token.dep_ == "advcl" and token.head.dep_ == "ROOT":
                root.append(token)

            elif token.dep_ == "xcomp" and token.head.dep_ == "ROOT":
                root.append(token)
            
            elif token.dep_ == "amod" and token.head.lemma_ == "expression":
                if token.head.head.dep_ == "ROOT":
                    root.append(token)
                elif token.text == "own":
                    if actor != None:
                        if target: target += " and " + token.text
                        else: target = actor
                    elif target != None:
                        if actor: actor += " and  " + token.text
                        else: actor = target

            elif token.dep_ == "advmod" and token.head.lemma_ in ["regulate", "control"]:
                d = token.doc
                start = min(token.i, token.head.i)
                end = max(token.i, token.head.i) + 1 

                phrase = d[start:end]
                if token.head in root: root.remove(token.head)
                root.append(phrase)


            elif token.dep_ == "appos" and token.head.text in gene_list and token.head.text not in actor:
                    actor = token.head.text

            elif token.dep_ == "ccomp" and token.head.dep_ == "ROOT":
                root.append(token)
            

        # Shortest path

        # if None in [actor, root, target]:
        #     if actor == None and target == None:
        #         continue
        #     if actor == None:
        #         for token in sent:
        #             if token.text in gene_list:
        #                 actor = token.text
        #                 continue
        #     if target == None: 
        #         for token in sent:
        #             if token.text in gene_list:
        #                 target = token.text
        #                 continue
        
        if (printer): print("\nACTOR: ", actor, "ROOT: ", root, "TARGET: ", target, [r.similarity(activate) for r in root],[r.similarity(inhibit) for r in root])


        if None in [actor, root, target]: continue
                
        relationships.append([actor, root, target, sent, [r.similarity(activate) for r in root],[r.similarity(inhibit) for r in root]])

    return relationships
          


def entities(doc: Doc):

    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))

    return entities



def interaction_evaluator(interactions: list[tuple[str, list[Token], str, str, list[float], list[float]]], gene_list: list[str]) -> str:
    
    """Processes interactions by ensuring multiple genes are handled correctly and normalizing verbs."""
    
    activation_verbs = { "activate", "activation", "trigger", "enhance", "boost", "raise", "amplify", "upregulation", "improve", "induce", "stimulate", "upregulate", "increase", "promote", "auto-activating", "direct"}
    repression_verbs = { "repress", "inhibit", 'hinder', "impede", "inhibition", "downregulate", "downregulation", "suppress", "loose", "inactive", "diminish", "lost", "lose", "decrease", "reduce"}
    
    parsed_interactions = []  # Store cleaned interactions
    seen_interactions = set()  # Track unique interactions
    

    for i in range(len(interactions)):
        
        knockout = False

        a, r, t, sent, a_sim, i_sim = interactions[i]  # Unpack tuple
        
        if any(l in a + t for l in ["knockout", "mutant"]):
            knockout = True

        # Handle multiple genes in subject (a) or target (t)
        a_genes = list(set([gene for gene in gene_list if any([gene == act.upper() for act in a.split()])]))
        t_genes = list(set([gene for gene in gene_list if any([gene == tar.upper() for tar in t.split()])]))

        # Standardize the relation type (r)
        for i, verb in enumerate(r):
            if "not" in verb.text.split() : # not case
                if verb.text.split()[1] in activation_verbs: 
                    r = "inhibits"
                    break
                elif verb.text.split()[1] in repression_verbs:
                    r = "activates"
                    break
            if verb.lemma_ in activation_verbs:
                r = "activates"
                break
            elif verb.lemma_ in repression_verbs: 
                r = "inhibits"
                break

        if r not in ["activates","inhibits"]:
            for token in sent:
                if token in activation_verbs:
                    r = "activates"
                elif token in repression_verbs:
                    r = "inhibits"
            if max(a_sim) >  max(i_sim): 
                    r = "activates"
            elif max(a_sim) <  max(i_sim):
                    r = "inhibits"

        if knockout and r == "activates": 
            r = "inhibits"
        elif knockout and r == "inhibits":
            r = "activates"


        # Create separate interactions for each subject-target pair
        for a_gene in a_genes:
            for t_gene in t_genes:
                interaction_tuple = (a_gene, r, t_gene)
                if interaction_tuple not in seen_interactions:
                    parsed_interactions.append((a_gene, r, t_gene, sent))
                    seen_interactions.add(interaction_tuple)
        
    inter = ''
    for i, interaction in enumerate(parsed_interactions): 
        if interaction[0] != None and interaction[1] in ["activates", "inhibits"] and interaction[2] != None:
            inter += f" {interaction[0]} {interaction[1]} {interaction[2]}."

    if (printer):
        for i, interaction in enumerate(parsed_interactions): 
            if interaction[0] != None and interaction[1] in ["activates", "inhibits"] and interaction[2] != None:
                print('\033[0m', f"Interaction {i+1}:", interaction[0], interaction[1], interaction[2], "    \tOriginal:", interaction[3])
            elif interaction != None: 
                print('\033[31m', f"Interaction {i+1}:", interaction[3],'\033[36m', interaction[0], interaction[1], interaction[2])


    return inter


def nlp_runner(text: str) -> str:
    text = re.sub(r"\.(?!\s)", "-", text + " ")
    nlp = spacy.load("en_ner_bionlp13cg_md")
    nlp.tokenizer = geneTokenizer(nlp)
    doc = nlp("GENE1 upregulates GENE2. GENE1 represses GENE2. " + text)

    genes = extract_genes(text)
    interactions =  interaction_evaluator(matcher(doc, genes), genes)
    if printer: print(genes)

    return interactions


if __name__ == '__main__':

    nlp = spacy.load("en_ner_bionlp13cg_md")
    # nlp_model_1 = spacy.load("en_core_sci_scibert")

    nlp.tokenizer = geneTokenizer(nlp)

    text_41 = "GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout. IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling."
    text_50 = "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. IRX contributes to activating ventricular genes and supressing atrial genes. IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1. In atrial cells derived by human induced embryonic stem cells, COUP-TFII, a transcription factor encoded by the NR2F2 gene, is robustly upregulated in response to RA during directed atrial differentiation. In mice cardiac cells, COUP-TFII represses IRX4 gene expression in CMs via direct binding to COUP-TFII response elements at the IRX4 genomic loci. In mice cardiac cells, COUP-TFII represses MYL2 gene expression through binding to multiple chromatin sites. In mice cardiac cells, COUP-TFII represses HEY2 gene expression in CMs via direct binding to COUP-TFII response elements at the HEY2 genomic loci. In mice cardiac cells, COUP-TFII binds to genomic loci of MYL7 and expression is lost in COUP-TFII knockout cells. In mice cells, ectopic MYL7 (and other atrial genes') expression is observed in HEY2 knockout ventricles. In mice cells, expression of HEY2 is increased by NOTCH signalling."
    text_44 = "The expression of SCR is reduced in shr mutants. ChIP-QRTPCR experiments show that SHR directly binds in vivo to the regulatory sequences of SCR and positively regulates its transcription. In the scr mutant background promoter activity of SCR is absent in the QC and CEI. A ChIP-PCR assay confirmed that SCR directly binds to its own promoter and directs its own expression. SCR mRNA expression as probed with a reporter lines is lost in the QC and CEI cells in jkd mutants from the early heart stage onward. The double mutant jkd mgp rescues the expression of SCR in the QC and CEI, which is lost in the jkd single mutant. The expression of MGP is severely reduced in the shr background. Experimental data using various approaches have suggested that MGP is a direct target of SHR. This result was later confirmed by ChIP-PCR. SCR directly binds to the MGP promoter, and MGP expression is reduced in the scr mutant background. The post-embryonic expression of JKD is reduced in shr mutant roots. The post-embryonic expression of JKD is reduced in scr mutant roots. WOX5 is not expressed in scr mutants. WOX5 expression is reduced in shr mutants. WOX5 expression is rarely detected in mp or bdl mutants. PLT1 mRNA region of expression is reduced in multiple mutants of PIN genes, and it is overexpressed under ectopic auxin addition. PLT1 &2 mRNAs are absent in the majority of mp embryos and even more so in mp nph4 double mutant embryos. Overexpression of Aux/IAA genes represses the expression of DR5 both in the presence and absence of auxin. Domains III & IV of Aux/IAA genes interact with domains III & IV of ARF stabilizing the dimerization that represses ARF transcriptional activity. Auxin application destabilizes Aux/IAA proteins. Aux/IAA proteins are targets of ubiquitin-mediated auxin-dependent degradation. Wild type root treated with CLE40p show a reduction of WOX5 expression, whereas in cle40 loss of function plants WOX5 is overexpressed."
    text_60 = "In the anterior signaling center, Fgf8 establishes the low anterior-graded expression of the TFs Emx2 and COUP-TFI by repression, and promotes the high anterior gradient of Sp8 expression.Fgf8 expression is also regulated positively by direct transcriptional activation by Sp8 through its binding to Fgf8 regulatory elements, and indirectly by Emx2, which represses the ability of Sp8 to directly induce Fgf8, as described in Figure 2. The asterisk marking the activation of Fgf8 by Sp8 indicates the only interaction that has been shown to be due to direct binding and transcriptional activation. Putative posterior signaling molecules Bmps and Wnts, expressed in the cortical hem, positively regulate the high caudal gradient of Emx2 expression. Genetic interactions between TFs also participate in the establishment of their graded expression. For example, Emx2 and Pax6 mutually suppress each other’s expression, Coup-TFI suppresses Pax6 expression and enhances Emx2 expression, and Sp8 suppresses Emx2 expression. Those changes to the expression patterns were identified in the knockout mice; thus, these interactions do not necessarily imply direct control of one TF on another. For instance, Emx2 suppression by Sp8 might be due to an enhancement of Fgf8 expression, which in turn acts negatively on Emx2 expression."

    addon = "GENE1 upregulates GENE2. GENE1 represses GENE2. "

    text = addon + text_41
    text = re.sub(r"\.(?!\s)", "-", text + " ")
    doc = nlp(text)

    genes = extract_genes(text)



    interactions =  interaction_evaluator(matcher(doc, genes), genes)
    # print(interactions)



    # print(genes)