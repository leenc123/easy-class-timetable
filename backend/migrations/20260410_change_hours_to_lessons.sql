-- 将学时改为课时（1课时=120分钟）
-- 执行时间：2026-04-10

-- 修改字段名、类型和注释
ALTER TABLE `student_subject_hours`
  CHANGE COLUMN `total_hours` `total_lessons` DECIMAL(10,1) NOT NULL DEFAULT 0 COMMENT '总课时（1课时=120分钟）',
  CHANGE COLUMN `remaining_hours` `remaining_lessons` DECIMAL(10,1) NOT NULL DEFAULT 0 COMMENT '剩余课时';