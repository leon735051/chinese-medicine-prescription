-- 創建資料庫
CREATE DATABASE IF NOT EXISTS chinese_medicine_db;
USE chinese_medicine_db;

-- 客戶資料表 (移除身分證號碼欄位並使用自動遞增ID)
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    birthday DATE,
    gender ENUM('男', '女') NOT NULL DEFAULT '男',
    occupation VARCHAR(50),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    address VARCHAR(100),
    create_date DATE NOT NULL,
    update_date DATE
) ENGINE=InnoDB AUTO_INCREMENT=1;

-- 客戶記錄表
CREATE TABLE IF NOT EXISTS records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    record_date DATETIME,
    times INT,
    price DECIMAL(10, 2),
    description TEXT,
    judgment VARCHAR(100),
    result VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- 處方資料表 (包含 record_id 欄位)
CREATE TABLE IF NOT EXISTS prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    record_id INT NOT NULL,
    prescription_name VARCHAR(50),
    composition TEXT,
    quantity DECIMAL(10, 2),
    unit VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
);

-- 方劑資料表 
CREATE TABLE IF NOT EXISTS formulas (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    origin_text VARCHAR(100),
    composition TEXT,
    effect TEXT,
    indication TEXT,
    application TEXT
);
-- 創建秘方資料表
CREATE TABLE IF NOT EXISTS secret_formulas (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    origin_text VARCHAR(100),
    composition TEXT,
    effect TEXT,
    indication TEXT,
    application TEXT
);
-- 藥材資料表 (單味藥)
CREATE TABLE IF NOT EXISTS medicines (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    origin_text VARCHAR(100),
    nature_flavor TEXT,
    effect TEXT,
    indication TEXT,
    application TEXT,
    unit VARCHAR(20),
    price_per_unit DECIMAL(10, 2)
);

-- 方劑組成表（方劑與藥材的關聯）
CREATE TABLE IF NOT EXISTS formula_compositions (
    formula_id VARCHAR(20),
    medicine_id VARCHAR(20),
    quantity DECIMAL(10, 2),
    PRIMARY KEY (formula_id, medicine_id),
    FOREIGN KEY (formula_id) REFERENCES formulas(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
);

-- 檢查是否已存在 record_id 欄位，如果不存在則新增
SET @sql = (SELECT IF(
    (SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_schema = DATABASE()
        AND table_name = 'prescriptions'
        AND column_name = 'record_id') > 0,
    'SELECT ''record_id column already exists'' as message;',
    'ALTER TABLE prescriptions ADD COLUMN record_id INT NOT NULL AFTER customer_id, ADD FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE;'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 插入客戶範例資料
INSERT IGNORE INTO customers (name, gender, create_date) VALUES
('鄭日陞', '男', CURDATE()),
('林國泰', '男', CURDATE()),
('劉政宏', '男', CURDATE()),
('陳泰嘉', '男', CURDATE()),
('陳俊金華', '男', CURDATE()),
('郭淑萍', '女', CURDATE()),
('張美鳳', '女', CURDATE()),
('陳師華', '男', CURDATE()),
('陳佩芬', '女', CURDATE()),
('莊娜綺', '女', CURDATE()),
('黃永雄', '男', CURDATE()),
('王瑞雲', '女', CURDATE()),
('田村鎮', '男', CURDATE());

-- 插入方劑範例資料
INSERT IGNORE INTO formulas (id, name, origin_text, composition, effect, indication, application) VALUES
('F0001', '二陳湯', '和劑局方', '半夏、生薑、茯苓、甘草、陳皮', '燥濕化痰，理氣和中。', 
 '咳嗽咯痰。痰多色白易咯，胸膈痞悶，惡心嘔吐，肢體困倦。或頭眩心悸。', 
 '本方廣泛用於慢性支氣管炎，慢性肺炎，清處源，神經性咳嗽，神經衰弱，甲狀腺腫，肺氣腫，小兒流涎症等，均效如觀說者。'),
('F0002', '龍膽瀉肝湯', '醫方集解', '龍膽草、梔子、黃芩、柴胡、生地黃、車前子、木通、澤瀉、當歸、甘草', 
 '清肝膽實火，瀉下焦濕熱。', '肝膽實火上炎，頭痛目赤，脅痛口苦，耳聾耳腫；濕熱下注，陰腫陰癢，筋痿陰汗，小便淋濁。', 
 '用於急性結膜炎、急性中耳炎、急性膽囊炎等屬肝膽實火者。'),
('F0003', '補中益氣湯', '脾胃論', '黃耆、甘草、人參、當歸、橘皮、升麻、柴胡、白朮', 
 '補中益氣，升陽舉陷。', '脾胃氣虛，中氣下陷，體倦乏力，食少腹脹，久瀉脫肛，子宮脫垂。', 
 '用於慢性胃炎、胃下垂、子宮脫垂、直腸脫垂等屬中氣下陷者。');

-- 插入秘方範例資料
INSERT IGNORE INTO secret_formulas (id, name, origin_text, composition, effect, indication, application) VALUES
('001', '家傳調胃秘方', '祖傳秘方', '白朮、茯苓、陳皮、半夏、甘草、人參、生薑', '健脾胃，化濕濁，調氣機。', 
 '脾胃虛弱，消化不良，腹脹納少，大便溏薄。', '家傳秘方，專治脾胃虛弱諸症，效果顯著。'),
('002', '秘製安神湯', '師傳秘方', '酸棗仁、龍骨、牡蠣、茯神、遠志、當歸、甘草', '養心安神，鎮靜安眠。', 
 '心神不寧，失眠多夢，驚悸怔忡，健忘。', '師傳秘方，專治各種失眠症狀，安神效果極佳。'),
('003', '祖傳止咳秘方', '祖傳秘方', '川貝、枇杷葉、桔梗、甘草、杏仁、陳皮、半夏', '潤肺止咳，化痰平喘。', 
 '肺燥咳嗽，痰少難咯，咽乾口燥，或痰多咳喘。', '祖傳三代秘方，治療各種咳嗽症狀，療效確切。'),
('004', '活血化瘀秘方', '家傳秘方', '丹參、紅花、桃仁、川芎、當歸、赤芍、乳香、沒藥', '活血化瘀，通經止痛。', 
 '血瘀氣滯，胸脅疼痛，跌打損傷，瘀血腫痛。', '家傳活血秘方，專治各種瘀血證候。'),
('005', '補腎壯陽秘方', '師傳秘方', '淫羊藿、巴戟天、肉蓯蓉、杜仲、續斷、菟絲子、枸杞子', '補腎壯陽，強筋健骨。', 
 '腎陽虛衰，陽痿早洩，腰膝酸軟，畏寒肢冷。', '師傳補腎秘方，專治腎陽虛諸症。');

-- 插入藥材範例資料
INSERT IGNORE INTO medicines (id, name, origin_text, nature_flavor, effect, indication, application) VALUES
('M0001', '人參', '神農本草經', '味甘、微苦，性溫。歸脾、肺、心、腎經。', '大補元氣，復脈固脫，補脾益肺，生津安神。', 
 '體虛欲脫，肢冷脈微，脾虛食少，肺虛喘咳，津傷口渴，內熱消渴，久病虛羸，驚悸失眠，陽痿宮冷。', 
 '用於休克、心力衰竭、神經衰弱等。每日3-9克，煎服。'),
('M0002', '甘草', '神農本草經', '味甘，性平。歸脾、胃、心、肺經。', '補脾益氣，清熱解毒，祛痰止咳，緩急止痛，調和諸藥。', 
 '脾胃虛弱，倦怠乏力，心悸氣短，咳嗽痰多，脘腹、四肢攣急疼痛，癰腫瘡毒。', 
 '用於胃及十二指腸潰瘍、支氣管炎等。每日2-10克，煎服。'),
('M0003', '黃耆', '神農本草經', '味甘，性溫。歸脾、肺經。', '補氣固表，利尿托毒，排膿，斂瘡生肌。', 
 '氣虛乏力，食少便溏，中氣下陷，久瀉脫肛，便血崩漏，表虛自汗，氣虛水腫，癰疽難潰，久潰不斂，血虛痿黃。', 
 '用於慢性腎炎、糖尿病、高血壓等。每日9-30克，煎服。'),
('M0004', '當歸', '神農本草經', '味甘、辛，性溫。歸肝、心、脾經。', '補血活血，調經止痛，潤燥滑腸。', 
 '血虛諸證，月經不調，經閉痛經，虛寒腹痛，風濕痹痛，跌撲損傷，癰疽瘡瘍，腸燥便秘。', 
 '用於貧血、月經不調、跌打損傷等。每日6-12克，煎服。'),
('M0005', '白朮', '神農本草經', '味甘、苦，性溫。歸脾、胃經。', '補氣健脾，燥濕利水，止汗，安胎。', 
 '脾胃氣虛，消化不良，泄瀉，水腫，自汗，胎動不安。', 
 '用於慢性胃炎、慢性腹瀉、水腫等。每日6-12克，煎服。');
 
 -- 為方劑表添加注意事項及副作用欄位
ALTER TABLE formulas ADD COLUMN warnings_side_effects TEXT AFTER application;

-- 為單味藥表添加注意事項及副作用欄位
ALTER TABLE medicines ADD COLUMN warnings_side_effects TEXT AFTER application;

-- 為秘方表添加注意事項及副作用欄位
ALTER TABLE secret_formulas ADD COLUMN warnings_side_effects TEXT AFTER application;