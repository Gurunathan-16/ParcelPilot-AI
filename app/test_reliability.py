from app.agent.reliability import (
    evaluate_evidence,
    detect_conflict
)


sources = [
    {
        "source": "01_Support_Policy_v3_CURRENT.pdf",
        "source_type": "general_policy",
        "status": "current",
        "authority": 80
    },
    {
        "source": "05_Northstar_Logistics_Enterprise_Agreement.pdf",
        "source_type": "customer_agreement",
        "customer": "Northstar Logistics",
        "status": "current",
        "authority": 100
    },
    {
        "source": "02_Support_Policy_v2_DEPRECATED.pdf",
        "source_type": "general_policy",
        "status": "deprecated",
        "authority": 10
    }
]


print("\nEVIDENCE EVALUATION")
print("=" * 60)

result = evaluate_evidence(
    sources,
    customer_name="Northstar Logistics"
)

print(result)


print("\nCONFLICT DETECTION")
print("=" * 60)

conflict = detect_conflict(sources)

print(conflict)