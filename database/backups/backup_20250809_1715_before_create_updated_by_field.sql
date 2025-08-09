-- MySQL dump 10.13  Distrib 8.0.15, for Win64 (x86_64)
--
-- Host: localhost    Database: scheduler_db
-- ------------------------------------------------------
-- Server version	8.0.15

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('5ddd0e85e3a2');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedules`
--

DROP TABLE IF EXISTS `schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `schedules` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '時段 ID',
  `role` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色：GIVER=提供者、TAKER=預約者',
  `giver_id` int(10) unsigned NOT NULL COMMENT 'Giver ID',
  `taker_id` int(10) unsigned DEFAULT NULL COMMENT 'Taker ID，可為 NULL',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'DRAFT' COMMENT '時段狀態',
  `date` date NOT NULL COMMENT '時段日期',
  `start_time` time NOT NULL COMMENT '開始時間',
  `end_time` time NOT NULL COMMENT '結束時間',
  `note` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '備註',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  `deleted_at` datetime DEFAULT NULL COMMENT '軟刪除標記',
  `updated_by` int(10) unsigned DEFAULT NULL COMMENT '最後更新者的使用者 ID，可為 NULL（表示系統自動更新）',
  PRIMARY KEY (`id`),
  KEY `ix_schedules_id` (`id`),
  KEY `fk_schedules_giver_id` (`giver_id`),
  KEY `fk_schedules_taker_id` (`taker_id`),
  KEY `fk_schedules_updated_by` (`updated_by`),
  CONSTRAINT `fk_schedules_giver_id` FOREIGN KEY (`giver_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_schedules_taker_id` FOREIGN KEY (`taker_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_schedules_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedules`
--

LOCK TABLES `schedules` WRITE;
/*!40000 ALTER TABLE `schedules` DISABLE KEYS */;
INSERT INTO `schedules` VALUES (1,'TAKER',1,1,'AVAILABLE','2025-08-14','10:09:00','22:00:00',NULL,'2025-08-09 10:17:10','2025-08-09 10:17:10',NULL,NULL),(2,'TAKER',1,1,'AVAILABLE','2025-08-16','20:00:00','22:00:00',NULL,'2025-08-09 10:17:37','2025-08-09 10:17:37',NULL,NULL),(3,'TAKER',1,1,'AVAILABLE','2025-08-15','10:00:00','22:00:00',NULL,'2025-08-09 11:06:57','2025-08-09 11:06:57',NULL,NULL),(4,'TAKER',14,1,'AVAILABLE','2025-08-16','20:00:00','22:00:00',NULL,'2025-08-09 11:07:16','2025-08-09 11:07:16',NULL,NULL),(5,'TAKER',14,1,'AVAILABLE','2025-08-23','20:00:00','22:00:00',NULL,'2025-08-09 11:28:11','2025-08-09 11:28:11',NULL,NULL),(6,'TAKER',14,1,'AVAILABLE','2025-08-20','11:11:00','22:00:00',NULL,'2025-08-09 15:35:50','2025-08-09 15:35:50',NULL,NULL),(7,'TAKER',14,1,'AVAILABLE','2025-08-18','20:00:00','22:00:00',NULL,'2025-08-09 15:37:12','2025-08-09 15:37:12',NULL,NULL),(8,'TAKER',1,1,'AVAILABLE','2025-08-19','20:00:00','22:00:00',NULL,'2025-08-09 16:57:58','2025-08-09 16:57:58',NULL,NULL),(9,'TAKER',1,1,'AVAILABLE','2025-08-12','10:00:00','22:00:00',NULL,'2025-08-09 17:13:44','2025-08-09 17:13:44',NULL,NULL);
/*!40000 ALTER TABLE `schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '使用者 ID',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '使用者姓名',
  `email` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '電子信箱（唯一）',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  `deleted_at` datetime DEFAULT NULL COMMENT '軟刪除標記',
  `updated_by` int(10) unsigned DEFAULT NULL COMMENT '最後更新者的使用者 ID，可為 NULL（表示系統自動更新）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `ix_users_id` (`id`),
  KEY `fk_users_updated_by` (`updated_by`),
  CONSTRAINT `fk_users_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'測試 Giver 1','giver1@test.com','2025-08-06 22:44:22','2025-08-06 22:44:22',NULL,NULL),(2,'測試 Giver 2','giver2@test.com','2025-08-06 22:44:22','2025-08-06 22:44:22',NULL,NULL),(3,'測試 Taker 1','taker1@test.com','2025-08-06 22:44:22','2025-08-06 22:44:22',NULL,NULL),(4,'測試 Taker 2','taker2@test.com','2025-08-06 22:44:22','2025-08-06 22:44:22',NULL,NULL),(5,'','invalid-email','2025-08-07 21:44:18','2025-08-07 21:44:18',NULL,NULL),(6,'王零六','wang零六@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(7,'王零七','wang零七@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(8,'王零八','wang零八@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(9,'王零九','wang零九@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(10,'王拾','wang拾@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(11,'王拾一','wang拾一@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(12,'王拾二','wang拾二@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(13,'王拾三','wang拾三@example.com','2025-08-08 02:07:45','2025-08-08 02:07:45',NULL,NULL),(14,'王拾四','wang拾四@example.com','2025-08-08 20:16:19','2025-08-08 20:16:19',NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-09 17:15:43
