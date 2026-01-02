# Example Conversations

## Sales
User: I'm looking for a standing desk with a bamboo top.
Assistant: Let me check options.
Tool call: search_products(keywords="bamboo", category="standing-desk")
Assistant: I found DriftDesk Pro (DSK-100), an electric standing desk with a bamboo top and memory presets. Want pricing or a comparison?

## Pricing
User: What's the price on DSK-100 for two units with BUNDLE10?
Assistant: I'll calculate pricing.
Tool call: get_pricing(sku="DSK-100", quantity=2, promo_code="BUNDLE10")
Assistant: Each is $699. Subtotal is $1,398. BUNDLE10 applies 10% off, so total is $1,258.20.

## Support
User: Order ORD-1002 says it's late.
Assistant: I'll check the latest status.
Tool call: check_order_status(order_id="ORD-1002")
Assistant: ORD-1002 is processing with ETA 2025-01-10. If you'd like, I can open a ticket to follow up with shipping.
