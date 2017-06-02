Skurt Back-End Programming Challenge - Faizan Haque

A python 3 script to launch a service that polls the interview API, and if required, emails Skurt engineering with the IDs of vehicles outside their geofences.

Dependencies

	-python 3
	-Requests

Usage

	python3 challenge.py

	flags
	-m --mode [test]

Running in test mode sets the polling interval to 15s, and only polls car 11, which should always be located out of bounds and therefor trigger a warning.

To run as a daemon, use as follows:

	nohup python3 challenge.py &

Note that this will decouple the script from the terminal session that invoked it, and also run it in the background. To stop execution, kill the PID (should be returned upon execution). This usage emulates what a service like this would be used for.

To run tests:

	python3 tests.py

Design Decisions/Limitations

Polling period
This program polls all cars every 240s (4m). This ensures that an email warning can be sent out within 5 minutes, even with some SMTP latency. Note that an email will continue to be sent every 4 minutes while any cars are out of bounds. The decision was made not to add more complex behaviour (eg. exponentially increasing email intervals) without understanding the context of this time requirement (urgency, escalation, etc.) first. In addition, only one email is sent out per polling period, as opposed to one email per car ID. This decision was made on the assumption that under the worst case, 10 emails (one per car) every 4 minutes (the polling period) would be distracting without offering any distinct advantages.

Email config
A testing gmail account has been setup for this challenge, it will actually send out emails to engineering@skurt.com! Credentials for this account are located in emailconfig.py. Plain text credentials are never great, but this serves our purposes here. A more robust solution can be built for production. Since this is a long running service, entering credentials on execution of the script might be a reasonable tradeoff between ease of use and security

Logging
In addition to email warnings, everything is logged to challenge.log. This ensures that even if emails are not being sent for some reason, the issue can be diagnosed and resolved.

Testing
Test coverage right now focusses on the is_in_bounds fn, as that contains the most complexity. For this challenge the decision was made not to extend coverage to sections of code that handle the HTTP response, but that is something that should definitely be done for production. A module like requests_mock would be helpful in setting up a mock server/response.

Daemonizing
This service emulates a daemon currently, but is not robust enough for long term use. for instance, unexpected terminations will be silent. The log or PID must be checked periodically to ensure the service is still running. This decision was made under the assumption that under production constraints, several tools and methods exist to handle unexpected termination, and those may be used as needed.