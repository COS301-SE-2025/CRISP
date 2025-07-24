import React, { useState, useEffect, useRef } from 'react';
import CountryCodeDropdown from './CountryCodeDropdown.jsx';
import countryCodes from '../data/countryCodes.js';

const PhoneNumberInput = ({ 
  value = '', 
  onChange, 
  disabled = false,
  placeholder = 'Enter phone number',
  className = ''
}) => {
  // Parse existing value to extract country code and phone number
  const parsePhoneNumber = (phoneValue) => {
    if (!phoneValue) return { countryCode: 'US', phoneNumber: '' };
    
    // Try to find matching country code
    const matchingCountry = countryCodes.find(country => 
      phoneValue.startsWith(country.phoneCode)
    );
    
    if (matchingCountry) {
      return {
        countryCode: matchingCountry.code,
        phoneNumber: phoneValue.substring(matchingCountry.phoneCode.length).trim()
      };
    }
    
    // Default to US if no match found
    return { countryCode: 'US', phoneNumber: phoneValue };
  };

  const [selectedCountry, setSelectedCountry] = useState(() => {
    const parsed = parsePhoneNumber(value);
    return parsed.countryCode;
  });
  
  const [phoneNumber, setPhoneNumber] = useState(() => {
    const parsed = parsePhoneNumber(value);
    return parsed.phoneNumber;
  });

  // Use ref to store the latest onChange callback to avoid dependency issues
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  // Update parent component when country or phone number changes
  useEffect(() => {
    const selectedCountryData = countryCodes.find(c => c.code === selectedCountry);
    const fullPhoneNumber = phoneNumber 
      ? `${selectedCountryData.phoneCode} ${phoneNumber}`.trim()
      : '';
    
    if (onChangeRef.current) {
      onChangeRef.current(fullPhoneNumber);
    }
  }, [selectedCountry, phoneNumber]);

  const handleCountryChange = (country) => {
    setSelectedCountry(country.code);
  };

  const handlePhoneNumberChange = (e) => {
    // Remove any non-digit characters except spaces and dashes
    const cleaned = e.target.value.replace(/[^\d\s-]/g, '');
    setPhoneNumber(cleaned);
  };

  const formatPhoneNumber = (number) => {
    // Basic formatting - can be enhanced based on country-specific patterns
    const cleaned = number.replace(/\D/g, '');
    
    if (cleaned.length <= 3) return cleaned;
    if (cleaned.length <= 6) return `${cleaned.slice(0, 3)} ${cleaned.slice(3)}`;
    if (cleaned.length <= 10) return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`;
    
    return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6, 10)}`;
  };

  const containerStyles = {
    width: '100%'
  };

  const inputContainerStyles = {
    display: 'flex',
    gap: '8px',
    alignItems: 'stretch'
  };

  const phoneInputStyles = {
    flex: 1,
    padding: '8px 12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    transition: 'border-color 0.2s ease',
    outline: 'none',
    background: disabled ? '#f5f5f5' : 'white',
    cursor: disabled ? 'not-allowed' : 'text',
    opacity: disabled ? 0.6 : 1
  };

  return (
    <div className={className} style={containerStyles}>
      <div style={inputContainerStyles}>
        <CountryCodeDropdown
          selectedCountry={selectedCountry}
          onCountryChange={handleCountryChange}
          disabled={disabled}
          style={{ flexShrink: 0 }}
        />
        <input
          type="tel"
          value={phoneNumber}
          onChange={handlePhoneNumberChange}
          placeholder={placeholder}
          disabled={disabled}
          style={phoneInputStyles}
          maxLength={20}
        />
      </div>
    </div>
  );
};

export default PhoneNumberInput;