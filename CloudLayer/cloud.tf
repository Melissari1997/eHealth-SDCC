# create a zip of your deployment with terraform called Cloud.zipls


provider "aws"{
    region = "us-east-1"
    access_key = "******"
    secret_key = "******"
}

resource "aws_dynamodb_table" "table1" {
  name           = "ospedali"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Id"

  
  attribute {
      name = "Id"
      type = "N"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  
    }
    
}

resource "aws_dynamodb_table" "table2" {
  name           = "pazienti"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Id"

  
  attribute {
      name = "Id"
      type = "N"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  
    }
    
}

resource "aws_dynamodb_table" "table3" {
  name           = "pazientiuscita"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Id"

  
  attribute {
      name = "Id"
      type = "N"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  
    }
    
}

resource "aws_dynamodb_table" "table4" {
  name           = "tempi"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Id"

  
  attribute {
      name = "Id"
      type = "N"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  
    }
    
}

resource "aws_dynamodb_table" "table5" {
  name           = "email"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Id"

  
  attribute {
      name = "Id"
      type = "N"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  
    }
    
}

resource "aws_dynamodb_table_item" "item" {
    table_name     = aws_dynamodb_table.table1.name
    hash_key       = aws_dynamodb_table.table1.hash_key
    
    for_each = {
    item0 = {
        id = 0,
        nome ="POLICLINICO GEMELLI"
        lat ="41.9305036"
        long ="12.4266098"
        numa = 10
    }
    item1 = {
        id = 1,
        nome ="OSPEDALE BAMBINO GESU'"
        lat ="41.8568957"
        long ="12.4133241"
        numa = 10
    }
    item2 = {
        id = 2,
        nome ="AZIENDA POLICLINICO UMBERTO I"
        lat ="41.9058155"
        long ="12.5124896"
        numa = 10
    }
    item3 = {
        id = 3,
        nome ="OSPEDALE CRISTO RE"
        lat ="41.9183312"
        long ="12.4184249"
        numa = 10
    }
    item4 = {
        id = 4,
        nome ="OSPEDALE S. EUGENIO"
        lat ="41.8212895"
        long ="12.4699554"
        numa = 10
    }
    item5 = {
        id = 5,
        nome ="OSPEDALE S. GIOVANNI BATTISTA"
        lat ="41.8275917"
        long ="12.414652"
        numa = 10
    }
    item6 = {
        id = 6,
        nome ="OSPEDALE S. SPIRITO"
        lat ="41.9008379"
        long ="12.460502"
        numa = 10
    }
    item7 = {
        id = 7,
        nome ="OSPEDALE SAN CARLO DI NANCY"
        lat ="41.8976962"
        long ="12.4368588"
        numa = 10
    }
    item8 = {
        id = 8,
        nome ="OSPEDALE SANDRO PERTINI"
        lat ="41.9203789"
        long ="12.5379549"
        numa = 10
    }
    item9 = {
        id = 9,
        nome ="OSPEDALE SANT'ANDREA"
        lat ="41.9826679"
        long ="12.4682322"
        numa = 10
    }
    item10 = {
        id = 10,
        nome ="POLICLINICO CASILINO"
        lat ="41.8687872"
        long ="12.5878892"
        numa = 10
    }
    item11 = {
        id = 11,
        nome ="POLICLINICO TOR VERGATA"
        lat ="41.9203789"
        long ="12.5379549"
        numa = 10
    }
  }
  item = <<EOF
{
  "Id": {"N": "${each.value.id}"},
  "Nome": {"S": "${each.value.nome}"},
  "Lat": {"S": "${each.value.lat}"},
  "Long": {"S": "${each.value.long}"},
  "NumA": {"N": "${each.value.numa}"}
}
EOF
}

resource "aws_s3_bucket" "dist_bucket" {
  bucket = "cloudb"
  acl    = "private"
}


resource "aws_s3_bucket_object" "dist_item" {
    key = "key"
    bucket = "${aws_s3_bucket.dist_bucket.id}"
    source = "Cloud.zip"
}

resource "aws_elastic_beanstalk_application" "app"{
    name = "cloud"
    
}

resource "aws_elastic_beanstalk_application_version" "application" {
  name        = aws_elastic_beanstalk_application.app.name
  application = aws_elastic_beanstalk_application.app.name
  description = "application version created by terraform"
  bucket      = "${aws_s3_bucket.dist_bucket.id}"
  key         = "${aws_s3_bucket_object.dist_item.id}"
}

resource "aws_elastic_beanstalk_environment" "environment" {
  name                = "Sdcc-environment"
  application         = aws_elastic_beanstalk_application_version.application.name
  solution_stack_name = "64bit Amazon Linux 2 v3.1.2 running Python 3.7"
  cname_prefix = "cloud-service"
  setting {
        namespace = "aws:autoscaling:launchconfiguration"
        name      = "IamInstanceProfile"
        value     = "aws-elasticbeanstalk-ec2-role"
      }

  setting{
      namespace = "aws:elasticbeanstalk:container:python"
      name = "NumThreads"
      value = 110
  }

  setting{
      namespace = "aws:autoscaling:asg"
      name = "MaxSize"
      value = 3
  }

  setting{
      namespace = "aws:autoscaling:trigger"
      name = "MeasureName"
      value = "RequestCount"
  }

  setting{
      namespace = "aws:autoscaling:trigger"
      name = "Statistic"
      value = "Sum"
  }

  setting{
      namespace = "aws:autoscaling:trigger"
      name = "Unit"
      value = "Count"
  }

  setting{
      namespace = "aws:autoscaling:trigger"
      name = "EvaluationPeriods"
      value = 3
  }

  setting{
      namespace = "aws:autoscaling:trigger"
      name = "LowerThreshold"
      value = 100
  }

  setting{
      namespace = "aws:autoscaling:trigger"
      name = "UpperThreshold"
      value = 300
  }

  setting{
      namespace = "aws:autoscaling:trigger"
      name = "Period"
      value = 1
  }



}
