from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

MODEL_NAME = "alvaroalon2/biobert_genetic_ner"
_ner_pipeline = None


def get_ner_pipeline():
    global _ner_pipeline

    if _ner_pipeline is None:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
        _ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

    return _ner_pipeline

def extract_genes(text):
    ner_results = get_ner_pipeline()(text)

    excluded_words = {"genes", "gene", "protein", "proteins", "loci", "genomic", "response", "elements", "mutant",}
    merged_genes: list[str] = []
    current_gene = ""
    last_end = -1

    for entity in ner_results:
        word = entity["word"]
        start = entity["start"]
        end = entity["end"]

        clean_word = word.replace("##", "")

        # If there's a space or different span, finish previous gene
        if current_gene and start > last_end + 1:
            cleaned = current_gene.strip().replace(" ", "").replace(".", "-")
            # Strip excluded suffixes
            for suffix in excluded_words:
                if cleaned.lower().endswith(suffix):
                    cleaned = cleaned[: -len(suffix)]
            cleaned = cleaned.strip("-")
            if cleaned and cleaned.lower() not in excluded_words:
                merged_genes.append(cleaned)
            current_gene = ""

        if clean_word.lower() not in excluded_words:
            current_gene += clean_word
        last_end = end

    # Final gene
    if current_gene:
        cleaned = current_gene.strip().replace(" ", "").replace(".", "-")
        for suffix in excluded_words:
            if cleaned.lower().endswith(suffix):
                cleaned = cleaned[: -len(suffix)]
        cleaned = cleaned.strip("-")
        if cleaned and cleaned.lower() not in excluded_words:
            merged_genes.append(cleaned)

    genes = []
    for g in merged_genes: 
        genes.append(g.upper())
    # Remove duplicates
    return list(set(genes))


if __name__ == '__main__':
    text = """GATA4 enhances HEY2 expression. 
            GATA4 directly activates HAND2 expression. 
            IRX4 expression is lost by HAND2 knockout. 
            IRX4 contributes to activating MYL2. 
            IRX4 activates HAND2. 
            NR2F2 represses IRX4 gene expression. 
            NR2F2 represses MYL2. 
            NR2F2 represses HEY2 gene. 
            Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. 
            Expression of HEY2 is increased by NOTCH signalling.
            GATA proteins regulate development.
            These loci are important in evolution."""
    
    test1 = "The expression of SCR is reduced in shr mutants. ChIP-QRTPCR experiments show that SHR directly binds in vivo to the regulatory sequences of SCR and positively regulates its transcription.  In the scr mutant background promoter activity of SCR is absent in the QC and CEI. A ChIP-PCR assay confirmed that SCR directly binds to its own promoter and directs its own expression.  SCR mRNA expression as probed with a reporter lines is lost in the QC and CEI cells in jkd mutants from the early heart stage onward.  The double mutant jkd mgp rescues the expression of SCR in the QC and CEI, which is lost in the jkd single mutant.  The expression of MGP is severely reduced in the shr background. Experimental data using various approaches have suggested that MGP is a direct target of SHR. This result was later confirmed by ChIP-PCR.  SCR directly binds to the MGP promoter, and MGP expression is reduced in the scr mutant background.  The post-embryonic expression of JKD is reduced in shr mutant roots.  The post-embryonic expression of JKD is reduced in scr mutant roots.  WOX5 is not expressed in scr mutants.  WOX5 expression is reduced in shr mutants.  WOX5 expression is rarely detected in mp or bdl mutants.  PLT1 mRNA region of expression is reduced in multiple mutants of PIN genes, and it is overexpressed under ectopic auxin addition. PLT1 & 2 mRNAs are absent in the majority of mp embryos and even more so in mp nph4 double mutant embryos.  Overexpression of Aux/IAA genes represses the expression of DR5 both in the presence and absence of auxin. Domains III & IV of Aux/IAA genes interact with domains III & IV of ARF stabilizing the dimerization that represses ARF transcriptional activity.  Auxin application destabilizes Aux/IAA proteins. Aux/IAA proteins are targets of ubiquitin-mediated auxin-dependent degradation.  Wild type root treated with CLE40p show a reduction of WOX5 expression, whereas in cle40 loss of function plants WOX5 is overexpressed."


    genes = extract_genes(test1)
    print(genes)
