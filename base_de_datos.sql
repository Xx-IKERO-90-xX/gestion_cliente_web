-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: 192.168.1.99    Database: GESTION_USUARIOS
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `CLIENTES`
--

DROP TABLE IF EXISTS `CLIENTES`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CLIENTES` (
  `dni` varchar(20) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `apellidos` varchar(200) NOT NULL,
  `direccion` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(200) NOT NULL,
  `telefono` varchar(200) NOT NULL,
  `googlemap_link` varchar(400) NOT NULL,
  PRIMARY KEY (`dni`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CLIENTES`
--

/*!40000 ALTER TABLE `CLIENTES` DISABLE KEYS */;
INSERT INTO `CLIENTES` VALUES ('47820080K','Iker Javier','Rodriguez Hernandez','Calle mis cojones p22','iker@gmail.com','434235231','https://maps.app.goo.gl/oqzRBKhwmKerdJyeA   '),('55945354Q','Samy','Hernandez Bramy','Alicante, Calle Oscar Espla Puerta 22','samyhernandez@gmail.com','543534634643','https://maps.app.goo.gl/ALPH7GFjzuhWb1rb7'),('63598206D','Juanma','Garcia Hernandez','Calle alfonso el sabio p22','juanmanuel@gmail.com','555342534222222','https://maps.app.goo.gl/v12nmstxQNqjRCKXA');
/*!40000 ALTER TABLE `CLIENTES` ENABLE KEYS */;

--
-- Table structure for table `USUARIOS`
--

DROP TABLE IF EXISTS `USUARIOS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USUARIOS` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(200) NOT NULL,
  `passwd` varchar(200) NOT NULL,
  `role` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `USUARIOS`
--

/*!40000 ALTER TABLE `USUARIOS` DISABLE KEYS */;
INSERT INTO `USUARIOS` VALUES (7,'ikero@empresa.com','$pbkdf2-sha256$29000$QehdSwmBUOo9x/hfS0kJIQ$9aaXOfsufmnLk05FKfEicXytzGgUQalxY/1q2XyKXG4','Administrador'),(8,'admin@empresa.com','$pbkdf2-sha256$29000$HSNkjBFiTEnpnRNiDEFIaQ$tqYvgUMC9y7b7Sew4UqSif6bsZY6hi4DQ9r04ouMt9Q','Administrador'),(9,'empleado1@empresa.com','$pbkdf2-sha256$29000$IkTovZey1to7hzDG.P8/hw$2e0fLD4MIWgFb1qMozVKAgAt4Tgx6hTxYAX8kl5ScNE','Empleado'),(10,'empleado2@empresa.com','$pbkdf2-sha256$29000$FMIYozSGkHIOwXgPIaT03g$01kTwDtMNYHt642123riJLQ//Uh3j79sLytcgVDTq/k','Empleado');
/*!40000 ALTER TABLE `USUARIOS` ENABLE KEYS */;

--
-- Dumping routines for database 'GESTION_USUARIOS'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-10  1:24:51
