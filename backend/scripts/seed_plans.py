from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.plan import Plan

PLANS = [
    {
        'code': 'starter',
        'name': 'Starter',
        'monthly_request_limit': 200,
        'monthly_input_token_limit': 2_000_000,
        'monthly_output_token_limit': 500_000,
        'monthly_cost_limit_usd': Decimal('5.00'),
        'allowed_models': ['openai/gpt-4.1-mini', 'openai/gpt-5.4-mini'],
        'max_upload_mb': 20,
    },
    {
        'code': 'pro',
        'name': 'Pro',
        'monthly_request_limit': 1000,
        'monthly_input_token_limit': 10_000_000,
        'monthly_output_token_limit': 2_000_000,
        'monthly_cost_limit_usd': Decimal('30.00'),
        'allowed_models': ['openai/gpt-4.1-mini', 'openai/gpt-5.4-mini', 'anthropic/claude-sonnet-4.5'],
        'max_upload_mb': 100,
    },
    {
        'code': 'premium',
        'name': 'Premium',
        'monthly_request_limit': 5000,
        'monthly_input_token_limit': 50_000_000,
        'monthly_output_token_limit': 10_000_000,
        'monthly_cost_limit_usd': Decimal('150.00'),
        'allowed_models': [
            'openai/gpt-4.1-mini',
            'openai/gpt-5.4-mini',
            'anthropic/claude-sonnet-4.5',
            'openai/gpt-5.4',
        ],
        'max_upload_mb': 250,
    },
]


def main() -> None:
    with SessionLocal() as db:
        for plan_data in PLANS:
            existing = db.scalar(select(Plan).where(Plan.code == plan_data['code']))
            if existing:
                for key, value in plan_data.items():
                    setattr(existing, key, value)
                db.add(existing)
            else:
                db.add(Plan(**plan_data))
        db.commit()


if __name__ == '__main__':
    main()
    print('Plans seeded successfully.')
