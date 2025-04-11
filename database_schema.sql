```sql
-- مخطط قاعدة بيانات CRM

-- جدول المستخدمين
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL, -- admin, manager, user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- جدول الصلاحيات
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- جدول العلاقة بين المستخدمين والصلاحيات
CREATE TABLE user_permissions (
    user_id INTEGER,
    permission_id INTEGER,
    PRIMARY KEY (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- جدول المناطق
CREATE TABLE regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- جدول المدن
CREATE TABLE cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    region_id INTEGER,
    FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE,
    UNIQUE (name, region_id)
);

-- جدول الأحياء
CREATE TABLE districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    city_id INTEGER,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    UNIQUE (name, city_id)
);

-- جدول أنواع المنشآت
CREATE TABLE establishment_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- جدول المنشآت
CREATE TABLE establishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unified_number BIGINT UNIQUE,
    name VARCHAR(200) NOT NULL,
    mobile VARCHAR(20),
    email VARCHAR(100),
    region_id INTEGER,
    city_id INTEGER,
    district_id INTEGER,
    establishment_type_id INTEGER,
    brokerage_license VARCHAR(50),
    property_management_license VARCHAR(50),
    facility_management_license VARCHAR(50),
    auction_license VARCHAR(50),
    real_estate_cooperation VARCHAR(100),
    whatsapp VARCHAR(20),
    campaign_type VARCHAR(100),
    action_taken TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (region_id) REFERENCES regions(id),
    FOREIGN KEY (city_id) REFERENCES cities(id),
    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (establishment_type_id) REFERENCES establishment_types(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- جدول مشاريع إدخال المنشآت
CREATE TABLE data_entry_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity VARCHAR(100) NOT NULL,
    region_id INTEGER,
    city_id INTEGER,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL, -- منتهي، جاري، لم يبدأ
    marketing_status VARCHAR(50), -- جاهز، غير جاهز
    responsible VARCHAR(100),
    current_count INTEGER DEFAULT 0,
    nizar_entry_count INTEGER DEFAULT 0,
    asmaa_entry_count INTEGER DEFAULT 0,
    total_entry_count INTEGER DEFAULT 0,
    difference INTEGER DEFAULT 0,
    asmaa_entitlement INTEGER DEFAULT 0,
    non_entered_value DECIMAL(10, 2) DEFAULT 0,
    pricing INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES regions(id),
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- جدول الإحصائيات
CREATE TABLE statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER,
    count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES regions(id)
);

-- جدول سجل النشاطات
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- جدول الإعدادات
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
