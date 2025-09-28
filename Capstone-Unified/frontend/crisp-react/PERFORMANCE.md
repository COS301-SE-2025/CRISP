# Performance Guidelines

## 🚨 Rules to Prevent Slowdowns

### **Polling Intervals**
- ❌ **Never** use intervals shorter than 60 seconds (60000ms)
- ✅ **Minimum**: 5 minutes (300000ms) for background tasks
- ✅ **Recommended**: 10+ minutes for non-critical updates

### **Console Logging**
- ❌ **Avoid** excessive console.log statements (max 50 per file)
- ❌ **Never** log inside loops or frequent functions
- ✅ **Only** use console.warn and console.error in production

### **API Calls**
- ❌ **Don't** make API calls every few seconds
- ✅ **Use** RefreshManager for coordinated updates
- ✅ **Batch** related API calls together

## 🔧 Tools

### Check Performance Issues
```bash
npm run perf:check
```

### Before Committing
```bash
npm run pre-commit
```

## 🎯 Quick Fixes

If the app becomes slow again:

1. **Hard refresh browser**: `Ctrl+Shift+R`
2. **Clear cache**: F12 → Application → Clear storage
3. **Restart dev server**: Stop and `npm run dev`
4. **Check console**: Look for excessive logging
5. **Run performance check**: `npm run perf:check`

## 📊 Performance Targets

- **Console logs per file**: < 50
- **setInterval calls per file**: < 10
- **Minimum interval time**: 60 seconds
- **API call frequency**: Every 5+ minutes
- **Page load time**: < 3 seconds
- **Time to interactive**: < 5 seconds