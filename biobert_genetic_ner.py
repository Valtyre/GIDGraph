import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# Load model and tokenizer
model_name = "alvaroalon2/biobert_genetic_ner"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Create NER pipeline
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

def extract_genes(text):
    """Extract gene mentions from text using BioBERT, properly handling hyphens and numbers."""
    ner_results = ner_pipeline(text)
    
    merged_genes = []
    current_gene = ""
    current_start = None
    current_end = None
    confidence_scores = []

    for entity in ner_results:
        word = entity["word"]
        start, end = entity["start"], entity["end"]
        score = entity["score"]

        # Check if token is a subword or part of a gene name
        if word.startswith("##"):
            current_gene += word[2:]  # Remove '##' and append
            current_end = end
            confidence_scores.append(score)
        elif word in ["-", "/", "."] or word.isdigit():
            # Merge standalone hyphens, slashes, dots, and numbers into the current gene
            current_gene += word
            current_end = end
            confidence_scores.append(score)
        else:
            # Store previous gene
            if current_gene:
                merged_genes.append(current_gene)
                # merged_genes.append((current_gene, current_start, current_end, sum(confidence_scores) / len(confidence_scores)))

            # Start a new gene entity
            current_gene = word
            current_start = start
            current_end = end
            confidence_scores = [score]

    # Add the last gene entity
    if current_gene:
        merged_genes.append(current_gene)
        # merged_genes.append((current_gene, current_start, current_end, sum(confidence_scores) / len(confidence_scores)))

    return list(set(merged_genes))



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
            Expression of HEY2 is increased by NOTCH signalling."""

    # Extract genes
    genes = extract_genes(text)






