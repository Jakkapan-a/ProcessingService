# ProcessingService

Service สำหรับประมวลผลภาพด้วย AI/ML models พร้อมระบบจัดการไฟล์และ API

## ข้อกำหนดระบบ

- Docker และ Docker Compose
- Python 3.9+
- PostgreSQL 17

## การติดตั้งและใช้งาน

### 1. เตรียมไฟล์ Environment

สร้างไฟล์ `.env` จากไฟล์ตัวอย่าง:

```bash
cp .env.example .env
```

แก้ไขค่าต่างๆ ในไฟล์ `.env`:

```env
POSTGRES_PASSWORD=your_secure_password
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_admin_password
```

### 2. เริ่มต้นระบบด้วย Docker Compose

สร้างและเริ่มต้น containers:

```bash
docker compose up --build -d
```

สิ่งที่จะเกิดขึ้น:
- **API Service**: จะทำงานที่ `http://localhost:10011`
- **PostgreSQL Database**: จะเปิดที่ port `6438`
- **pgAdmin4**: จะเปิดที่ `http://localhost:8090`

### 3. ตรวจสอบสถานะ containers

```bash
docker compose ps
```

### 4. หยุดระบบ

```bash
docker compose down
```

## Database Migration

### การสร้าง Migration ครั้งแรก

1. เข้าไปใน container ของ API:

```bash
docker exec -it processing_image_service bash
```

2. สร้าง migration directory (ทำครั้งแรกเท่านั้น):

```bash
flask db init
```

3. สร้าง migration file จาก models:

```bash
flask db migrate -m "Initial migration"
```

4. Apply migration ไปยังฐานข้อมูล:

```bash
flask db upgrade
```

### การ Migrate เมื่อมีการเปลี่ยนแปลง Models

เมื่อมีการแก้ไข models ใน `app/models/`:

1. เข้าไปใน container:

```bash
docker exec -it processing_image_service bash
```

2. สร้าง migration file ใหม่:

```bash
flask db migrate -m "Description of changes"
```

3. Apply การเปลี่ยนแปลง:

```bash
flask db upgrade
```

### คำสั่ง Migration อื่นๆ

```bash
# ดู migration history
flask db history

# ดูสถานะปัจจุบัน
flask db current

# Rollback migration
flask db downgrade

# ดู SQL ที่จะถูก execute
flask db show <revision>
```

## การเข้าถึงบริการ

| บริการ | URL | รายละเอียด |
|--------|-----|-----------|
| API Service | http://localhost:10011 | Main API endpoint |
| pgAdmin4 | http://localhost:8090 | Database management |
| PostgreSQL | localhost:6438 | Database connection |

### การเชื่อมต่อฐานข้อมูลผ่าน pgAdmin4

1. เปิด http://localhost:8090
2. Login ด้วย email และ password ที่กำหนดใน `.env`
3. เพิ่ม server connection:
   - **Host**: `processing_image_db` (ชื่อ container)
   - **Port**: `5432`
   - **Database**: `postgres`
   - **Username**: `postgres`
   - **Password**: ตามที่กำหนดใน `.env`

## โครงสร้างโปรเจกต์

```
ProcessingService/
├── app/                    # โค้ดหลักของ application
│   ├── models/            # Database models
│   ├── routes/            # API routes
│   ├── services/          # Business logic
│   ├── config.py          # Configuration
│   └── __init__.py        # App factory
├── models/                # AI/ML model files
├── public/temp/           # Temporary files
├── data/                  # PostgreSQL data
├── logs/                  # Application logs
├── tests/                 # Unit tests
├── docker-compose.yaml    # Docker compose configuration
├── Dockerfile             # Docker image configuration
├── requirements.txt       # Python dependencies
└── server.py              # Application entry point
```

## การพัฒนา (Development)

### การรัน tests

```bash
# เข้าไปใน container
docker exec -it processing_image_service bash

# รัน tests
python -m pytest tests/
```

### การดู logs

```bash
# ดู logs ของ API service
docker compose logs processing_image_service

# ดู logs แบบ real-time
docker compose logs -f processing_image_service

# ดู logs ของ database
docker compose logs processing_image_db
```

### การ debug

1. ตั้งค่า `DEBUG=true` ในไฟล์ `.env`
2. Restart containers:

```bash
docker compose down
docker compose up --build
```

## การ Backup และ Restore Database

### Backup

```bash
docker exec processing_image_db pg_dump -U postgres postgres > backup.sql
```

### Restore

```bash
docker exec -i processing_image_db psql -U postgres postgres < backup.sql
```

## Troubleshooting

### ปัญหาที่พบบ่อย

1. **Container ไม่เริ่มต้น**: ตรวจสอบไฟล์ `.env` และ logs
2. **Database connection error**: ตรวจสอบว่า database container ทำงานแล้ว
3. **Migration error**: ตรวจสอบ database connection และ models

### การแก้ไขปัญหา

```bash
# ลบ containers และ volumes ทั้งหมด (ระวัง: จะลบข้อมูลทั้งหมด)
docker compose down -v

# ลบ images และสร้างใหม่
docker compose down --rmi all
docker compose up --build
```

## การติดต่อ

หากมีปัญหาหรือข้อสงสัย กรุณาติดต่อทีมพัฒนา