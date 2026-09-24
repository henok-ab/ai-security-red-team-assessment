## Finding 1 — Invalid File Causes Unhandled Exception

### Test

Uploaded a plain text file to:

POST /predict

### Result

The API returned:

HTTP 500 Internal Server Error

The server log showed:

PIL.UnidentifiedImageError:
cannot identify image file

### Root Cause

The application passes uploaded bytes directly to:

Image.open(...)

without explicit validation or exception handling.

### Security Impact

Malformed or unsupported uploads can trigger application
exceptions and produce server errors.

Depending on deployment configuration, detailed exception
information could potentially be exposed.

### Evidence

- Invalid file: test.txt
- Endpoint: POST /predict
- HTTP response: 500 Internal Server Error
- Exception: PIL.UnidentifiedImageError

### Recommended Remediation

- Validate uploaded file type.
- Validate image dimensions and size.
- Catch image parsing exceptions.
- Return a controlled 4xx response for invalid input.
- Ensure production error responses do not expose stack traces.