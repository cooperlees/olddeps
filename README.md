# olddeps
Take a requirements file and check against PyPI

## Sample Output
```
cooper-mbp1:olddeps cooper$ /tmp/tod/bin/od --debug sample-reqs.txt
[2019-05-07 15:57:10,629] DEBUG: Using selector: KqueueSelector (selector_events.py:53)
[2019-05-07 15:57:10,630] INFO: Parsing sample-reqs.txt (od.py:60)
[2019-05-07 15:57:10,631] DEBUG: Opening sample-reqs.txt to parse with requirements (od.py:33)
Packages from sample-reqs.txt
 - chardet: 698
 - async-timeout: 210
 - filelock: 186
 - aiohttp: 115
 - attrs: 65
 - certifi: 59
 ```
