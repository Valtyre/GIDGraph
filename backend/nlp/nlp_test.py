from natural_language_processor import nlp_runner


def NLP_tester():

    # Georgious 
    text_1 = "GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout. IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling."
    expected_1 = "GATA46 activates HEY2. GATA46 activates HAND2. HAND2 activates IRX4. IRX4 activates MYL2. IRX4 activates HAND2. NR2F2 inhibits IRX4. NR2F2 inhibits MYL2. NR2F2 inhibits HEY2. NR2F2 activates MYL7. HEY2 inhibits MYL7. NOTCH activates HEY2."

    # Molecular mechanisms of heart field specific cardiomyocyte differentiation- a computational modeling approach
    text_2 = "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. IRX contributes to activating ventricular genes and supressing atrial genes. IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1. In atrial cells derived by human induced embryonic stem cells, COUP-TFII, a transcription factor encoded by the NR2F2 gene, is robustly upregulated in response to RA during directed atrial differentiation. In mice cardiac cells, COUP-TFII represses IRX4 gene expression in CMs via direct binding to COUP-TFII response elements at the IRX4 genomic loci. In mice cardiac cells, COUP-TFII represses MYL2 gene expression through binding to multiple chromatin sites. In mice cardiac cells, COUP-TFII represses HEY2 gene expression in CMs via direct binding to COUP-TFII response elements at the HEY2 genomic loci. In mice cardiac cells, COUP-TFII binds to genomic loci of MYL7 and expression is lost in COUP-TFII knockout cells. In mice cells, ectopic MYL7 (and other atrial genes') expression is observed in HEY2 knockout ventricles. In mice cells, expression of HEY2 is increased by NOTCH signalling."
    expected_2 = "GATA6 activates HAND2. GATA4 activates HAND2. GATA activates HEY2. HAND2 activates IRX4. IRX4 activates HAND1. IRX4 activates HAND2.  IRX4 activates HAND1. RA activates COUP-TFII. COUP-TFII inhibits IRX4. COUP-TFII inhibits MYL2. COUP-TFII inhibits HEY2. COUP-TFII activates MYL7. HEY2 inhibits MYL7. NOTCH activates HEY2."

    # Single-cell and coupled GRN models of cell patterning in the Arabidopsis thaliana root stem cell niche
    text_3 = "ChIP-QRTPCR experiments show that SHR directly binds in vivo to the regulatory sequences of SCR and positively regulates its transcription. In the scr mutant background, promoter activity of SCR is absent in the QC and CEI. A ChIP-PCR assay confirmed that SCR directly binds to its own promoter and directs its own expression. SCR mRNA expression as probed with a reporter lines is lost in the QC and CEI cells in jkd mutants from the early heart stage onward. The double mutant jkd mgp rescues the expression of SCR in the QC and CEI, which is lost in the jkd single mutant. The expression of MGP is severely reduced in the shr background. Experimental data using various approaches have suggested that MGP is a direct target of SHR. This result was later confirmed by ChIP-PCR. SCR directly binds to the MGP promoter, and MGP expression is reduced in the scr mutant background. The post-embryonic expression of JKD is reduced in shr mutant roots. The post-embryonic expression of JKD is reduced in scr mutant roots. WOX5 is not expressed in scr mutants. WOX5 expression is reduced in shr mutants. WOX5 expression is rarely detected in mp or bdl mutants. PLT1 mRNA region of expression is reduced in multiple mutants of PIN genes, and it is overexpressed under ectopic auxin addition. PLT1 &2 mRNAs are absent in the majority of mp embryos and even more so in mp nph4 double mutant embryos. Overexpression of Aux/IAA genes represses the expression of DR5 both in the presence and absence of auxin. Domains III & IV of Aux/IAA genes interact with domains III & IV of ARF stabilizing the dimerization that represses ARF transcriptional activity. Auxin application destabilizes Aux/IAA proteins. Aux/IAA proteins are targets of ubiquitin-mediated auxin-dependent degradation. Wild type root treated with CLE40p show a reduction of WOX5 expression, whereas in cle40 loss of function plants WOX5 is overexpressed."
    expected_3 = "SHR activates SCR. SCR activates SCR. JKD activates SCR. MGP inhibits SCR. SHR activates MGP. SCR activates MGP. SHR activates JKD. SCR activates JKD. SCR activates WOX5. SHR activates WOX5. ARF (MP) activates WOX5. ARF activates PLT. Aux/IAA inhibits ARF. Auxin inhibits Aux/IAA. CLE40 inhibits WOX5"

    # Hierarchical Differentiation of Myeloid Progenitors Is Encoded in the Transcription Factor Network
    text_4 = "As described above, GATA-2 is an early hematopoietic transcription factor that directs differentiation into the MegE lineage by activating GATA-1. GATA-1 and FOG-1 in turn synergize to downregulate the activatory function of GATA-2 on its own promoter, pushing the differentiation process towards maturated blood cells. As both factors are required to exhibit this repressory mechanism, we implemented their influence towards GATA-2 with a Boolean AND gate. GATA-2 is expressed in immature hematopoietic progenitor cells and activates GATA-1 to drive differentiation towards the MegE lineage. GATA-1, in turn, activates its own expression by direct interaction of a GATA-1 homodimer protein complex with the GATA-1 proximal promoter. Starck et al. found that the GATA-1 downstream factor Fli-1 enhances the stimulatory activity of GATA-1 on GATA-1-responsive promoters. We assume this to have a positive effect on the autoregulation of GATA-1, making Fli-1 an indirect GATA-1 transcriptional activator. Finally, PU.1 and GATA-1 mutually inhibit each other's promoter activity in both mice and human cells."
    expected_4 = "GATA-2 activates GATA-1. GATA-1 inhibits GATA-2. FOG-1 inhibits GATA-2. GATA-2 activates GATA-2. GATA-1 activates GATA-1. Fli-1 activates GATA-1. PU-1 inhibits GATA-1. GATA-1 inhibits PU-1."

    text_5 = "The transcription factor FOG-1 acts as a cofactor of GATA-1 and is necessary for megakaryocytic and erythroid differentiation. Iwasaki et al. demonstrated that GATA-1 upregulates FOG-1 expression in lymphoid or granulocyte/megakaryocyte progenitor cells. GATA-1 has been shown to be crucial for the expression of the erythrocyte lineage factor EKLF. Moreover, there is evidence for the regulation of the megakaryocyte transcription factor Fli-1 by GATA-1. Studies of the dependence of GATA-1 on its cofactor showed that FOG-1 is dispensable for the induction of EKLF by GATA-1. In addition, EKLF and Fli-1 repress each other's transcriptional activity on erythrocyte- and megakaryocyte-specific promoters, respectively. This mutual inhibitory circuit creates the decision switch in the MegE lineage."
    expected_5 = "GATA-1 activates FOG-1. GATA-1 activates EKLF. GATA-1 activates Fli-1. EKLF inhibits Fli-1. Fli-1 inhibits EKLF."

    text_6 = "SCL is a central hematopoietic player required for both primitive and definitive hematopoiesis. However, sustaining the expression of SCL requires different activators during the differentiation process. GATA-1 has been shown to specifically target the SCL promoter during erythroid differentiation. PU.1 inhibits the expression of SCL in the same context. Thus, the SCL player in our model solely represents the SCL protein, which is active in the MegE lineage."
    expected_6 = "GATA-1 activates SCL. PU-1 inhibits SCL."

    text_7 = "The major granulocyte/monocyte transcription factor C/EBP has been shown to be a strong promoter of its own gene. However, to the best of our knowledge, there is no experimental evidence for upstream regulatory factors of C/EBP (literature research and personal communication). However, the factor is strongly downregulated during megakaryocyte/erythrocyte development and thus requires one of the factors from the opposing lineage to be a direct or indirect inhibitor of C/EBP. In our model, the inhibition could be exhibited by, for instance, GATA-1, SCL, or FOG-1. For the model derivation process, we require all three of these MegE factors to be active to constitute C/EBP inhibition."
    expected_7 = "C/EBP activtes C/EBP. GATA1 inhibits C/EBP. SCL inhibits C/EBP. FOG-1 inhibits C/EBP."

    text_8 = "C/EBP is known to be a major inducer of PU.1 during GM development and drives the CMP to GMP transition. It directly binds to a distal cis-regulatory element upstream of the PU.1 promoter to stimulate PU.1 mRNA transcription. PU.1 has been shown to autoregulate its expression in murine and human myeloid cells. An autoregulatory loop mediated by an upstream regulatory element of the PU.1 promoter has been postulated by Okuno et al. In addition, as described above, PU.1 and the GATA factors mutually antagonize each other's promoter activity. The binding of GATA-1 and GATA-2 proteins to the PU.1 promoter and subsequent repression have been shown by Chou et al."
    expected_8 = "C/EBP activates PU-1. PU-1 activates PU-1. GATA-1 inhibits PU-1. GATA-2 inhibits PU-1."

    test_list = [
        # (text_1, expected_1),
        # (text_2, expected_2),
        (text_3, expected_3),
        # (text_4, expected_4),
        # (text_5, expected_5),
        # (text_6, expected_6),
        # (text_7, expected_7),
        # (text_8, expected_8),
    ]

    for t in test_list:
        test, expected = t
        result = nlp_runner(test)

        expected_set = set([e.lstrip().upper() for e in expected.split(". ")])
        result_set = set([e.lstrip().upper() for e in result.split(". ")])

        matching_pairs = expected_set & result_set
        unmatched_expected = expected_set - result_set
        unmatched_result = result_set - expected_set

        print(f"\nMatching Pairs: {matching_pairs}")
        print(f"Unmatched Expected: {unmatched_expected}")
        print(f"Unmatched Result: {unmatched_result}\n")


if __name__ == '__main__':
    NLP_tester()