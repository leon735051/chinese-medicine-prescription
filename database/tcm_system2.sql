-- 為方劑表添加注意事項及副作用欄位
USE chinese_medicine_db;
ALTER TABLE formulas ADD COLUMN warnings_side_effects TEXT AFTER application;

-- 為單味藥表添加注意事項及副作用欄位
ALTER TABLE medicines ADD COLUMN warnings_side_effects TEXT AFTER application;

-- 為秘方表添加注意事項及副作用欄位
ALTER TABLE secret_formulas ADD COLUMN warnings_side_effects TEXT AFTER application;