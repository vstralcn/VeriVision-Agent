# API Documentation

Complete API reference for the Deepfake Detection Platform.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Response Format

All responses follow this structure:

### Success Response
```json
{
  "data": { ... },
  "message": "Success"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

---

## Authentication Endpoints

### Register User

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "nickname": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-30T10:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Email already registered
- `422 Unprocessable Entity` - Invalid input

---

### Login

**POST** `/auth/login`

Login and receive JWT access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account disabled

---

### Get Current User

**GET** `/auth/me`

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-30T10:00:00Z"
}
```

---

## Detection Endpoints

### Upload and Detect Image

**POST** `/detection/upload`

Upload an image and perform deepfake detection.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <image_file>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "image_path": "uploads/images/abc123.jpg",
  "heatmap_path": "uploads/heatmaps/heatmap_xyz789.jpg",
  "is_fake": true,
  "confidence": 0.85,
  "fake_probability": 0.92,
  "analysis_report": {
    "verdict": "Fake",
    "fake_probability": 0.92,
    "confidence": 0.85,
    "risk_level": "High",
    "analysis": {
      "face_manipulation": 0.88,
      "texture_inconsistency": 0.75,
      "lighting_artifacts": 0.65,
      "compression_anomalies": 0.55
    },
    "summary": "This image shows signs of manipulation...",
    "recommendations": [
      "Verify the source of this image",
      "Cross-reference with original sources"
    ]
  },
  "cert_id": "CERT-20240130100000-ABC12345",
  "cert_signature": "a1b2c3d4e5f6...",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "phash": "8f373c8c8f3f3c3c",
  "created_at": "2024-01-30T10:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Invalid file type
- `413 Payload Too Large` - File exceeds size limit
- `500 Internal Server Error` - Detection failed

---

### Get Detection History

**GET** `/detection/history`

Get user's detection history with pagination.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 20)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "image_path": "uploads/images/abc123.jpg",
    "heatmap_path": "uploads/heatmaps/heatmap_xyz789.jpg",
    "is_fake": true,
    "confidence": 0.85,
    "fake_probability": 0.92,
    "analysis_report": { ... },
    "cert_id": "CERT-20240130100000-ABC12345",
    "cert_signature": "a1b2c3d4e5f6...",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "phash": "8f373c8c8f3f3c3c",
    "created_at": "2024-01-30T10:00:00Z"
  }
]
```

---

### Get Recent Detections

**GET** `/detection/recent`

Get recent detections for dashboard display.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (integer, optional): Maximum records to return (default: 5)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "image_path": "uploads/images/abc123.jpg",
    "is_fake": true,
    "confidence": 0.85,
    "cert_id": "CERT-20240130100000-ABC12345",
    "created_at": "2024-01-30T10:00:00Z"
  }
]
```

---

### Get Detection Details

**GET** `/detection/{detection_id}`

Get detailed information about a specific detection.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `detection_id` (integer): Detection ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "image_path": "uploads/images/abc123.jpg",
  "heatmap_path": "uploads/heatmaps/heatmap_xyz789.jpg",
  "is_fake": true,
  "confidence": 0.85,
  "fake_probability": 0.92,
  "analysis_report": { ... },
  "cert_id": "CERT-20240130100000-ABC12345",
  "cert_signature": "a1b2c3d4e5f6...",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "phash": "8f373c8c8f3f3c3c",
  "created_at": "2024-01-30T10:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Detection not found
- `403 Forbidden` - Not authorized to access this detection

---

### Get Trace Records

**GET** `/detection/{detection_id}/trace`

Get traceability records for a detection.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `detection_id` (integer): Detection ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "detection_id": 1,
    "action": "uploaded",
    "description": "Image uploaded for detection",
    "metadata": {
      "timestamp": "2024-01-30T10:00:00Z"
    },
    "created_at": "2024-01-30T10:00:00Z"
  },
  {
    "id": 2,
    "detection_id": 1,
    "action": "detected",
    "description": "Detection completed: Fake",
    "metadata": {
      "timestamp": "2024-01-30T10:00:05Z"
    },
    "created_at": "2024-01-30T10:00:05Z"
  }
]
```

---

### Verify Certification

**POST** `/detection/{detection_id}/verify`

Verify the cryptographic signature of a detection certification.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `detection_id` (integer): Detection ID

**Response:** `200 OK`
```json
{
  "cert_id": "CERT-20240130100000-ABC12345",
  "is_valid": true,
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

---

### Get Image

**GET** `/detection/image/{filename}`

Retrieve an uploaded image file.

**Path Parameters:**
- `filename` (string): Image filename

**Response:** `200 OK`
- Content-Type: image/jpeg, image/png, etc.
- Binary image data

**Errors:**
- `404 Not Found` - Image not found

---

### Get Heatmap

**GET** `/detection/heatmap/{filename}`

Retrieve a generated heatmap image.

**Path Parameters:**
- `filename` (string): Heatmap filename

**Response:** `200 OK`
- Content-Type: image/jpeg
- Binary image data

**Errors:**
- `404 Not Found` - Heatmap not found

---

## User Endpoints

### Get User Profile

**GET** `/user/me`

Get current user's profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-30T10:00:00Z"
}
```

---

### Update User Profile

**PUT** `/user/me`

Update current user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "nickname": "Jane Doe"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "Jane Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-30T10:00:00Z"
}
```

---

## Admin Endpoints

**Note:** All admin endpoints require `role=admin`

### Get Dashboard Statistics

**GET** `/admin/dashboard/stats`

Get admin dashboard statistics.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:** `200 OK`
```json
{
  "today_detection_count": 150,
  "today_fake_count": 45,
  "today_fake_ratio": 0.3,
  "total_users": 1250,
  "total_detections": 15000
}
```

**Errors:**
- `403 Forbidden` - Not enough permissions

---

### Get All Users

**GET** `/admin/users`

Get list of all users with pagination.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 50)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "nickname": "John Doe",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-30T10:00:00Z",
    "detection_count": 25
  }
]
```

---

### Toggle User Active Status

**PUT** `/admin/users/{user_id}/toggle-active`

Enable or disable a user account.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `user_id` (integer): User ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "John Doe",
  "role": "user",
  "is_active": false,
  "created_at": "2024-01-30T10:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Cannot disable your own account
- `404 Not Found` - User not found

---

### Get Audit Logs

**GET** `/admin/audit-logs`

Get audit logs with filtering options.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip
- `limit` (integer, optional): Maximum records to return
- `action` (string, optional): Filter by action type
- `user_id` (integer, optional): Filter by user ID
- `success` (boolean, optional): Filter by success status
- `start_date` (datetime, optional): Filter by start date
- `end_date` (datetime, optional): Filter by end date

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "action": "login",
    "resource": null,
    "success": true,
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "detail": {
      "email": "user@example.com"
    },
    "created_at": "2024-01-30T10:00:00Z"
  }
]
```

---

### Get Audit Log Detail

**GET** `/admin/audit-logs/{log_id}`

Get detailed information about a specific audit log entry.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `log_id` (integer): Audit log ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "action": "detection",
  "resource": "detection:123",
  "success": true,
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "detail": {
    "detection_id": 123,
    "is_fake": true,
    "confidence": 0.85
  },
  "created_at": "2024-01-30T10:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Audit log not found

---

## Health Check Endpoints

### Root Endpoint

**GET** `/`

Get API information.

**Response:** `200 OK`
```json
{
  "message": "Deepfake Detection Platform API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### Health Check

**GET** `/health`

Check API health status.

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 413 | Payload Too Large - File size exceeds limit |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **Detection endpoints**: 10 requests per minute
- **Other endpoints**: 60 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1706616000
```

---

## Examples

### cURL Examples

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user123"}'
```

#### Upload Image
```bash
curl -X POST http://localhost:8000/api/detection/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

#### Get Detection History
```bash
curl -X GET "http://localhost:8000/api/detection/history?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Python Examples

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "user@example.com", "password": "user123"}
)
token = response.json()["access_token"]

# Upload image
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/detection/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f}
    )
detection = response.json()

print(f"Detection result: {detection['is_fake']}")
print(f"Confidence: {detection['confidence']}")
```

### JavaScript Examples

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'user123'
  })
});
const { access_token } = await loginResponse.json();

// Upload image
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/detection/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
});
const detection = await uploadResponse.json();

console.log('Detection result:', detection.is_fake);
console.log('Confidence:', detection.confidence);
```

---

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can:
- Test all endpoints directly
- View request/response schemas
- Authenticate and try API calls
- Download OpenAPI specification

---

**For more information, see the [README.md](../README.md)**
