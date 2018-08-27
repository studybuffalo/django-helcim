# import environ
# import requests
# from xml.etree import ElementTree


# ROOT_DIR = environ.Path(__file__) - 1

# env = environ.Env()
# env.read_env(env_file=ROOT_DIR.file('settings.env'))

# HELCIM_ACCOUNT_ID = env('HELCIM_ACCOUNT_ID')
# HELCIM_API_TOKEN = env('HELCIM_API_TOKEN')
# HELCIM_API_URL = env('HELCIM_API_URL')

# CC_NUMBER = env('TEST_MC_NUMBER')
# CC_EXPIRY_MONTH = env('TEST_MC_EXPIRY_MONTH')
# CC_EXPIRY_YEAR = env('TEST_MC_EXPIRY_YEAR')
# CC_EXPIRY = '{}{}'.format(CC_EXPIRY_MONTH, CC_EXPIRY_YEAR)
# CC_CVV = env('TEST_MC_CVV')

# post_data = {
#     'accountId': HELCIM_ACCOUNT_ID,
#     'apiToken': HELCIM_API_TOKEN,
#     'test': 1,
#     'transactionType': 'purchase',
#     'amount': 100.00,
#     'cardHolderName': 'Test Person',
#     'cardNumber': CC_NUMBER,
#     'cardExpiry': CC_EXPIRY,
#     'cardCVV': CC_CVV,
#     'cardHolderAddress': '1234 Fake Street',
#     'cardHolderPostalCode': '1T10T0',
# }

# # POST
# response = requests.post(HELCIM_API_URL, data=post_data)

# # GET XML RESPONSE
# xmlResponse = ElementTree.fromstring(response.content)

# # PRINT RESPONSE XML
# print(response.text)
