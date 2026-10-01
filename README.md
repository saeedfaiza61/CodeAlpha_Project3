# CodeAlpha_Project3
 identifying security vulnerabilities.

# Language: Python 3, Flask
# Application:  a small web app with login, a welcome page, a network ping utility, a file viewer, a session loader, and an admin panel.

●	Manual code review: line-by-line inspection of each route, focusing on how user-controlled input (form fields, query parameters, request body) flows into sensitive operations, database queries, HTML output, shell commands, file paths, deserialization, and session/auth checks.
●	Dynamic testing: manually exploited two findings against the running application to confirm they are real, not just theoretical (SQL injection login bypass, reflected XSS).
●	Static analysis: Bandit, a Python-specific static analyzer, run against app.py to flag known-bad patterns (hardcoded secrets, weak hashing, shell=True, pickle.loads, etc.) automatically.


#	Vulnerability                     	CWE	            Severity                           	Location	             Status
1	SQL Injection (auth bypass)       	CWE-89	         Critical                         	/login	Verified        exploited
2	Reflected XSS	                     CWE-79	         High	                             /welcome	Verified      exploited
3	OS Command Injection              	CWE-78	         Critical	                         /ping	                Identified
4	Path Traversal	                    CWE-22	         High	                             /file	                Identified
5	Insecure Deserialization	         CWE-502	         Critical	                        /load_session          Identified
6	Broken Access Control	            CWE-863	         High	                            /admin                Identified
7	Hardcoded Secret Key             	CWE-79	          High                            	app.secret_key	       Identified
8	Weak Password Hashing (MD5)	      CWE-916	        High	                            login, init_db	        Identified
9	Debug Mode Enabled	               CWE-215	        Medium	                          app.run(...)	          Identified

# Finding 1:
SQL Injection  
Evidence: Submitting username admin' -- with any password logs in as admin without a valid password.
Root cause: Query built via Python string formatting (%) instead of parameterization.
Fix:
cur = conn.execute(     "SELECT id, is_admin FROM users WHERE username = ? AND password = ?",     (username, pw_hash) )


# Finding 2 : 
Reflected XSS  
Evidence: ?name=<b>test</b> rendered as bold text instead of literal text.
Root cause: User input concatenated into an HTML string and rendered with render_template_string.
Fix: Use render_template with autoescaping, or explicitly escape with markupsafe.escape(name).

# Finding 3 :
OS Command Injection  
Root cause: /ping passes the raw host parameter to os.popen.
Fix:
subprocess.run(["ping", "-c", "1", host], shell=False) # plus strict validation that host is a well-formed hostname/IP
# Finding 4:
Path Traversal 
Root cause: /file joins user input into a path without checking for .. sequences.
Fix: Resolve the final path with os.path.realpath() and verify it is still inside the intended directory before opening.
# Finding 5:
Insecure Deserialization  
Root cause: /load_session calls pickle.loads() on raw request data.
Fix: Replace with json.loads(); never unpickle untrusted input.
# Finding 6 :
Broken Access Control  
Root cause: /admin trusts a client-session flag with no server-side re-verification against the database.
Fix: Re-check the user's role/permissions server-side on each sensitive request (e.g. query the DB by user_id); don't rely solely on session state.
# Finding 7 :
Hardcoded Secret Key  
Root cause: app.secret_key is a fixed string in source code.
Fix: Load from an environment variable; generate with secrets.token_hex(32).
# Finding 8 
Weak Password Hashing 
Root cause: Passwords hashed with unsalted MD5, which is fast to brute-force.
Fix: Replace with bcrypt or werkzeug.security.generate_password_hash.
# Finding 9:
Debug Mode Enabled  
Root cause: app.run(debug=True, host="0.0.0.0") exposes the interactive debugger and binds beyond localhost.
Fix: Set debug=False in production; use a proper WSGI server (gunicorn/uwsgi) instead of Flask's built-in dev server.
# Recommendations :
●	Validate and sanitize all external input at the point it enters the application.
●	Use parameterized queries or an ORM everywhere — never build SQL via string concatenation.
●	Auto-escape all output rendered into HTML.
●	Avoid shelling out to the OS; when unavoidable, never use shell=True or string concatenation.
●	Never deserialize untrusted data with pickle; prefer JSON.
●	Re-verify authorization server-side on every privileged action.
●	Keep secrets out of source code; use environment variables or a secrets manager.
●	Run static analysis (Bandit) and dependency scanning (pip-audit) as part of CI.
●	Disable debug mode and framework banners before deployment.
