# Async Image processor

    An Asyncronous web app to process images from a csv

# API Documentation

## Base URL

`https://api.example.com/`

## Endpoints

### 1. Upload CSV

- **URL**: `/api/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### Request Parameters

| Parameter    | Type   | Required | Description                          |
| ------------ | ------ | -------- | ------------------------------------ |
| file         | File   | Yes      | CSV file to be processed             |
| webhook_urls | String | No       | Comma-separated list of webhook URLs |

#### Response

```json
{
  "requestId": "string"
}
```

#### Status Codes

- 202: Accepted
- 400: Bad Request
- 500: Internal Server Error

### 2. Get Job Status

- **URL**: `/api/status/{request_id}`
- **Method**: `GET`

#### Path Parameters

| Parameter  | Type   | Required | Description                                |
| ---------- | ------ | -------- | ------------------------------------------ |
| request_id | String | Yes      | Unique request ID returned from upload API |

#### Response

```json
{
  "requestId": "string",
  "status": "string",
  "output_url": "string"
}
```

#### Status Codes

- 200: OK
- 404: Not Found
- 500: Internal Server Error

### 3. Add Webhook

- **URL**: `/api/webhook/{request_id}`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

#### Path Parameters

| Parameter  | Type   | Required | Description                   |
| ---------- | ------ | -------- | ----------------------------- |
| request_id | String | Yes      | Unique request ID for the job |

#### Request Parameters

| Parameter   | Type   | Required | Description                          |
| ----------- | ------ | -------- | ------------------------------------ |
| webhook_url | String | Yes      | URL to receive webhook notifications |

#### Response

```json
{
  "message": "Webhook added successfully"
}
```

#### Status Codes

- 200: OK
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

## Webhook Payload

When a job is completed, the following payload will be sent to all registered webhook URLs:

```json
{
  "requestId": "string",
  "status": "string",
  "output_url": "string"
}
```
