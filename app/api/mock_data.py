"""
Fin-Trace: Mock Investigation Data
A real, previously-generated investigation response, used for frontend
development so UI work doesn't burn Groq API tokens or wait on live calls.
"""

MOCK_INVESTIGATION_RESPONSE = {
    "question": "Why did Tesla's net income rise despite falling margins in 2023?",
    "sub_questions": [
        "What was the change in Tesla's total revenue and vehicle delivery volumes in 2023 versus 2022?",
        "How did cost of goods sold, operating expenses, and other recurring costs evolve, and what effect did they have on gross and operating margins?",
        "What one-time or non-recurring items (e.g., tax benefits, share-based compensation adjustments, asset sale gains, restructuring charges) were recorded in 2023 that impacted net income?",
        "How did Tesla's effective tax rate and related tax expense change in 2023, and what contribution did this have to net income?",
        "Were there any accounting policy changes, reclassifications, or adjustments (e.g., depreciation, amortization, inventory write-downs) in 2023 that affected the net income figure?",
    ],
    "findings": [
        {
            "sub_question": "What was the change in Tesla's total revenue and vehicle delivery volumes in 2023 versus 2022?",
            "answer": "Total revenue rose from $81,462 million in 2022 to $96,773 million in 2023, an increase of $15,311 million (~18.8%). Automotive-sales revenue rose about 17% due to an increase of 473,382 combined Model 3 and Model Y cash deliveries from production ramp-up of Model Y globally.",
            "sources": ["tsla-20231231-gen.pdf"],
        },
        {
            "sub_question": "How did cost of goods sold, operating expenses, and other recurring costs evolve, and what effect did they have on gross and operating margins?",
            "answer": "Total-automotive gross margin fell from 28.5% in 2022 to 19.4% in 2023, and combined automotive + services-and-other gross margin dropped from 26.5% to 18.2%. The decline is attributed primarily to lower average selling prices on vehicles, partially offset by lower average cost per unit (lower material costs, better fixed-cost absorption) and IRA manufacturing credits. Operating-expense figures (SG&A, R&D) were not disclosed in the excerpts, limiting a full operating-margin quantification.",
            "sources": ["tsla-20231231-gen.pdf"],
        },
        {
            "sub_question": "What one-time or non-recurring items (e.g., tax benefits, share-based compensation adjustments, asset sale gains, restructuring charges) were recorded in 2023 that impacted net income?",
            "answer": "A $326 million income-tax benefit was recognized from the release of a valuation allowance on U.S. deferred tax assets related to stock-based compensation. Additionally, $199 million of stock-based compensation expense was capitalized to the balance sheet rather than expensed, reducing reported expense. No asset-sale gains or restructuring charges were disclosed in the excerpts.",
            "sources": ["tsla-20231231-gen.pdf"],
        },
        {
            "sub_question": "How did Tesla's effective tax rate and related tax expense change in 2023, and what contribution did this have to net income?",
            "answer": "A deferred income-tax adjustment of -$6.349 billion appeared in the 2023 cash-flow statement, versus -$0.196 billion in 2022, indicating a much larger deferred-tax charge. Net income still rose from $12.587 billion in 2022 to $14.974 billion in 2023. Total tax expense and pre-tax income were not disclosed in the excerpts, so an exact effective tax rate could not be calculated.",
            "sources": ["tsla-20231231-gen.pdf"],
        },
        {
            "sub_question": "Were there any accounting policy changes, reclassifications, or adjustments (e.g., depreciation, amortization, inventory write-downs) in 2023 that affected the net income figure?",
            "answer": "No accounting-policy changes, reclassifications, or special adjustments affecting net income were disclosed. Internal control over financial reporting was reported unchanged for the quarter ended December 31, 2023.",
            "sources": ["tsla-20231231-gen.pdf"],
        },
    ],
    "contradictions": {
        "contradictions_found": False,
        "contradictions": [],
    },
    "report": {
        "conclusion": "Tesla's net income rose in 2023 because strong revenue growth and one-time tax and accounting benefits more than offset the decline in operating margins caused by lower vehicle pricing and higher cost pressures.",
        "confidence": 80,
        "key_factors": [
            {
                "factor": "Revenue growth",
                "explanation": "Total revenue jumped 18.8% to $96.8 bn, driven by a 15.3% increase in automotive sales and higher deliveries of Model 3/Y, providing a larger top-line base.",
                "evidence_source": "tsla-20231231-gen.pdf",
            },
            {
                "factor": "Margin compression",
                "explanation": "Automotive gross margin fell from 28.5% to 19.4% and operating margin dropped from 16.76% to 9.19% as average selling prices fell and cost-of-revenue pressures rose.",
                "evidence_source": "tsla-20231231-gen.pdf",
            },
            {
                "factor": "Tax benefit from stock-based compensation",
                "explanation": "A $326 million reduction in income-tax expense (release of a valuation allowance) directly lifted net income.",
                "evidence_source": "tsla-20231231-gen.pdf",
            },
            {
                "factor": "Capitalization of stock-based compensation",
                "explanation": "Tesla capitalized $199 million of stock-based compensation expense, lowering the expense recognized in the income statement and boosting net income.",
                "evidence_source": "tsla-20231231-gen.pdf",
            },
            {
                "factor": "Deferred tax adjustment (cash-flow effect)",
                "explanation": "A large negative deferred-tax adjustment ($6.349 bn) appears in the cash-flow statement, indicating timing differences that reduced cash taxes paid, supporting higher net income despite higher reported tax expense.",
                "evidence_source": "tsla-20231231-gen.pdf",
            },
        ],
        "contradictions_or_gaps": "Operating-expense figures (SG&A, R&D, depreciation) are missing, preventing a full accounting of the operating-margin decline. Effective tax rate cannot be calculated from the provided data.",
        "reasoning_chain": "Higher vehicle deliveries and strong growth in energy and services revenue lifted total revenue, creating a larger profit base. Although lower average selling prices and higher cost-of-revenue compressed gross and operating margins, Tesla recorded a $326 million tax benefit and capitalized $199 million of stock-based compensation, both of which reduced expenses and directly increased net income. The combined effect of revenue expansion and these one-time items outweighed the margin deterioration, resulting in a rise in net income despite the margin decline.",
    },
    "graph_image_url": "/images/knowledge_graph.png",
    "graph_edges": [
        {"source": "Vehicle Deliveries", "relation": "drove", "target": "Revenue Growth"},
        {"source": "Revenue Growth", "relation": "expanded", "target": "Total Revenue"},
        {"source": "Lower Selling Prices", "relation": "compressed", "target": "Gross Margin"},
        {"source": "Higher Cost Pressures", "relation": "compressed", "target": "Gross Margin"},
        {"source": "Gross Margin", "relation": "reduced", "target": "Operating Margin"},
        {"source": "Tax Valuation Release", "relation": "added to", "target": "Net Income"},
        {"source": "Capitalized Stock Comp", "relation": "added to", "target": "Net Income"},
        {"source": "Total Revenue", "relation": "supported", "target": "Net Income"},
        {"source": "Operating Margin", "relation": "pressured", "target": "Net Income"},
    ],
}