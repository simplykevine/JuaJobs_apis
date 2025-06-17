import re
from django.core.exceptions import ValidationError
from django.conf import settings

class AfricanPhoneValidator:
    """Validator for African phone number formats"""
    
    def __init__(self, country_code=None):
        self.country_code = country_code
    
    def __call__(self, value):
        if not value:
            return
        
        # If country code is provided, validate against specific pattern
        if self.country_code:
            country_config = settings.AFRICAN_COUNTRIES.get(self.country_code)
            if country_config:
                pattern = country_config['phone_pattern']
                if not re.match(pattern, value):
                    raise ValidationError(
                        f'Invalid phone number format for {country_config["name"]}. '
                        f'Expected format: {pattern}'
                    )
        else:
            # Validate against all African patterns
            valid = False
            for country_code, config in settings.AFRICAN_COUNTRIES.items():
                if re.match(config['phone_pattern'], value):
                    valid = True
                    break
            
            if not valid:
                raise ValidationError('Invalid African phone number format')

class CurrencyValidator:
    """Validator for African currencies"""
    
    def __call__(self, value):
        if not value:
            return
        
        valid_currencies = [config['currency'] for config in settings.AFRICAN_COUNTRIES.values()]
        valid_currencies.extend(['USD', 'EUR'])  # Add international currencies
        
        if value not in valid_currencies:
            raise ValidationError(f'Currency {value} is not supported. Valid currencies: {", ".join(valid_currencies)}')

class MobileMoneyValidator:
    """Validator for mobile money payment methods"""
    
    def __call__(self, payment_type, phone_number, country):
        if payment_type not in settings.MOBILE_MONEY_PROVIDERS:
            raise ValidationError(f'Mobile money provider {payment_type} is not supported')
        
        provider_config = settings.MOBILE_MONEY_PROVIDERS[payment_type]
        
        if country not in provider_config['countries']:
            raise ValidationError(
                f'{payment_type} is not available in {country}. '
                f'Available countries: {", ".join(provider_config["countries"])}'
            )
        
        # Validate phone number format
        validator = AfricanPhoneValidator(country)
        validator(phone_number)
