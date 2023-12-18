resource "aws_db_instance" "vs-backend-database" {
  allocated_storage       = 20
  max_allocated_storage   = 40
  backup_retention_period = 7
  db_subnet_group_name    = aws_db_subnet_group.vs-backend-rds-subnet-group.id
  vpc_security_group_ids  = ["${aws_security_group.vs-backend-rds-sg.id}"]
  engine                  = "postgres"
  engine_version          = "15.2"
  identifier              = local.app_env
  instance_class          = var.rds_instance_class
  multi_az                = false
  username                = var.rds_username
  db_name                 = var.rds_db_name
  password                = var.rds_password
  port                    = 5432
  publicly_accessible     = false
  storage_encrypted       = true
  storage_type            = "gp2"
  skip_final_snapshot     = true

  tags = {
    Name        = "${local.app_env}-db-instance"
    Environment = "${var.environment}"
  }
}
