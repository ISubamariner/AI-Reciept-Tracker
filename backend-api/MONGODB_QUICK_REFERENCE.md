# MongoDB Receipt Storage - Quick Reference

## Quick Start

### 1. Start Services

```bash
cd portfolio-ai-app
docker-compose up -d
```

### 2. Verify MongoDB is Running

```bash
# Check status
docker-compose ps mongodb

# Check health
curl http://localhost:5000/api/health
```

### 3. Test Receipt Upload

Upload a receipt - it will automatically save to both PostgreSQL and MongoDB:

```bash
curl -X POST http://localhost:5000/api/receipts/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@receipt.jpg"
```

## Common Operations

### Get User's Receipts

```bash
curl http://localhost:5000/api/receipts/mongo/user/45 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Archive a Receipt

```bash
curl -X POST http://localhost:5000/api/receipts/mongo/archive/123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "old_data"}'
```

### Unarchive a Receipt

```bash
curl -X POST http://localhost:5000/api/receipts/mongo/unarchive/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Statistics

```bash
curl http://localhost:5000/api/receipts/mongo/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Receipts

```bash
curl "http://localhost:5000/api/receipts/mongo/search?q=target" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## MongoDB Shell Commands

### Connect to MongoDB

```bash
docker exec -it pythonmoneytracker-mongodb mongosh -u mongouser -p Admin@1234 --authenticationDatabase admin
```

### Useful Queries

```javascript
// Switch to receipts database
use receipts

// Count all receipts
db.receipts.countDocuments()

// Count archived receipts
db.receipts.countDocuments({ archived: true })

// Find user's receipts
db.receipts.find({ uploader_id: 45 }).pretty()

// Find pending receipts
db.receipts.find({ status: "PENDING" }).pretty()

// Find receipts by vendor
db.receipts.find({ "metadata.vendor_name": /target/i }).pretty()

// Get latest 10 receipts
db.receipts.find().sort({ created_at: -1 }).limit(10).pretty()

// Archive old receipts (older than 90 days)
const ninetyDaysAgo = new Date(Date.now() - 90*24*60*60*1000);
db.receipts.updateMany(
  { created_at: { $lt: ninetyDaysAgo }, archived: false },
  { $set: { archived: true, archive_date: new Date(), archive_reason: "auto_archived" } }
)

// Storage stats
db.receipts.stats()
```

## Archiving Workflows

### Manual Archive (User)

```bash
curl -X POST http://localhost:5000/api/receipts/mongo/archive/123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "user_requested"}'
```

### Bulk Archive (Admin Only)

```bash
curl -X POST http://localhost:5000/api/receipts/mongo/bulk-archive \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days_old": 90}'
```

### View Archived Receipts

```bash
# All archived receipts
curl http://localhost:5000/api/receipts/mongo/archived \
  -H "Authorization: Bearer YOUR_TOKEN"

# Archived more than 30 days ago
curl "http://localhost:5000/api/receipts/mongo/archived?days_old=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Backup & Restore

### Backup MongoDB

```bash
# Create backup
docker exec pythonmoneytracker-mongodb mongodump \
  --username mongouser \
  --password Admin@1234 \
  --authenticationDatabase admin \
  --db receipts \
  --out /backup

# Copy to host
docker cp pythonmoneytracker-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d)
```

### Restore MongoDB

```bash
# Copy backup to container
docker cp ./mongodb-backup pythonmoneytracker-mongodb:/backup

# Restore
docker exec pythonmoneytracker-mongodb mongorestore \
  --username mongouser \
  --password Admin@1234 \
  --authenticationDatabase admin \
  --db receipts \
  /backup/receipts
```

## Troubleshooting

### Check MongoDB Logs

```bash
docker-compose logs -f mongodb
```

### Check Backend Logs

```bash
docker-compose logs -f backend
```

### Restart MongoDB

```bash
docker-compose restart mongodb
```

### Test MongoDB Connection

```bash
docker exec pythonmoneytracker-mongodb mongosh \
  --eval "db.adminCommand('ping')" \
  -u mongouser \
  -p Admin@1234 \
  --authenticationDatabase admin
```

## Environment Variables

Add to `.env` file:

```env
MONGODB_URL=mongodb://mongouser:Admin@1234@mongodb:27017/receipts?authSource=admin
```

## API Endpoints Summary

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/receipts/mongo/<receipt_id>` | Get single receipt | Logger, User, Admin |
| GET | `/api/receipts/mongo/user/<user_id>` | Get user's receipts | Logger, User, Admin |
| POST | `/api/receipts/mongo/archive/<receipt_id>` | Archive receipt | Logger, Admin |
| POST | `/api/receipts/mongo/unarchive/<receipt_id>` | Unarchive receipt | Logger, Admin |
| GET | `/api/receipts/mongo/archived` | Get archived receipts | Logger, Admin |
| GET | `/api/receipts/mongo/stats` | Get statistics | Logger, User, Admin |
| GET | `/api/receipts/mongo/search` | Search receipts | Logger, User, Admin |
| POST | `/api/receipts/mongo/bulk-archive` | Bulk archive old receipts | Admin only |

## Document Structure

```javascript
{
  receipt_id: Number,          // PostgreSQL reference
  uploader_id: Number,         // User ID
  image_url: String,           // Image location
  status: String,              // PENDING, PROCESSED, ERROR
  raw_ai_data: Object,         // AI extraction output
  metadata: {                  // Structured data
    vendor_name: String,
    total_amount: Number,
    currency: String,
    transaction_date: Date,
    receipt_number: String
  },
  archived: Boolean,           // Archive flag
  archive_date: Date,          // When archived
  archive_reason: String,      // Why archived
  created_at: Date,
  updated_at: Date,
  tags: [String],              // Custom tags
  file_size: Number,           // Size in bytes
  mime_type: String            // Image format
}
```

## Best Practices

1. ✅ Always include `archived: false` filter for active receipts
2. ✅ Use pagination with `limit` and `skip` for large datasets
3. ✅ Archive receipts older than 90 days regularly
4. ✅ Backup MongoDB weekly
5. ✅ Monitor storage usage via stats endpoint
6. ✅ Use meaningful archive reasons
7. ✅ Test restore process periodically

## Performance Tips

- Default queries exclude archived receipts
- Use indexed fields (receipt_id, uploader_id, status, created_at)
- Limit result sets to reasonable sizes
- Archive old data regularly
- Monitor database size with `db.stats()`
