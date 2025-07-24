import React, { useState, useRef, useEffect } from 'react';
import countryCodes from '../data/countryCodes.js';

const CountryCodeDropdown = ({ 
  selectedCountry = 'US', 
  onCountryChange, 
  disabled = false,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dropdownPosition, setDropdownPosition] = useState('below');
  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);
  const buttonRef = useRef(null);

  // Find selected country data
  const selectedCountryData = countryCodes.find(country => country.code === selectedCountry) || countryCodes[0];

  // Filter countries based on search term
  const filteredCountries = countryCodes.filter(country =>
    country.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    country.phoneCode.includes(searchTerm) ||
    country.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when dropdown opens and calculate position
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
      
      // Calculate dropdown position
      if (buttonRef.current) {
        const buttonRect = buttonRef.current.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const dropdownHeight = 300; // max height of dropdown
        const spaceBelow = viewportHeight - buttonRect.bottom;
        const spaceAbove = buttonRect.top;
        
        // Position above if there's more space above or not enough space below
        if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
          setDropdownPosition('above');
        } else {
          setDropdownPosition('below');
        }
      }
    }
  }, [isOpen]);

  const handleCountrySelect = (country) => {
    onCountryChange(country);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleKeyDown = (event, country) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleCountrySelect(country);
    }
  };

  const dropdownStyles = {
    position: 'relative',
    display: 'inline-block'
  };

  const selectorStyles = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '8px 12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    background: disabled ? '#f5f5f5' : 'white',
    cursor: disabled ? 'not-allowed' : 'pointer',
    minWidth: '120px',
    fontSize: '14px',
    transition: 'border-color 0.2s ease',
    opacity: disabled ? 0.6 : 1
  };

  const selectedCountryStyles = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  };

  const dropdownMenuStyles = {
    position: 'absolute',
    ...(dropdownPosition === 'above' 
      ? { bottom: '100%', marginBottom: '4px' } 
      : { top: '100%', marginTop: '4px' }
    ),
    left: 0,
    right: 0,
    background: 'white',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    zIndex: 1000,
    maxHeight: '300px',
    overflow: 'hidden'
  };

  const searchContainerStyles = {
    padding: '8px',
    borderBottom: '1px solid #eee'
  };

  const searchInputStyles = {
    width: '100%',
    padding: '6px 8px',
    border: '1px solid #ddd',
    borderRadius: '3px',
    fontSize: '14px',
    outline: 'none'
  };

  const countriesListStyles = {
    maxHeight: '200px',
    overflowY: 'auto',
    margin: 0,
    padding: 0,
    listStyle: 'none'
  };

  const getCountryOptionStyles = (isSelected) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 12px',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
    border: 'none',
    outline: 'none',
    backgroundColor: isSelected ? '#e3f2fd' : 'transparent',
    color: isSelected ? '#1976d2' : '#333'
  });

  const countryInfoStyles = {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    flex: 1
  };

  const countryNameStyles = {
    fontSize: '14px',
    fontWeight: '500'
  };

  const countryCodeStyles = {
    fontSize: '12px',
    color: '#666',
    fontWeight: '400'
  };

  return (
    <div className={className} style={dropdownStyles} ref={dropdownRef}>
      <button
        ref={buttonRef}
        type="button"
        style={selectorStyles}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span style={selectedCountryStyles}>
          <span style={{ fontSize: '16px' }}>{selectedCountryData.emoji}</span>
          <span style={{ fontWeight: '500', color: '#333' }}>{selectedCountryData.phoneCode}</span>
        </span>
        <span style={{ fontSize: '10px', color: '#666', transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}>▼</span>
      </button>

      {isOpen && !disabled && (
        <div style={dropdownMenuStyles}>
          <div style={searchContainerStyles}>
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search countries..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={searchInputStyles}
            />
          </div>
          <ul style={countriesListStyles} role="listbox">
            {filteredCountries.map((country) => (
              <li
                key={country.code}
                style={getCountryOptionStyles(selectedCountry === country.code)}
                onClick={() => handleCountrySelect(country)}
                onKeyDown={(e) => handleKeyDown(e, country)}
                onMouseEnter={(e) => e.target.style.backgroundColor = selectedCountry === country.code ? '#e3f2fd' : '#f8f9fa'}
                onMouseLeave={(e) => e.target.style.backgroundColor = selectedCountry === country.code ? '#e3f2fd' : 'transparent'}
                role="option"
                aria-selected={selectedCountry === country.code}
                tabIndex={0}
              >
                <span style={{ fontSize: '16px' }}>{country.emoji}</span>
                <span style={countryInfoStyles}>
                  <span style={countryNameStyles}>{country.name}</span>
                  <span style={{...countryCodeStyles, color: selectedCountry === country.code ? '#1976d2' : '#666'}}>{country.phoneCode}</span>
                </span>
              </li>
            ))}
          </ul>
          {filteredCountries.length === 0 && (
            <div style={{ padding: '16px', textAlign: 'center', color: '#666', fontStyle: 'italic' }}>No countries found</div>
          )}
        </div>
      )}

    </div>
  );
};

export default CountryCodeDropdown;