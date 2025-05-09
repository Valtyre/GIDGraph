from natural_language_processor import nlp_runner


def NLP_tester():

    # Georgious 
    text_41 = "GATA46 enhances HEY2 expression. GATA46 directly activates HAND2 expression. IRX4 expression is lost by HAND2 knockout. IRX4 contributes to activating MYL2. IRX4 activates HAND2. NR2F2 represses IRX4 gene expression. NR2F2 represses MYL2. NR2F2 represses HEY2 gene. NR2F2 binds to genomic loci of MYL7 and expression is lost in NR2F2 knockout cells. Ectopic MYL7 (and other atrial genes) expression is observed in HEY2 knockout ventricles. Expression of HEY2 is increased by NOTCH signalling."
    expected_41 = "GATA46 activates HEY2. GATA46 activates HAND2. HAND2 activates IRX4. IRX4 activates MYL2. IRX4 activates HAND2. NR2F2 inhibits IRX4. NR2F2 inhibits MYL2. NR2F2 inhibits HEY2. NR2F2 activates MYL7. HEY2 inhibits MYL7. NOTCH activates HEY2."

    # Molecular mechanisms of heart field specific cardiomyocyte differentiation- a computational modeling approach
    text_50 = "In CMs derived by human induced pluripotent stem cells, GATA6 and GATA4 directly activate HAND2 expression. In mice cells, GATA proteins (together with TBX20 ) enhance HEY2 expression in ventricular CMs. In mice cells, IRX4 expression is lost by HAND2 (with/or NKX2.5 ) knockout ventricular CMs. IRX contributes to activating ventricular genes and supressing atrial genes. IRX4 activates both HAND1 and HAND2. IRX4 activates also HAND1. In atrial cells derived by human induced embryonic stem cells, COUP-TFII, a transcription factor encoded by the NR2F2 gene, is robustly upregulated in response to RA during directed atrial differentiation. In mice cardiac cells, COUP-TFII represses IRX4 gene expression in CMs via direct binding to COUP-TFII response elements at the IRX4 genomic loci. In mice cardiac cells, COUP-TFII represses MYL2 gene expression through binding to multiple chromatin sites. In mice cardiac cells, COUP-TFII represses HEY2 gene expression in CMs via direct binding to COUP-TFII response elements at the HEY2 genomic loci. In mice cardiac cells, COUP-TFII binds to genomic loci of MYL7 and expression is lost in COUP-TFII knockout cells. In mice cells, ectopic MYL7 (and other atrial genes') expression is observed in HEY2 knockout ventricles. In mice cells, expression of HEY2 is increased by NOTCH signalling."
    expected_50 = "GATA6 activates HAND2. GATA4 activates HAND2. GATA activates HEY2. HAND2 activates IRX4. IRX4 activates HAND1. IRX4 activates HAND2.  IRX4 activates HAND1. RA activates COUP-TFII. COUP-TFII inhibits IRX4. COUP-TFII inhibits MYL2. COUP-TFII inhibits HEY2. COUP-TFII activates MYL7. HEY2 inhibits MYL7. NOTCH activates HEY2."

    # Single-cell and coupled GRN models of cell patterning in the Arabidopsis thaliana root stem cell niche
    text_44 = "ChIP-QRTPCR experiments show that SHR directly binds in vivo to the regulatory sequences of SCR and positively regulates its transcription. In the scr mutant background, promoter activity of SCR is absent in the QC and CEI. A ChIP-PCR assay confirmed that SCR directly binds to its own promoter and directs its own expression. SCR mRNA expression as probed with a reporter lines is lost in the QC and CEI cells in jkd mutants from the early heart stage onward. The double mutant jkd mgp rescues the expression of SCR in the QC and CEI, which is lost in the jkd single mutant. The expression of MGP is severely reduced in the shr background. Experimental data using various approaches have suggested that MGP is a direct target of SHR. This result was later confirmed by ChIP-PCR. SCR directly binds to the MGP promoter, and MGP expression is reduced in the scr mutant background. The post-embryonic expression of JKD is reduced in shr mutant roots. The post-embryonic expression of JKD is reduced in scr mutant roots. WOX5 is not expressed in scr mutants. WOX5 expression is reduced in shr mutants. WOX5 expression is rarely detected in mp or bdl mutants. PLT1 mRNA region of expression is reduced in multiple mutants of PIN genes, and it is overexpressed under ectopic auxin addition. PLT1 &2 mRNAs are absent in the majority of mp embryos and even more so in mp nph4 double mutant embryos. Overexpression of Aux/IAA genes represses the expression of DR5 both in the presence and absence of auxin. Domains III & IV of Aux/IAA genes interact with domains III & IV of ARF stabilizing the dimerization that represses ARF transcriptional activity. Auxin application destabilizes Aux/IAA proteins. Aux/IAA proteins are targets of ubiquitin-mediated auxin-dependent degradation. Wild type root treated with CLE40p show a reduction of WOX5 expression, whereas in cle40 loss of function plants WOX5 is overexpressed."
    expected_44 = "SHR activates SCR. SCR activates SCR. JKD activates SCR. MGP inhibits SCR. SHR activates MGP. SCR activates MGP. SHR activates JKD. SCR activates JKD. SCR activates WOX5. SHR activates WOX5. ARF (MP) activates WOX5. ARF activates PLT. Aux/IAA inhibits ARF. Auxin inhibits Aux/IAA. CLE40 inhibits WOX5"

    # Hierarchical Differentiation of Myeloid Progenitors Is Encoded in the Transcription Factor Network
    text_61 = "As described above, GATA-2 is an early hematopoietic transcription factor that directs differentiation into the MegE lineage by activating GATA-1. GATA-1 and FOG-1 in turn synergize to downregulate the activatory function of GATA-2 on its own promoter, pushing the differentiation process towards maturated blood cells. As both factors are required to exhibit this repressory mechanism, we implemented their influence towards GATA-2 with a Boolean AND gate."
    expected_61 = "GATA-2 inhibits GATA-1. GATA-1 inhibits GATA-2. FOG-1 inhibits GATA-2."

    text_47 = "GATA-2 is expressed in immature hematopoietic progenitor cells and activates GATA-1 to drive differentiation towards the MegE lineage. GATA-1, in turn, activates its own expression by direct interaction of a GATA-1 homodimer protein complex with the GATA-1 proximal promoter. Starck et al. found that the GATA-1 downstream factor Fli-1 enhances the stimulatory activity of GATA-1 on GATA-1-responsive promoters. We assume this to have a positive effect on the autoregulation of GATA-1, making Fli-1 an indirect GATA-1 transcriptional activator. Finally, PU.1 and GATA-1 mutually inhibit each other's promoter activity in both mice and human cells."
    expected_47 = "GATA-2 activates GATA-1. GATA-1 activates GATA-1. Fli-1 activates GATA-1. PU.1 inhibits GATA-1. PU.1 inhibits GATA-2."


    test_list = [
        # (text_41, expected_41),
        # (text_50, expected_50),
        # (text_44, expected_44),
        # (text_61, expected_61),
        (text_47, expected_47),
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