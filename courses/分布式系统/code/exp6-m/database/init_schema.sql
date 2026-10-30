CREATE DATABASE IF NOT EXISTS experiment6;
USE experiment6;

-- 用户画像表
CREATE TABLE IF NOT EXISTS user_profile (
    user_id VARCHAR(50) PRIMARY KEY,
    ip_address VARCHAR(45),
    visit_count INT DEFAULT 1,
    first_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    preferred_content_type ENUM('text', 'image', 'video', 'mixed') DEFAULT 'mixed',
    interest_tags TEXT,
    ai_analysis_result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 访问日志表
CREATE TABLE IF NOT EXISTS access_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    request_method VARCHAR(10),
    request_path VARCHAR(500),
    request_headers TEXT,
    response_status INT,
    response_time_ms INT,
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- 内容生成记录表
CREATE TABLE IF NOT EXISTS content_generation (
    generation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    request_path VARCHAR(500),
    ai_prompt TEXT,
    ai_response TEXT,
    generated_html TEXT,
    generation_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);