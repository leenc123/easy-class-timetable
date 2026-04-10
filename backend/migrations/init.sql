-- 补习班排课表系统数据库初始化脚本
-- 创建时间：2026-04-09

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 机构表
-- ----------------------------
DROP TABLE IF EXISTS `organizations`;
CREATE TABLE `organizations` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(200) NOT NULL COMMENT '机构名称',
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '机构编码',
    `address` VARCHAR(500) COMMENT '地址',
    `contact_phone` VARCHAR(20) COMMENT '联系电话',
    `contact_email` VARCHAR(100) COMMENT '联系邮箱',
    `logo_url` VARCHAR(500) COMMENT 'Logo URL',
    `description` TEXT COMMENT '机构描述',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_code` (`code`),
    INDEX `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='机构表';

-- ----------------------------
-- 用户表
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT COMMENT '所属机构ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `real_name` VARCHAR(100) NOT NULL COMMENT '真实姓名',
    `phone` VARCHAR(20) COMMENT '手机号',
    `email` VARCHAR(100) COMMENT '邮箱',
    `role` ENUM('super_admin', 'org_admin', 'teacher', 'student_parent') NOT NULL DEFAULT 'teacher' COMMENT '角色',
    `avatar_url` VARCHAR(500) COMMENT '头像URL',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `last_login_at` TIMESTAMP COMMENT '最后登录时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE SET NULL,
    INDEX `idx_username` (`username`),
    INDEX `idx_org` (`org_id`),
    INDEX `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ----------------------------
-- 教室表
-- ----------------------------
DROP TABLE IF EXISTS `classrooms`;
CREATE TABLE `classrooms` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL COMMENT '所属机构ID',
    `name` VARCHAR(100) NOT NULL COMMENT '教室名称',
    `code` VARCHAR(50) COMMENT '教室编码',
    `capacity` INT NOT NULL DEFAULT 30 COMMENT '容量',
    `location` VARCHAR(200) COMMENT '位置',
    `equipment` JSON COMMENT '设备列表',
    `description` TEXT COMMENT '描述',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    INDEX `idx_org` (`org_id`),
    INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教室表';

-- ----------------------------
-- 教师表
-- ----------------------------
DROP TABLE IF EXISTS `teachers`;
CREATE TABLE `teachers` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL COMMENT '所属机构ID',
    `user_id` BIGINT UNIQUE COMMENT '关联用户ID',
    `name` VARCHAR(100) NOT NULL COMMENT '教师姓名',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `email` VARCHAR(100) COMMENT '邮箱',
    `subjects` JSON COMMENT '可教授科目',
    `max_hours_per_week` INT DEFAULT 20 COMMENT '每周最大课时',
    `bio` VARCHAR(500) COMMENT '简介',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_org` (`org_id`),
    INDEX `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师表';

-- ----------------------------
-- 教师可用时间表
-- ----------------------------
DROP TABLE IF EXISTS `teacher_availability`;
CREATE TABLE `teacher_availability` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `teacher_id` BIGINT NOT NULL COMMENT '教师ID',
    `day_of_week` INT NOT NULL COMMENT '星期几 0-6',
    `start_time` TIME NOT NULL COMMENT '开始时间',
    `end_time` TIME NOT NULL COMMENT '结束时间',
    `is_recurring` BOOLEAN DEFAULT TRUE COMMENT '是否每周重复',
    `specific_date` DATE COMMENT '具体日期',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE CASCADE,
    INDEX `idx_teacher` (`teacher_id`),
    INDEX `idx_date` (`specific_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师可用时间表';

-- ----------------------------
-- 学生表
-- ----------------------------
DROP TABLE IF EXISTS `students`;
CREATE TABLE `students` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL COMMENT '所属机构ID',
    `user_id` BIGINT COMMENT '关联用户ID（家长账号）',
    `name` VARCHAR(100) NOT NULL COMMENT '学生姓名',
    `grade` VARCHAR(20) COMMENT '年级',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `parent_name` VARCHAR(100) COMMENT '家长姓名',
    `parent_phone` VARCHAR(20) COMMENT '家长电话',
    `notes` VARCHAR(500) COMMENT '备注',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_org` (`org_id`),
    INDEX `idx_grade` (`grade`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生表';

-- ----------------------------
-- 学生学科课时表
-- ----------------------------
DROP TABLE IF EXISTS `student_subject_hours`;
CREATE TABLE `student_subject_hours` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `subject` VARCHAR(50) NOT NULL COMMENT '学科名称',
    `total_lessons` DECIMAL(10,1) NOT NULL DEFAULT 0 COMMENT '总课时（1课时=120分钟）',
    `remaining_lessons` DECIMAL(10,1) NOT NULL DEFAULT 0 COMMENT '剩余课时',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_student_subject` (`student_id`, `subject`),
    INDEX `idx_student` (`student_id`),
    INDEX `idx_subject` (`subject`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生学科课时表';

-- ----------------------------
-- 课程表
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL COMMENT '所属机构ID',
    `name` VARCHAR(200) NOT NULL COMMENT '课程名称',
    `code` VARCHAR(50) COMMENT '课程编码',
    `subject` VARCHAR(50) NOT NULL COMMENT '科目',
    `duration_minutes` INT NOT NULL DEFAULT 60 COMMENT '单次课时长',
    `min_students` INT DEFAULT 1 COMMENT '最少学生数',
    `max_students` INT DEFAULT 30 COMMENT '最多学生数',
    `required_equipment` JSON COMMENT '所需设备',
    `description` VARCHAR(500) COMMENT '描述',
    `status` ENUM('active', 'inactive', 'completed') DEFAULT 'active' COMMENT '状态',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    INDEX `idx_org` (`org_id`),
    INDEX `idx_subject` (`subject`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- ----------------------------
-- 课程-教师关联表
-- ----------------------------
DROP TABLE IF EXISTS `course_teachers`;
CREATE TABLE `course_teachers` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `course_id` BIGINT NOT NULL,
    `teacher_id` BIGINT NOT NULL,
    `is_primary` BOOLEAN DEFAULT FALSE COMMENT '是否主教',
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_course_teacher` (`course_id`, `teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-教师关联表';

-- ----------------------------
-- 课程-学生关联表
-- ----------------------------
DROP TABLE IF EXISTS `course_students`;
CREATE TABLE `course_students` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `course_id` BIGINT NOT NULL,
    `student_id` BIGINT NOT NULL,
    `enrolled_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
    `status` ENUM('enrolled', 'completed', 'dropped') DEFAULT 'enrolled' COMMENT '状态',
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_course_student` (`course_id`, `student_id`),
    INDEX `idx_student` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-学生关联表';

-- ----------------------------
-- 排课周期表
-- ----------------------------
DROP TABLE IF EXISTS `scheduling_cycles`;
CREATE TABLE `scheduling_cycles` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL COMMENT '所属机构ID',
    `name` VARCHAR(100) NOT NULL COMMENT '周期名称',
    `cycle_days` INT NOT NULL COMMENT '周期天数',
    `start_date` DATE NOT NULL COMMENT '开始日期',
    `end_date` DATE COMMENT '结束日期',
    `description` TEXT COMMENT '描述',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    INDEX `idx_org` (`org_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='排课周期表';

-- ----------------------------
-- 周期-日期映射表
-- ----------------------------
DROP TABLE IF EXISTS `cycle_dates`;
CREATE TABLE `cycle_dates` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `cycle_id` BIGINT NOT NULL,
    `cycle_day` INT NOT NULL COMMENT '周期中的第几天',
    `actual_date` DATE NOT NULL COMMENT '实际日期',
    FOREIGN KEY (`cycle_id`) REFERENCES `scheduling_cycles`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_cycle_date` (`cycle_id`, `actual_date`),
    INDEX `idx_date` (`actual_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='周期-日期映射表';

-- ----------------------------
-- 时间段定义表
-- ----------------------------
DROP TABLE IF EXISTS `time_slots`;
CREATE TABLE `time_slots` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL COMMENT '所属机构ID',
    `name` VARCHAR(50) NOT NULL COMMENT '时间段名称',
    `start_time` VARCHAR(10) NOT NULL COMMENT '开始时间 HH:MM',
    `end_time` VARCHAR(10) NOT NULL COMMENT '结束时间 HH:MM',
    `display_order` INT NOT NULL DEFAULT 1 COMMENT '显示顺序',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    INDEX `idx_org` (`org_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='时间段定义表';

-- ----------------------------
-- 课程实例表
-- ----------------------------
DROP TABLE IF EXISTS `class_sessions`;
CREATE TABLE `class_sessions` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL COMMENT '所属机构ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `teacher_id` BIGINT NOT NULL COMMENT '教师ID',
    `classroom_id` BIGINT NOT NULL COMMENT '教室ID',
    `cycle_id` BIGINT COMMENT '周期ID',
    `cycle_day` INT COMMENT '周期中的第几天',
    `session_date` DATE NOT NULL COMMENT '上课日期',
    `time_slot_id` BIGINT NOT NULL COMMENT '时间段ID',
    `status` ENUM('scheduled', 'completed', 'cancelled', 'rescheduled') DEFAULT 'scheduled' COMMENT '状态',
    `notes` TEXT COMMENT '备注',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`),
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`),
    FOREIGN KEY (`classroom_id`) REFERENCES `classrooms`(`id`),
    FOREIGN KEY (`cycle_id`) REFERENCES `scheduling_cycles`(`id`),
    FOREIGN KEY (`time_slot_id`) REFERENCES `time_slots`(`id`),
    INDEX `idx_date` (`session_date`),
    INDEX `idx_cycle` (`cycle_id`, `cycle_day`),
    INDEX `idx_teacher_date` (`teacher_id`, `session_date`),
    INDEX `idx_classroom_date` (`classroom_id`, `session_date`),
    UNIQUE KEY `uk_teacher_timeslot` (`teacher_id`, `session_date`, `time_slot_id`),
    UNIQUE KEY `uk_classroom_timeslot` (`classroom_id`, `session_date`, `time_slot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程实例表';

-- ----------------------------
-- 学生出勤表
-- ----------------------------
DROP TABLE IF EXISTS `student_attendances`;
CREATE TABLE `student_attendances` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `session_id` BIGINT NOT NULL,
    `student_id` BIGINT NOT NULL,
    `attendance_status` ENUM('present', 'absent', 'late', 'excused') DEFAULT 'present' COMMENT '出勤状态',
    FOREIGN KEY (`session_id`) REFERENCES `class_sessions`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_session_student` (`session_id`, `student_id`),
    INDEX `idx_student` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生出勤表';

-- ----------------------------
-- 课程盘点表
-- ----------------------------
DROP TABLE IF EXISTS `session_checkins`;
CREATE TABLE `session_checkins` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `session_id` BIGINT NOT NULL UNIQUE COMMENT '课程实例ID',
    `teacher_id` BIGINT NOT NULL COMMENT '填写教师ID',
    `expected_count` INT NOT NULL COMMENT '应到人数',
    `actual_count` INT NOT NULL COMMENT '实到人数',
    `notes` TEXT COMMENT '备注',
    `checkin_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '盘点时间',
    FOREIGN KEY (`session_id`) REFERENCES `class_sessions`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`),
    INDEX `idx_session` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程盘点表';

-- ----------------------------
-- 排课冲突日志表
-- ----------------------------
DROP TABLE IF EXISTS `scheduling_conflicts`;
CREATE TABLE `scheduling_conflicts` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
    `org_id` BIGINT NOT NULL,
    `session_id` BIGINT COMMENT '课程实例ID',
    `conflict_type` ENUM('classroom', 'teacher', 'student', 'time') NOT NULL COMMENT '冲突类型',
    `conflicting_resource_type` VARCHAR(50) NOT NULL COMMENT '冲突资源类型',
    `conflicting_resource_id` BIGINT NOT NULL COMMENT '冲突资源ID',
    `conflicting_session_id` BIGINT COMMENT '冲突的课程实例ID',
    `description` TEXT NOT NULL COMMENT '冲突描述',
    `resolved` BOOLEAN DEFAULT FALSE COMMENT '是否已解决',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`org_id`) REFERENCES `organizations`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`session_id`) REFERENCES `class_sessions`(`id`) ON DELETE SET NULL,
    INDEX `idx_session` (`session_id`),
    INDEX `idx_resolved` (`resolved`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='排课冲突日志表';

-- ----------------------------
-- 初始数据
-- ----------------------------
-- 插入默认机构
INSERT INTO `organizations` (`name`, `code`, `description`) VALUES
('示范培训机构', 'DEMO001', '系统演示机构') ON DUPLICATE KEY UPDATE name=name;

-- 默认用户由应用程序启动时自动创建
-- admin / admin123 (超级管理员)
-- org_admin / org123 (机构管理员)

SET FOREIGN_KEY_CHECKS = 1;