import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# Load model and tokenizer
model_name = "alvaroalon2/biobert_genetic_ner"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Create NER pipeline
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

def extract_genes(text):
    ner_results = ner_pipeline(text)

    # Words to exclude (lowercased)
    excluded_words = {"genes", "gene", "protein", "proteins", "loci", "genomic"}

    merged_genes = []
    current_gene = ""
    last_end = -1  # Track last token position to detect spacing

    for entity in ner_results:
        word = entity["word"]
        start = entity["start"]

        # Normalize subword (BioBERT uses ##)
        clean_word = word.replace("##", "")
        
        # If there is a space between previous and current word, finalize the previous gene
        if current_gene and start > last_end + 1:
            gene_cleaned = current_gene.replace(" ", "").replace(".", "-")
            if gene_cleaned.lower() not in excluded_words:
                merged_genes.append(gene_cleaned)
            current_gene = ""

        # Add current word to gene
        current_gene += clean_word
        last_end = entity["end"]

    # Final gene after loop
    if current_gene:
        gene_cleaned = current_gene.replace(" ", "").replace(".", "-")
        if gene_cleaned.lower() not in excluded_words:
            merged_genes.append(gene_cleaned)

    # Remove any that exactly match excluded words
    final_genes = {
        gene for gene in merged_genes if gene.lower() not in excluded_words
    }

    return list(final_genes)

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

    genes = extract_genes(text)
    print(genes)
