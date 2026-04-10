-- 添加学生学科学时表
-- 执行时间：2026-04-10
-- 说明：支持学生多学科学时配置，上课签到时自动扣除

-- ----------------------------
-- 学生学科学时表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `student_subject_hours` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `subject` VARCHAR(50) NOT NULL COMMENT '学科名称',
    `total_hours` INT NOT NULL DEFAULT 0 COMMENT '总学时（分钟）',
    `remaining_hours` INT NOT NULL DEFAULT 0 COMMENT '剩余学时（分钟）',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_student_subject` (`student_id`, `subject`),
    INDEX `idx_student` (`student_id`),
    INDEX `idx_subject` (`subject`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生学科学时表';