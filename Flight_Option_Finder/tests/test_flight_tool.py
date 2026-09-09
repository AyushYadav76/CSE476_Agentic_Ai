from app.tools import search_flights, compare_price

search = search_flights(
    from_city="Delhi",
    to_city="Mumbai",
    departure_date="2026-09-15",
    passengers=1,
    cabin_class="economy",
)

print(search)

print("\n" + "=" * 70)
print("PRICE COMPARISON")
print("=" * 70)

ranked = compare_price(search)
print(ranked)