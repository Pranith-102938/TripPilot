/**
 * Formats a number as Indian Rupee (INR) currency string with proper lakh/crore commas.
 * @param {number} amount
 * @returns {string} e.g. "₹24,500"
 */
export function formatINR(amount) {
  if (amount === undefined || amount === null || isNaN(amount)) {
    return '₹0';
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
}

/**
 * Formats day string (e.g. "1 Day" vs "3 Days")
 */
export function formatDays(count) {
  return count === 1 ? '1 day' : `${count} days`;
}
