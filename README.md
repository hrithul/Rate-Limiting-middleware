# Documentation

## How the Rolling Window Rate Limiting is Implemented
  1. For each request, the middleware identifies the client's IP address.
  2. It retrieves a list of timestamps (stored in Django's cache) representing the times of previous requests from that IP.
  3. It removes timestamps older than the window (e.g., 5 minutes ago).
  4. If the number of valid timestamps exceeds the allowed limit (`RATE_LIMIT`), it blocks the request with a 429 error ("Too Many Requests") and sets the `X-RateLimit-Remaining` header to 0.
  5. Otherwise, it appends the current timestamp, saves the updated list back to the cache, and allows the request, also setting the `X-RateLimit-Remaining` header.
- **Rolling Window:** The window is always the last N seconds from the current request, not a fixed interval, so it's precise and fair.

### How to Test
1. **Start the Django server:**
   ```sh
   venv\Scripts\python manage.py runserver
   ```
2. **Send requests using Postman or curl:**
   - URL: `http://127.0.0.1:8000/`
   - Method: GET
   - Observe the `X-RateLimit-Remaining` header in the response.
   - After 5 requests within 5 minutes, you’ll receive a 429 error.
   - Use the `X-Forwarded-For` header to simulate different IPs.
3. **Example curl command:**
   ```sh
   curl -i http://127.0.0.1:8000/
   curl -i -H "X-Forwarded-For: 1.2.3.4" http://127.0.0.1:8000/
   ```

## Example Input/Output
**Scenario:** 5 allowed requests per 5 minutes.

- **Request 1-5:**
  - Status: 200 OK
  - Header: `X-RateLimit-Remaining: 4`, ..., `X-RateLimit-Remaining: 0`
- **Request 6 onwards:**
  - Status: 429 Too Many Requests
  - Body: `{ "detail": "Too Many Requests" }`
  - Header: `X-RateLimit-Remaining: 0`

**Example Debug Output (add print statements to middleware for debugging):**
```
[18/May/2025 22:33:05] "GET / HTTP/1.1" 200 9
[18/May/2025 22:33:08] "GET / HTTP/1.1" 200 9
[18/May/2025 22:33:09] "GET / HTTP/1.1" 200 9
[18/May/2025 22:33:10] "GET / HTTP/1.1" 200 9
[18/May/2025 22:33:11] "GET / HTTP/1.1" 200 9
Too Many Requests: /
[18/May/2025 22:33:11] "GET / HTTP/1.1" 429 31
```
