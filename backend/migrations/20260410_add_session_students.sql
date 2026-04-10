-- 添加课程实例-学生关联表
-- 执行时间：2026-04-10

-- 创建课程实例-学生关联表
CREATE TABLE IF NOT EXISTS `session_students` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `session_id` BIGINT NOT NULL COMMENT '课程实例ID',
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `enrolled_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    FOREIGN KEY (`session_id`) REFERENCES `class_sessions`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_session_student` (`session_id`, `student_id`),
    INDEX `idx_session` (`session_id`),
    INDEX `idx_student` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程实例-学生关联表';