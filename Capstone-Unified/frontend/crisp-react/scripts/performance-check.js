#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Performance warning thresholds
const THRESHOLDS = {
  MAX_CONSOLE_LOGS: 50,      // Max console.log statements
  MIN_INTERVAL_MS: 60000,    // Min interval time (1 minute)
  MAX_SETINTERVALS: 10       // Max setInterval calls
};

function checkPerformance() {
  const srcDir = path.join(__dirname, '../src');
  const issues = [];

  function scanDirectory(dir) {
    const files = fs.readdirSync(dir);

    files.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);

      if (stat.isDirectory()) {
        scanDirectory(filePath);
      } else if (file.endsWith('.jsx') || file.endsWith('.js')) {
        checkFile(filePath);
      }
    });
  }

  function checkFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');

    let consoleCount = 0;
    let intervalCount = 0;

    lines.forEach((line, index) => {
      // Check for console.log statements
      if (line.includes('console.log') && !line.trim().startsWith('//')) {
        consoleCount++;
      }

      // Check for short intervals
      const intervalMatch = line.match(/setInterval\([^,]+,\s*(\d+)\)/);
      if (intervalMatch) {
        intervalCount++;
        const intervalTime = parseInt(intervalMatch[1]);
        if (intervalTime < THRESHOLDS.MIN_INTERVAL_MS) {
          issues.push(`⚠️  ${filePath}:${index + 1} - Short interval: ${intervalTime}ms (minimum: ${THRESHOLDS.MIN_INTERVAL_MS}ms)`);
        }
      }
    });

    if (consoleCount > THRESHOLDS.MAX_CONSOLE_LOGS) {
      issues.push(`⚠️  ${filePath} - Too many console.log statements: ${consoleCount} (max: ${THRESHOLDS.MAX_CONSOLE_LOGS})`);
    }

    if (intervalCount > THRESHOLDS.MAX_SETINTERVALS) {
      issues.push(`⚠️  ${filePath} - Too many setInterval calls: ${intervalCount} (max: ${THRESHOLDS.MAX_SETINTERVALS})`);
    }
  }

  scanDirectory(srcDir);

  if (issues.length === 0) {
    console.log('✅ No performance issues detected!');
  } else {
    console.log('🚨 Performance issues found:');
    issues.forEach(issue => console.log(issue));
    process.exit(1);
  }
}

checkPerformance();