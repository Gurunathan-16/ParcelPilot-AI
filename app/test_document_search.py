from app.tools.document_search import search_documents


results = search_documents(
    query="What are the cancellation rules and cancellation fees?",
    customer_name="Northstar Logistics"
)

print("\n🔍 SEARCH RESULTS")
print("=" * 70)

if not results:
    print("No results found.")

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}")
    print(f"Source: {result['source']}")
    print(f"Page: {result['page']}")
    print(f"Authority: {result['authority']}")
    print(f"Distance: {result['distance']}")
    print(f"Content: {result['content'][:500]}...")