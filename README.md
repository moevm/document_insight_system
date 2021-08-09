#### LTI1.3 test implementation:  

test platform: https://lti-ri.imsglobal.org/platforms/2426; 
test tool: https://lti-ri.imsglobal.org/lti/tools/2153

To test launch, go to platform -> resource links -> select user -> oidc login -> etc.

Base implementation would include 3 routes: /lti_login/(tool's initiation url), /launch/(tool link's url), /jwks/(keys).
1.3 requires usage of HTTPS
