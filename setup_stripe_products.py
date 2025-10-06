#!/usr/bin/env python3
"""
Stripe Product Setup Script for Infinite Carwash Subscription System
This script creates the subscription products and pricing plans in your new Stripe account.
"""

import stripe
import os
from decimal import Decimal

# Set your Stripe secret key from environment variable
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

if not stripe.api_key:
    print("❌ Error: STRIPE_SECRET_KEY environment variable is not set.")
    print("Please set your Stripe secret key as an environment variable:")
    print("export STRIPE_SECRET_KEY='sk_test_...'")
    exit(1)

def create_subscription_products():
    """Create subscription products and pricing plans in Stripe"""
    
    print("🚀 Setting up Stripe subscription products...")
    
    # Vehicle type multipliers for pricing
    vehicle_multipliers = {
        'small_car': 1.0,
        'medium_car': 1.43,  # £50/£35 = 1.43
        'large_car': 1.71,   # £60/£35 = 1.71
        'van': 2.14          # £75/£35 = 2.14
    }
    
    products_created = []
    
    try:
        # 1. Mini Valet Subscription Product
        print("Creating Mini Valet Subscription product...")
        mini_valet_product = stripe.Product.create(
            name="Mini Valet Subscription",
            description="Comprehensive exterior and interior cleaning service subscription",
            metadata={
                'service_type': 'mini_valet',
                'duration': '90 minutes',
                'base_price': '35'
            }
        )
        
        # Create pricing plans for Mini Valet (different frequencies)
        mini_valet_prices = []
        
        # Monthly plan (4 services per month, 15% discount)
        monthly_price = stripe.Price.create(
            product=mini_valet_product.id,
            unit_amount=4760,  # £47.60 (£35 * 4 * 0.85 for 15% discount)
            currency='gbp',
            recurring={'interval': 'month'},
            metadata={
                'frequency': 'monthly',
                'services_per_month': '4',
                'discount': '15',
                'vehicle_type': 'small_car'
            }
        )
        mini_valet_prices.append(monthly_price)
        
        # Bi-weekly plan (2 services per month, 10% discount)
        biweekly_price = stripe.Price.create(
            product=mini_valet_product.id,
            unit_amount=6300,  # £63.00 (£35 * 2 * 0.90 for 10% discount)
            currency='gbp',
            recurring={'interval': 'month'},
            metadata={
                'frequency': 'biweekly',
                'services_per_month': '2',
                'discount': '10',
                'vehicle_type': 'small_car'
            }
        )
        mini_valet_prices.append(biweekly_price)
        
        # Weekly plan (4 services per month, 15% discount)
        weekly_price = stripe.Price.create(
            product=mini_valet_product.id,
            unit_amount=11900,  # £119.00 (£35 * 4 * 0.85 for 15% discount)
            currency='gbp',
            recurring={'interval': 'month'},
            metadata={
                'frequency': 'weekly',
                'services_per_month': '4',
                'discount': '15',
                'vehicle_type': 'small_car'
            }
        )
        mini_valet_prices.append(weekly_price)
        
        products_created.append({
            'product': mini_valet_product,
            'prices': mini_valet_prices
        })
        
        # 2. Full Valet Subscription Product
        print("Creating Full Valet Subscription product...")
        full_valet_product = stripe.Product.create(
            name="Full Valet Subscription",
            description="Complete premium cleaning service inside and out subscription",
            metadata={
                'service_type': 'full_valet',
                'duration': '120 minutes',
                'base_price': '80'
            }
        )
        
        # Create pricing plans for Full Valet
        full_valet_prices = []
        
        # Monthly plan (4 services per month, 15% discount)
        monthly_price = stripe.Price.create(
            product=full_valet_product.id,
            unit_amount=27200,  # £272.00 (£80 * 4 * 0.85 for 15% discount)
            currency='gbp',
            recurring={'interval': 'month'},
            metadata={
                'frequency': 'monthly',
                'services_per_month': '4',
                'discount': '15',
                'vehicle_type': 'small_car'
            }
        )
        full_valet_prices.append(monthly_price)
        
        # Bi-weekly plan (2 services per month, 10% discount)
        biweekly_price = stripe.Price.create(
            product=full_valet_product.id,
            unit_amount=14400,  # £144.00 (£80 * 2 * 0.90 for 10% discount)
            currency='gbp',
            recurring={'interval': 'month'},
            metadata={
                'frequency': 'biweekly',
                'services_per_month': '2',
                'discount': '10',
                'vehicle_type': 'small_car'
            }
        )
        full_valet_prices.append(biweekly_price)
        
        products_created.append({
            'product': full_valet_product,
            'prices': full_valet_prices
        })
        
        # 3. Premium Services (one-time purchases)
        print("Creating Premium Services products...")
        
        premium_services = [
            {
                'name': 'Interior Detailing',
                'description': 'Complete interior restoration and protection (2-3 hours)',
                'price': 14000,  # £140
                'duration': '2-3 hours'
            },
            {
                'name': 'Exterior Detailing', 
                'description': 'Professional paint correction and protection (4-5 hours)',
                'price': 26000,  # £260
                'duration': '4-5 hours'
            },
            {
                'name': 'Full Detailing',
                'description': 'Complete interior and exterior transformation (6-8 hours)',
                'price': 36000,  # £360
                'duration': '6-8 hours'
            },
            {
                'name': 'Stage 1 Polishing',
                'description': 'Professional single-stage machine polishing (3-4 hours)',
                'price': 45000,  # £450
                'duration': '3-4 hours'
            },
            {
                'name': 'Stage 2 Polishing',
                'description': 'Advanced two-stage polishing process (6+ hours)',
                'price': 65000,  # £650
                'duration': '6+ hours'
            }
        ]
        
        for service in premium_services:
            product = stripe.Product.create(
                name=service['name'],
                description=service['description'],
                metadata={
                    'service_type': 'premium',
                    'duration': service['duration']
                }
            )
            
            price = stripe.Price.create(
                product=product.id,
                unit_amount=service['price'],
                currency='gbp',
                metadata={
                    'service_type': 'premium',
                    'one_time': 'true'
                }
            )
            
            products_created.append({
                'product': product,
                'prices': [price]
            })
        
        print("✅ Successfully created all Stripe products and pricing plans!")
        print(f"📊 Total products created: {len(products_created)}")
        
        # Print summary
        print("\n📋 Product Summary:")
        for item in products_created:
            product = item['product']
            prices = item['prices']
            print(f"  • {product.name} (ID: {product.id})")
            for price in prices:
                amount = price.unit_amount / 100
                if price.recurring:
                    print(f"    - £{amount:.2f}/{price.recurring['interval']}")
                else:
                    print(f"    - £{amount:.2f} (one-time)")
        
        return products_created
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    products = create_subscription_products()
    if products:
        print("\n🎉 Stripe setup complete! Your subscription system is ready to accept payments.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
