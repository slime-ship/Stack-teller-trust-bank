from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
import random
import string
from decimal import Decimal
from cloudinary.models import CloudinaryField
from datetime import datetime, timedelta

# ============ HELPER FUNCTIONS ============


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_account_number():
    return ''.join(str(random.randint(0, 9)) for _ in range(11))

def generate_otp():
    return ''.join(str(random.randint(0, 4)) for _ in range(6))

def generate_imf():
    return ''.join(str(random.randint(0, 4)) for _ in range(6))

def generate_aml():
    return ''.join(str(random.randint(0, 4)) for _ in range(6))

def generate_vat():
    return ''.join(str(random.randint(0, 4)) for _ in range(6))

def generate_tac():
    return ''.join(str(random.randint(0, 4)) for _ in range(6))


def generate_card_application_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def generate_card_number():
    return ''.join(random.choices(string.digits, k=16))

def generate_cvv():
    return ''.join(random.choices(string.digits, k=3))

def generate_expiry_date():
    future_date = datetime.now() + timedelta(days=365*3)
    return future_date.strftime("%m/%Y")


# ============ CRYPTO CURRENCY MODEL - MUST BE FIRST ============

class CryptoCurrency(models.Model):
    """Cryptocurrency types available in the system"""
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether (ERC20)'),
        ('USDC', 'USD Coin'),
        ('BSC', 'BNB Binance Smart Chain (BEP20)'),
        ('SOL', 'Solana'),
        ('XRP', 'Ripple'),
        ('DOGE', 'Dogecoin'),
        ('TRX', 'Tron'),
        ('MATIC', 'Polygon'),
        ('LTC', 'Litecoin'),
        ('ADA', 'Cardano'),
    ]

    code = models.CharField(max_length=10, choices=CRYPTO_CHOICES, unique=True)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, default='fab fa-bitcoin')
    min_deposit = models.DecimalField(max_digits=20, decimal_places=8, default=0.001)
    confirmations_required = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = "Cryptocurrencies"

    def __str__(self):
        return f"{self.name} ({self.code})"


# ============ CRYPTO WALLET ADDRESS MODEL ============

class CryptoWalletAddress(models.Model):
    """Multiple wallet addresses for different cryptocurrencies"""
    NETWORK_CHOICES = [
        ('ERC20', 'Ethereum (ERC20)'),
        ('TRC20', 'Tron (TRC20)'),
        ('BEP20', 'Binance (BEP20)'),
        ('SOL', 'Solana'),
        ('BTC', 'Bitcoin'),
        ('LTC', 'Litecoin'),
        ('XRP', 'Ripple'),
        ('DOGE', 'Dogecoin'),
        ('ADA', 'Cardano'),
        ('MATIC', 'Polygon'),
        ('AVAX', 'Avalanche C-Chain'),
    ]

    crypto = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE, related_name='wallet_addresses')
    address = models.CharField(max_length=500, verbose_name="Wallet Address")
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['crypto__name', '-is_primary', '-created_at']
        unique_together = ['crypto', 'address']

    def __str__(self):
        network_str = f" ({self.network})" if self.network else ""
        primary_str = " ★" if self.is_primary else ""
        return f"{self.crypto.name}{network_str}: {self.address[:20]}...{primary_str}"

    def get_short_address(self):
        if len(self.address) > 30:
            return f"{self.address[:15]}...{self.address[-10:]}"
        return self.address


# ============ SYSTEM CRYPTO SETTINGS ============

class SystemCryptoSetting(models.Model):
    """System-wide cryptocurrency settings"""
    auto_approve_deposits = models.BooleanField(default=False)
    deposit_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    min_deposit_amount = models.DecimalField(max_digits=20, decimal_places=8, default=10)
    max_deposit_amount = models.DecimalField(max_digits=20, decimal_places=8, default=100000)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "System Crypto Setting"
        verbose_name_plural = "System Crypto Settings"

    def __str__(self):
        return "System Crypto Settings"

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(id=1)
        return settings


# ============ USER PROFILE MODEL ============

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    refund_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    four_digit_auth_key = models.CharField(max_length=4, null=True, blank=True)

    OCCUPATION_CHOICES = [
        ('management', 'Management'),
        ('business_finance', 'Business and Financial Operations'),
        ('computer_math', 'Computer and Mathematical'),
        ('architecture_engineering', 'Architecture and Engineering'),
        ('life_sciences', 'Life, Physical, and Social Sciences'),
        ('community_social', 'Community and Social Service'),
        ('legal', 'Legal'),
        ('education', 'Education, Training, and Library'),
        ('arts_design', 'Arts, Design, Entertainment, Sports, and Media'),
        ('healthcare', 'Healthcare Practitioners and Technical'),
    ]

    occupation = models.CharField(max_length=50, default='select your occupation', choices=OCCUPATION_CHOICES, blank=True, null=True)
    next_of_kin = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(max_length=255, blank=True, null=True)
    zip_code = models.IntegerField(blank=True, null=True)

    TWO_FACTOR_CHOICES = [
        ('enable', 'Enable'),
        ('disable', 'Disable'),
    ]

    two_factor_auth = models.CharField(
        max_length=10,
        choices=TWO_FACTOR_CHOICES,
        default='Enable',
        blank=True,
    )

    card_application_fee_code = models.CharField(max_length=16, default=generate_card_application_code)
    cardholder_name = models.CharField(max_length=255, blank=True, null=True)
    card_number = models.CharField(max_length=16, default=generate_card_number)
    cvv = models.CharField(max_length=3, default=generate_cvv)
    expiry_date = models.CharField(max_length=7, default=generate_expiry_date)

    COUNTRY_CHOICES = [
        ('Afghanistan', 'Afghanistan'),
        ('Albania', 'Albania'),
        ('Algeria', 'Algeria'),
        ('Andorra', 'Andorra'),
        ('Angola', 'Angola'),
        ('Anguilla', 'Anguilla'),
        ('Antigua and Barbuda', 'Antigua and Barbuda'),
        ('Argentina', 'Argentina'),
        ('Armenia', 'Armenia'),
        ('Aruba', 'Aruba'),
        ('Australia', 'Australia'),
        ('Austria', 'Austria'),
        ('Azerbaijan', 'Azerbaijan'),
        ('Bahamas', 'Bahamas'),
        ('Bahrain', 'Bahrain'),
        ('Bangladesh', 'Bangladesh'),
        ('Barbados', 'Barbados'),
        ('Belarus', 'Belarus'),
        ('Belgium', 'Belgium'),
        ('Belize', 'Belize'),
        ('Benin', 'Benin'),
        ('Bermuda', 'Bermuda'),
        ('Bhutan', 'Bhutan'),
        ('Bolivia', 'Bolivia'),
        ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'),
        ('Botswana', 'Botswana'),
        ('Brazil', 'Brazil'),
        ('British Virgin Islands', 'British Virgin Islands'),
        ('Brunei', 'Brunei'),
        ('Bulgaria', 'Bulgaria'),
        ('Burkina Faso', 'Burkina Faso'),
        ('Burundi', 'Burundi'),
        ('Cambodia', 'Cambodia'),
        ('Cameroon', 'Cameroon'),
        ('Canada', 'Canada'),
        ('Cape Verde', 'Cape Verde'),
        ('Cayman Islands', 'Cayman Islands'),
        ('Central African Republic', 'Central African Republic'),
        ('Chad', 'Chad'),
        ('Chile', 'Chile'),
        ('China', 'China'),
        ('Colombia', 'Colombia'),
        ('Comoros', 'Comoros'),
        ('Congo', 'Congo'),
        ('Cook Islands', 'Cook Islands'),
        ('Costa Rica', 'Costa Rica'),
        ('Croatia', 'Croatia'),
        ('Cuba', 'Cuba'),
        ('Cyprus', 'Cyprus'),
        ('Czech Republic', 'Czech Republic'),
        ('Democratic Republic of the Congo', 'Democratic Republic of the Congo'),
        ('Denmark', 'Denmark'),
        ('Djibouti', 'Djibouti'),
        ('Dominica', 'Dominica'),
        ('Dominican Republic', 'Dominican Republic'),
        ('East Timor', 'East Timor'),
        ('Ecuador', 'Ecuador'),
        ('Egypt', 'Egypt'),
        ('El Salvador', 'El Salvador'),
        ('Equatorial Guinea', 'Equatorial Guinea'),
        ('Eritrea', 'Eritrea'),
        ('Estonia', 'Estonia'),
        ('Ethiopia', 'Ethiopia'),
        ('Faroe Islands', 'Faroe Islands'),
        ('Fiji', 'Fiji'),
        ('Finland', 'Finland'),
        ('France', 'France'),
        ('French Guiana', 'French Guiana'),
        ('French Polynesia', 'French Polynesia'),
        ('Gabon', 'Gabon'),
        ('Gambia', 'Gambia'),
        ('Georgia', 'Georgia'),
        ('Germany', 'Germany'),
        ('Ghana', 'Ghana'),
        ('Gibraltar', 'Gibraltar'),
        ('Greece', 'Greece'),
        ('Greenland', 'Greenland'),
        ('Grenada', 'Grenada'),
        ('Guadeloupe', 'Guadeloupe'),
        ('Guatemala', 'Guatemala'),
        ('Guinea', 'Guinea'),
        ('Guinea-Bissau', 'Guinea-Bissau'),
        ('Guyana', 'Guyana'),
        ('Haiti', 'Haiti'),
        ('Honduras', 'Honduras'),
        ('Hong Kong', 'Hong Kong'),
        ('Hungary', 'Hungary'),
        ('Iceland', 'Iceland'),
        ('India', 'India'),
        ('Indonesia', 'Indonesia'),
        ('Iran', 'Iran'),
        ('Iraq', 'Iraq'),
        ('Ireland', 'Ireland'),
        ('Israel', 'Israel'),
        ('Italy', 'Italy'),
        ('Ivory Coast', 'Ivory Coast'),
        ('Jamaica', 'Jamaica'),
        ('Japan', 'Japan'),
        ('Jordan', 'Jordan'),
        ('Kazakhstan', 'Kazakhstan'),
        ('Kenya', 'Kenya'),
        ('Kiribati', 'Kiribati'),
        ('Kuwait', 'Kuwait'),
        ('Kyrgyzstan', 'Kyrgyzstan'),
        ('Laos', 'Laos'),
        ('Latvia', 'Latvia'),
        ('Lebanon', 'Lebanon'),
        ('Lesotho', 'Lesotho'),
        ('Liberia', 'Liberia'),
        ('Libya', 'Libya'),
        ('Liechtenstein', 'Liechtenstein'),
        ('Lithuania', 'Lithuania'),
        ('Luxembourg', 'Luxembourg'),
        ('Macau', 'Macau'),
        ('Macedonia', 'Macedonia'),
        ('Madagascar', 'Madagascar'),
        ('Malawi', 'Malawi'),
        ('Malaysia', 'Malaysia'),
        ('Maldives', 'Maldives'),
        ('Mali', 'Mali'),
        ('Malta', 'Malta'),
        ('Marshall Islands', 'Marshall Islands'),
        ('Martinique', 'Martinique'),
        ('Mauritania', 'Mauritania'),
        ('Mauritius', 'Mauritius'),
        ('Mayotte', 'Mayotte'),
        ('Mexico', 'Mexico'),
        ('Micronesia', 'Micronesia'),
        ('Moldova', 'Moldova'),
        ('Monaco', 'Monaco'),
        ('Mongolia', 'Mongolia'),
        ('Montenegro', 'Montenegro'),
        ('Montserrat', 'Montserrat'),
        ('Morocco', 'Morocco'),
        ('Mozambique', 'Mozambique'),
        ('Myanmar', 'Myanmar'),
        ('Namibia', 'Namibia'),
        ('Nauru', 'Nauru'),
        ('Nepal', 'Nepal'),
        ('Netherlands', 'Netherlands'),
        ('New Caledonia', 'New Caledonia'),
        ('New Zealand', 'New Zealand'),
        ('Nicaragua', 'Nicaragua'),
        ('Niger', 'Niger'),
        ('Nigeria', 'Nigeria'),
        ('Niue', 'Niue'),
        ('Norfolk Island', 'Norfolk Island'),
        ('North Korea', 'North Korea'),
        ('Norway', 'Norway'),
        ('Oman', 'Oman'),
        ('Pakistan', 'Pakistan'),
        ('Palau', 'Palau'),
        ('Palestinian Territory', 'Palestinian Territory'),
        ('Panama', 'Panama'),
        ('Papua New Guinea', 'Papua New Guinea'),
        ('Paraguay', 'Paraguay'),
        ('Peru', 'Peru'),
        ('Philippines', 'Philippines'),
        ('Poland', 'Poland'),
        ('Portugal', 'Portugal'),
        ('Qatar', 'Qatar'),
        ('Reunion', 'Reunion'),
        ('Romania', 'Romania'),
        ('Russia', 'Russia'),
        ('Rwanda', 'Rwanda'),
        ('Saint Barthelemy', 'Saint Barthelemy'),
        ('Saint Helena', 'Saint Helena'),
        ('Saint Kitts and Nevis', 'Saint Kitts and Nevis'),
        ('Saint Lucia', 'Saint Lucia'),
        ('Saint Martin', 'Saint Martin'),
        ('Saint Pierre and Miquelon', 'Saint Pierre and Miquelon'),
        ('Saint Vincent and the Grenadines', 'Saint Vincent and the Grenadines'),
        ('Samoa', 'Samoa'),
        ('San Marino', 'San Marino'),
        ('Sao Tome and Principe', 'Sao Tome and Principe'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Senegal', 'Senegal'),
        ('Serbia', 'Serbia'),
        ('Seychelles', 'Seychelles'),
        ('Sierra Leone', 'Sierra Leone'),
        ('Singapore', 'Singapore'),
        ('Slovakia', 'Slovakia'),
        ('Slovenia', 'Slovenia'),
        ('Solomon Islands', 'Solomon Islands'),
        ('Somalia', 'Somalia'),
        ('South Africa', 'South Africa'),
        ('South Korea', 'South Korea'),
        ('South Sudan', 'South Sudan'),
        ('Spain', 'Spain'),
        ('Sri Lanka', 'Sri Lanka'),
        ('Sudan', 'Sudan'),
        ('Suriname', 'Suriname'),
        ('Swaziland', 'Swaziland'),
        ('Sweden', 'Sweden'),
        ('Switzerland', 'Switzerland'),
        ('Syria', 'Syria'),
        ('Taiwan', 'Taiwan'),
        ('Tajikistan', 'Tajikistan'),
        ('Tanzania', 'Tanzania'),
        ('Thailand', 'Thailand'),
        ('Togo', 'Togo'),
        ('Tonga', 'Tonga'),
        ('Trinidad and Tobago', 'Trinidad and Tobago'),
        ('Tunisia', 'Tunisia'),
        ('Turkey', 'Turkey'),
        ('Turkmenistan', 'Turkmenistan'),
        ('Turks and Caicos Islands', 'Turks and Caicos Islands'),
        ('Tuvalu', 'Tuvalu'),
        ('Uganda', 'Uganda'),
        ('Ukraine', 'Ukraine'),
        ('United Arab Emirates', 'United Arab Emirates'),
        ('United Kingdom', 'United Kingdom'),
        ('United States', 'United States'),
        ('Uruguay', 'Uruguay'),
        ('Uzbekistan', 'Uzbekistan'),
        ('Vanuatu', 'Vanuatu'),
        ('Vatican City', 'Vatican City'),
        ('Venezuela', 'Venezuela'),
        ('Vietnam', 'Vietnam'),
        ('Yemen', 'Yemen'),
        ('Zambia', 'Zambia'),
        ('Zimbabwe', 'Zimbabwe'),
        ('Western Sahara', 'Western Sahara'),
        ('South Georgia and the South Sandwich Islands', 'South Georgia and the South Sandwich Islands'),
        ('Saint Kitts and Nevis', 'Saint Kitts and Nevis'),
        ('Saint Lucia', 'Saint Lucia'),
        ('Saint Martin', 'Saint Martin'),
        ('Saint Pierre and Miquelon', 'Saint Pierre and Miquelon'),
        ('Saint Vincent and the Grenadines', 'Saint Vincent and the Grenadines'),
        ('Samoa', 'Samoa'),
        ('San Marino', 'San Marino'),
        ('Sao Tome and Principe', 'Sao Tome and Principe'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Senegal', 'Senegal'),
        ('Serbia', 'Serbia'),
        ('Seychelles', 'Seychelles'),
        ('Sierra Leone', 'Sierra Leone'),
        ('Singapore', 'Singapore'),
        ('Slovakia', 'Slovakia'),
        ('Slovenia', 'Slovenia'),
        ('Solomon Islands', 'Solomon Islands'),
        ('Somalia', 'Somalia'),
        ('South Africa', 'South Africa'),
        ('South Korea', 'South Korea'),
        ('South Sudan', 'South Sudan'),
        ('Spain', 'Spain'),
        ('Sri Lanka', 'Sri Lanka'),
        ('Sudan', 'Sudan'),
        ('Suriname', 'Suriname'),
        ('Swaziland', 'Swaziland'),
        ('Sweden', 'Sweden'),
        ('Switzerland', 'Switzerland'),
        ('Syria', 'Syria'),
        ('Taiwan', 'Taiwan'),
        ('Tajikistan', 'Tajikistan'),
        ('Tanzania', 'Tanzania'),
        ('Thailand', 'Thailand'),
        ('Togo', 'Togo'),
        ('Tonga', 'Tonga'),
        ('Trinidad and Tobago', 'Trinidad and Tobago'),
        ('Tunisia', 'Tunisia'),
        ('Turkey', 'Turkey'),
        ('Turkmenistan', 'Turkmenistan'),
        ('Turks and Caicos Islands', 'Turks and Caicos Islands'),
        ('Tuvalu', 'Tuvalu'),
        ('Uganda', 'Uganda'),
        ('Ukraine', 'Ukraine'),
        ('United Arab Emirates', 'United Arab Emirates'),
        ('United Kingdom', 'United Kingdom'),
        ('United States', 'United States'),
        ('Uruguay', 'Uruguay'),
        ('Uzbekistan', 'Uzbekistan'),
        ('Vanuatu', 'Vanuatu'),
        ('Vatican City', 'Vatican City'),
        ('Venezuela', 'Venezuela'),
        ('Vietnam', 'Vietnam'),
        ('Yemen', 'Yemen'),
        ('Zambia', 'Zambia'),
        ('Zimbabwe', 'Zimbabwe'),
    ]
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, blank=True)
    currency_choices = currency_choices = [
        ('$', 'US Dollar'),
        ('€', 'Euro'),
        ('£', 'British Pound'),
        ('¥', 'Japanese Yen'),
        ('A$', 'Australian Dollar'),
        ('C$', 'Canadian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('¥', 'Chinese Yuan'),
        ('kr', 'Swedish Krona'),
        ('$', 'New Zealand Dollar'),
        ('₩', 'South Korean Won'),
        ('$', 'Singapore Dollar'),
        ('kr', 'Norwegian Krone'),
        ('$', 'Mexican Peso'),
        ('₹', 'Indian Rupee'),
        ('₽', 'Russian Ruble'),
        ('R', 'South African Rand'),
        ('R$', 'Brazilian Real'),
        ('₺', 'Turkish Lira'),
        ('$', 'Hong Kong Dollar'),
        ('Rp', 'Indonesian Rupiah'),
        ('RM', 'Malaysian Ringgit'),
        ('₱', 'Philippine Peso'),
        ('฿', 'Thai Baht'),
        ('kr', 'Danish Krone'),
        ('zł', 'Polish Zloty'),
        ('Ft', 'Hungarian Forint'),
        ('Kč', 'Czech Koruna'),
        ('₪', 'Israeli Shekel'),
        ('$', 'Chilean Peso'),
        ('E£', 'Egyptian Pound'),
        ('₴', 'Ukrainian Hryvnia'),
        ('د.إ', 'United Arab Emirates Dirham'),
        ('$', 'Argentine Peso'),
        ('ر.س', 'Saudi Riyal'),
        ('ر.ق', 'Qatari Riyal'),
        ('د.ك', 'Kuwaiti Dinar'),
        ('₦', 'Nigerian Naira'),
        ('৳', 'Bangladeshi Taka'),
        ('₫', 'Vietnamese Dong'),
        ('$', 'Colombian Peso'),
        ('lei', 'Romanian Leu'),
        ('S/', 'Peruvian Sol'),
        ('₨', 'Pakistani Rupee'),
        ('₨', 'Sri Lankan Rupee'),
        ('kn', 'Croatian Kuna'),
        ('лв', 'Bulgarian Lev'),
        ('د.ج', 'Algerian Dinar'),
        ('﷼', 'Iranian Rial'),
        ('$', 'Taiwan Dollar'),
        ('₾', 'Georgian Lari'),
        ('BYN', 'Belarusian Ruble'),
        ('₸', 'Kazakhstani Tenge'),
        ('د.م.', 'Moroccan Dirham'),
        ('Bs', 'Venezuelan Bolívar'),
        ('ብር', 'Ethiopian Birr'),
        ('Sh', 'Ugandan Shilling'),
        ('ج.س.', 'Sudanese Pound'),
        ('₨', 'Nepalese Rupee'),
        ('FCFA', 'Central African CFA Franc'),
        ('CFA', 'West African CFA Franc'),
        ('$', 'East Caribbean Dollar'),
        ('Sh', 'Tanzanian Shilling'),
        ('₵', 'Ghanaian Cedi'),
        ('Sh', 'Kenyan Shilling'),
        ('MT', 'Mozambican Metical'),
        ('Kz', 'Angolan Kwanza'),
        ('Sh', 'Ugandan Shilling'),
        ('د.ت', 'Tunisian Dinar'),
        ('ل.ل', 'Lebanese Pound'),
        ('د.أ', 'Jordanian Dinar'),
        ('Q', 'Guatemalan Quetzal'),
        ('₲', 'Paraguayan Guarani'),
        ('Bs', 'Bolivian Boliviano'),
        ('₣', 'CFP Franc'),
        ('$', 'Bahamian Dollar'),
        ('$', 'Barbadian Dollar'),
        ('$', 'Bermudian Dollar'),
        ('$', 'Fijian Dollar'),
        ('$', 'Guyanese Dollar'),
        ('$', 'Guyanese Dollar'),
        ('L', 'Honduran Lempira'),
        ('J$', 'Jamaican Dollar'),
        ('៛', 'Cambodian Riel'),
        ('с', 'Kyrgyzstani Som'),
        ('₭', 'Lao Kip'),
        ('₨', 'Sri Lankan Rupee'),
        ('Ar', 'Malagasy Ariary'),
        ('lei', 'Moldovan Leu'),
        ('ден', 'Macedonian Denar'),
        ('Ks', 'Myanmar Kyat'),
        ('MOP$', 'Macau Pataca'),
        ('₨', 'Mauritian Rupee'),
        ('Rf', 'Maldivian Rufiyaa'),
        ('MK', 'Malawian Kwacha'),
        ('$', 'Namibian Dollar'),
        ('C$', 'Nicaraguan Córdoba'),
        ('K', 'Papua New Guinean Kina'),
        ('din', 'Serbian Dinar'),
        ('₨', 'Seychellois Rupee'),
        ('£', 'Syrian Pound'),
        ('SM', 'Tajikistani Somoni'),
        ('T$', 'Tongan Paʻanga'),
        ('$', 'Trinidad and Tobago Dollar'),
        ('T', 'Turkmenistan Manat'),
        ('Sh', 'Tanzanian Shilling'),
        ('Sh', 'Ugandan Shilling'),
        ('$', 'Uruguayan Peso'),
        ('лв', 'Uzbekistani Som'),
        ('Vt', 'Vanuatu Vatu'),
        ('T', 'Samoan Tala'),
        ('FCFA', 'Central African CFA Franc'),
        ('SDR', 'Special Drawing Rights'),
        ('CFA', 'West African CFA Franc'),
        ('﷼', 'Yemeni Rial'),
        ('ZK', 'Zambian Kwacha'),
    ]

    currency = models.CharField(max_length=4, choices=currency_choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    working_choices = [('Employed', 'Employed'), ('Unemployed', 'Unemployed'), ('Retired', 'Retired'), ('Student', 'Student'), ('Others', 'Others')]
    status = models.CharField(max_length=50, choices=working_choices, blank=True)

    gender_choices = [('Male', 'Male'), ('Female', 'Female')]
    Gender = models.CharField(max_length=50, choices=gender_choices, blank=True)

    account_choices = [('Online Account', 'Online Account'), ('Checking Account', 'Checking Account'), ('Current Account', 'Current Account'), ('Corporate Account', 'Corporate Account'), ('Offshore Account', 'Offshore Account'), ('Joint Account', 'Joint Account')]
    account_type = models.CharField(max_length=50, choices=account_choices, blank=True)

    profile_pic = CloudinaryField('profile_pic', null=True, blank=True)
    account_number = models.CharField(max_length=11, default=generate_account_number)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True)
    linking_code = models.CharField(max_length=11, default=generate_code)
    tax_code = models.CharField(max_length=11, default=generate_otp)
    imf_code = models.CharField(max_length=11, default=generate_imf)
    bic_code = models.CharField(max_length=11, default=generate_aml)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_linked = models.BooleanField(default=False)
    is_upgraded = models.BooleanField(default=False)
    frozenState = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = generate_account_number()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        auth_key_str = str(self.four_digit_auth_key) if self.four_digit_auth_key is not None else ''
        if self.two_factor_auth == 'enable':
            if not auth_key_str.isdigit() or len(auth_key_str) != 4:
                raise ValidationError({
                    'four_digit_auth_key': 'A 4-digit numeric authentication key is required.'
                })
        else:
            self.four_digit_auth_key = None

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    previous_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    tx_type = models.CharField(max_length=10, choices=[('CREDIT', 'Credit'), ('DEBIT', 'Debit')], default='CREDIT')
    transaction_type = models.CharField(max_length=50, default='Transfer')
    status = models.CharField(max_length=50, default='Successful')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} - {self.user.username} - {self.timestamp}"
class UserInvestment(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    investment_plan = models.ForeignKey('InvestmentPlan', on_delete=models.CASCADE)
    amount_invested = models.DecimalField(max_digits=15, decimal_places=2)
    expected_return = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_expected_return(self):
        daily_rate = self.investment_plan.interest_rate / 365 / 100
        days = self.investment_plan.duration_days
        return self.amount_invested * (1 + daily_rate * days)

    def save(self, *args, **kwargs):
        if not self.expected_return:
            self.expected_return = self.calculate_expected_return()
        if not self.end_date:
            from django.utils import timezone
            from datetime import timedelta
            self.end_date = timezone.now() + timedelta(days=self.investment_plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.investment_plan.name} - ${self.amount_invested}"

class InvestmentTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('INVESTMENT', 'Investment'),
        ('RETURN', 'Return'),
        ('BONUS', 'Bonus'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    investment = models.ForeignKey(UserInvestment, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"

class InvestmentPlan(models.Model):
    PLAN_TYPES = [
        ('BASIC', 'Basic Plan'),
        ('STANDARD', 'Standard Plan'),
        ('PREMIUM', 'Premium Plan'),
        ('VIP', 'VIP Plan'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, default=100.00)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Annual percentage
    duration_days = models.IntegerField()  # Investment duration in days
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.interest_rate}%"

# Consolidated Transaction model defined above

