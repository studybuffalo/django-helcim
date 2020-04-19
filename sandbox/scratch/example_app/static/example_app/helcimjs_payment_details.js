function displayError(errors, targetID) {
  // Get the error span and clear it for new errors
  const errorSpan = document.getElementById(targetID);
  errorSpan.innerHTML = '';

  // Format the error list
  const errorList = document.createElement('ul');
  errorList.classList.add('errorlist');

  // Add each error as a list item
  for (let error of errors) {
    const errorItem = document.createElement('li');
    errorItem.innerText = error;
    errorList.appendChild(errorItem);
  }

  // Add error list to DOM
  errorSpan.appendChild(errorList);
}

function assembleExpiryDate(month, year) {
  // Function determines what the next month and year is and uses
  // this to work backwards to get the last of the month (the actual)
  // Expiry date.

  if (month < 12) {
    // Next month is in the same year - can just assemble date
    // Can just use existing month integer as months are 0-based
    return new Date(year, month, 0);
  }

  // In this case, we need to move to January of next year
  return new Date(year + 1, 0, 0);
}

function validateFormDetails() {
  // CONFIRM CARD NUMBER DETAILS
  const ccNumber = document.getElementById('id_django_cc_number').value.trim();
  const ccNumberErrors = [];

  // Confirms this value only contains digits and is 13 to 16 characters
  if (/^\d{13,16}$/.test(ccNumber) === false) {
    ccNumberErrors.push('Number must be 13 to 16 digits long (no spaces).');
  }

  // CONFIRM CARDHOLDER NAME DETAILS
  const ccName = document.getElementById('id_django_cc_name').value.trim();
  const ccNameErrors = [];

  // Confirm length is under 256 characters
  if (ccName.length > 256) {
    ccNameErrors.push('Cardholder name must be less than 256 characters.');
  }

  // CONFIRM CVV DETAILS
  const ccCVV = document.getElementById('id_django_cc_cvv').value.trim();
  const ccCVVErrors = [];

  // Confirm CVV is 3 or 4 digits long
  if (/^\d{3,4}$/.test(ccCVV) === false) {
    ccCVVErrors.push('CVV must be 3 or 4 digits long.');
  }

  // CONFIRM EXPIRY DETAILS
  const ccExpiryMonth = document.getElementById('id_django_cc_expiry_month').value;
  const ccExpiryYear = document.getElementById('id_django_cc_expiry_year').value;
  const ccExpiryErrors = [];

  // Confirm each component is 2 digits long
  if (/^(01|02|03|04|05|06|07|08|09|10|11|12)$/.test(ccExpiryMonth) === false) {
    ccExpiryErrors.push('Please enter month as two digits (01 = January, 12 = December).');
  }

  if (/^\d{2}$/.test(ccExpiryYear) === false) {
    ccExpiryErrors.push('Please enter year as two digits (2022 = 22, 2030 = 30).');
  }

  // Confirm card is not expired
  const monthInt = Number(ccExpiryMonth);
  const yearInt = Number(`20${ccExpiryYear}`);
  const ccExpiry = assembleExpiryDate(monthInt, yearInt);
  const today = new Date();

  if (ccExpiry < today) {
    ccExpiryErrors.push('Credit card is expired - confirm expiry date details.');
  }

  // Confirm amount details
  const amount = document.getElementById('id_django_amount').value;
  const ccAmountErrors = [];

  if (/^\d{0,13}\.{0,1}\d{0,2}$/.test(amount) === false) {
    ccAmountErrors.push('Please enter year as two digits (2022 = 22, 2030 = 30).');
  }

  // Update any error displays
  let valid = true;

  if (ccNumberErrors.length > 0) {
    valid = false;
    displayError(ccNumberErrors, 'django-cc-number-errors');
  }

  if (ccNameErrors.length > 0) {
    valid = false;
    displayError(ccNameErrors, 'django-cc-name-errors');
  }

  if (ccExpiryErrors.length > 0) {
    valid = false;
    displayError(ccExpiryErrors, 'django-cc-expiry-errors');
  }

  if (ccCVVErrors.length > 0) {
    valid = false;
    displayError(ccCVVErrors, 'django-cc-cvv-errors');
  }

  if (ccAmountErrors.length > 0) {
    valid = false;
    displayError(ccAmountErrors, 'django-amount-errors');
  }

  // Return true if no errors, otherwise return false
  return valid;
}

function formatCurrency(value) {
  // Split into dollars and cents
  splitValue = value.split('.');

  // Format the cents
  let cents = '';

  if (splitValue.length > 1) {
    if (splitValue[1].length == 0) {
      cents = '00'
    } else if (splitValue[1].length == 1) {
      cents = `${splitValue[1]}0`;
    } else {
      cents = splitValue[1];
    }
  } else {
    cents = '00'
  }

  // Convert dollars to a number to strip leading zeros
  const dollars = Number(splitValue[0])

  // Assemble final value
  return `$${dollars}.${cents}`;
}

function showConfirmationDetails() {
  // Confirm entered details into form are valid
  const formValid = validateFormDetails();

  // If form is not valid, stop processing and let user fix issues
  if (formValid === false) {
    return;
  }

  // Get all relevant form values to format and insert into required locations
  const ccNumber = document.getElementById('id_django_cc_number').value.trim();
  const ccName = document.getElementById('id_django_cc_name').value.trim();
  const ccCVV = document.getElementById('id_django_cc_cvv').value.trim();
  const ccExpiryMonth = document.getElementById('id_django_cc_expiry_month').value;
  const ccExpiryYear = document.getElementById('id_django_cc_expiry_year').value;
  const amount = document.getElementById('id_django_amount').value;

  // Format CC number and update display
  const ccLength = ccNumber.length;
  const ccNumberFirst = ccNumber.substring(0, 4);
  const ccNumberLast = ccNumber.substring(ccLength - 4, ccLength);
  const confirmationCCNumber = document.getElementById('confirmation-cc-number');
  confirmationCCNumber.innerText = `${ccNumberFirst}${'*'.repeat(ccLength - 8)}${ccNumberLast}`;

  // Update Cardholder Name display
  const confirmationCCName = document.getElementById('confirmation-cc-name');
  confirmationCCName.innerText = ccName;

  // Format CC expiry and update display
  const confirmationCCExpiry = document.getElementById('confirmation-cc-expiry');
  confirmationCCExpiry.innerText = `${ccExpiryMonth}/${ccExpiryYear}`;

  // Format amount and update display
  const confirmationAmount = document.getElementById('confirmation-amount');
  confirmationAmount.innerText = formatCurrency(amount);

  // Update the Helcim.js form inputs for submission
  document.getElementById('cardNumber').value = ccNumber;
  document.getElementById('cardExpiry').value = `${ccExpiryMonth}${ccExpiryYear}`;
  document.getElementById('cardCVV').value = ccCVV;
  document.getElementById('cardHolderName').value = ccName;
  document.getElementById('amount').value = amount;

  // Update displays to progress to confirmation view
  document.getElementById('header-payment').classList.add('hide');
  document.getElementById('payment-form').classList.add('hide');
  document.getElementById('header-confirmation').classList.remove('hide');
  document.getElementById('confirmation-details').classList.remove('hide');
}

function showPaymentDetails() {
  // Update displays
  document.getElementById('header-payment').classList.remove('hide');
  document.getElementById('payment-form').classList.remove('hide');
  document.getElementById('header-confirmation').classList.add('hide');
  document.getElementById('confirmation-details').classList.add('hide');
}

window.addEventListener('load', () => {
  const proceedToConfirmationButton = document.getElementById('proceed-to-confirmation');
  proceedToConfirmationButton.addEventListener('click', (e) => {
      showConfirmationDetails();
  });

  const backToDetailsButton = document.getElementById('back-to-details');
  backToDetailsButton.addEventListener('click', (e) => {
    showPaymentDetails();
  })
});
