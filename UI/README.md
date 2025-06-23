# CRISP


dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP$ source venv/bin/activate      
(venv) dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP$ python manage.py runserver 8001
python: can't open file 'manage.py': [Errno 2] No such file or directory
(venv) dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP$ cd /mnt/c/Users/Client/Documents/GitHub/CRISP
(venv) dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP$ python manage.py runserver 8001
python: can't open file 'manage.py': [Errno 2] No such file or directory
(venv) dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP$ cd crisp_backend
(venv) dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP/crisp_backend$ python manage.py runserver 8001



UI Login: 
    N/A - removed
    {-Username = ADMIN
    -password = Admin123}

Django 
[
RUN:  python manage.py runserver 8001


    ##Admin
    -Username = TEST1
    -password = KAKPRAAT123
    -email = test1@gmail.com

    -Username = adminUser1
    -password = ThisIsATest123

    ##User
    - username = regularUser1
    - Something123

    
]
postgre pssql
    -user = crisp_user
    -psswd = CrispAdmin@#$


TESTING

dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP/crisp-react$ npm test

> crisp-react@0.0.0 test
> jest

  console.log
    Setup tests initialized

      at Object.log (src/setupTests.js:2:9)

 PASS  src/api.test.js (16.067 s)
  API Service Tests
    loginUser
      ✓ should login successfully and store auth data (11 ms)                                      
      ✓ should handle login failure with detail message (1 ms)                                     
      ✓ should handle login failure with non_field_errors                                          
      ✓ should handle login failure with generic error                                             
      ✓ should not store auth data if no token returned (1 ms)                                     
    registerUser                                                                                   
      ✓ should register successfully and store auth data (1 ms)                                    
      ✓ should handle registration failure                                                         
      ✓ should not store auth data if no token returned (1 ms)                                     
    getCurrentUser                                                                                 
      ✓ should return current user when auth data exists                                           
      ✓ should return null when no auth data exists                                                
      ✓ should return null when auth data exists but no user                                       
      ✓ should handle invalid JSON in localStorage (80 ms)                                         
    logoutUser                                                                                     
      ✓ should remove auth data from localStorage                                                  
    authHeader                                                                                     
      ✓ should return authorization header when token exists (1 ms)                                
      ✓ should return empty object when no auth data exists                                        
      ✓ should return empty object when auth data exists but no token (1 ms)                       
      ✓ should handle invalid JSON in localStorage                                                 
    refreshToken                                                                                   
      ✓ should refresh token successfully and update localStorage                                  
      ✓ should reject when no auth data exists                                                     
      ✓ should reject when no refresh token exists
      ✓ should handle refresh token failure (1 ms)
      ✓ should not update localStorage if no access token returned (1 ms)
    Error Handling Edge Cases
      ✓ should handle network errors
      ✓ should handle JSON parsing errors in API responses

Test Suites: 1 passed, 1 total
Tests:       24 passed, 24 total
Snapshots:   0 total
Time:        51.789 s
Ran all test suites.
dreas@DESKTOP-V5A0C20:/mnt/c/Users/Client/Documents/GitHub/CRISP/crisp-react$