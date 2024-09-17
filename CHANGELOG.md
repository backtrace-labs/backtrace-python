# Version 0.4.0

- Changed a submission flow - from spawning and sending data from a process to background thread(#19).
- Added support for submit.backtrace.io(#14).
- Added new default attributes:
  - backtrace.agent, backtrace.version (#13)
  - application.session (#13),
  - uname.sysname, uname.version, uname.release (#13),
  - error.type (#13),
  - linux process and system memory information (#15),
  - guid (#15),
  - cpu attributes (#15),
  - process.age (#15),
- Added a support for attachments (#19),
- Added a new client initialization attributes:
  - attributes - client specific attributes that will be included every time the report is being generated (#19),
  - attachments - list of attachments paths (#19),
  - collect_source_code - disable collecting source code information for each stack trace (#20),
  - ignore_ssl_certificate ($19)
