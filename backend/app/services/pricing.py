from decimal import Decimal

MODEL_PRICING_PER_MILLION: dict[str, dict[str, Decimal]] = {
    'openai/gpt-4.1-mini': {'input': Decimal('0.40'), 'output': Decimal('1.60')},
    'openai/gpt-5.4-mini': {'input': Decimal('0.60'), 'output': Decimal('2.40')},
    'anthropic/claude-sonnet-4.5': {'input': Decimal('3.00'), 'output': Decimal('15.00')},
    'openai/gpt-5.4': {'input': Decimal('2.50'), 'output': Decimal('10.00')},
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> Decimal:
    pricing = MODEL_PRICING_PER_MILLION.get(model)
    if not pricing:
        return Decimal('0')
    input_cost = (Decimal(input_tokens) / Decimal(1_000_000)) * pricing['input']
    output_cost = (Decimal(output_tokens) / Decimal(1_000_000)) * pricing['output']
    return (input_cost + output_cost).quantize(Decimal('0.000001'))
