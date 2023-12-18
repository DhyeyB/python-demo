resource "aws_cognito_user_pool" "user-pool" {
  name = "${local.app_env}"

  # username_attributes = ["email"]

  # mfa_configuration = "ON"

  # software_token_mfa_configuration {
  #   enabled = true
  # }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  email_configuration {
    email_sending_account = "DEVELOPER" # You can also use SES for custom emails
    from_email_address = "Virtu Sign <support@dev-email.virtu-sign.com>"
    reply_to_email_address = "donotreply@dev-email.virtu-sign.com"
    source_arn = var.email_configuration_source_arn
  }

   # Enable email verification
  auto_verified_attributes = ["email"]
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }

  #schema {
  #  attribute_data_type = "String"
  #  name               = "email"
  #  required           = true
  #  mutable            = true
  #}


  tags = {
    Name        = "${local.app_env}-cognito-up"
    Environment = "${var.environment}"
  }

  lifecycle {

    ignore_changes = [
      password_policy,
      schema
    ]
  }

  schema {
  attribute_data_type      = "String"
      developer_only_attribute = false
      mutable                  = true
      name                     = "email"
      required                 = true

      string_attribute_constraints {
        min_length = 1
        max_length = 256
      }
  }

}

resource "aws_cognito_identity_provider" "google_provider" {
  user_pool_id  = aws_cognito_user_pool.user-pool.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    authorize_scopes = "profile email openid"
    client_id        = var.google_client_id
    client_secret    = var.google_client_secret
  }

  attribute_mapping = {
    "email_verified" = "email_verified"
    "name"           = "name"
    "family_name"    = "family_name"
    "given_name"     = "given_name"
    "email"          = "email"
    "username"       = "sub"
  }

  depends_on = [
    aws_cognito_user_pool.user-pool
 ]

}


resource "aws_cognito_user_pool_client" "app-client" {
  name                          = "${local.app_env}-app-client"
  user_pool_id                  = aws_cognito_user_pool.user-pool.id
  generate_secret               = false
  supported_identity_providers  = ["COGNITO", "Google"]
  explicit_auth_flows           = ["ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH", "ALLOW_USER_PASSWORD_AUTH", "ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_CUSTOM_AUTH"]
  prevent_user_existence_errors = "LEGACY"

  allowed_oauth_flows = ["implicit"]
  allowed_oauth_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "phone",
    "profile",
  ]

  access_token_validity = 3600
  id_token_validity = 60
  refresh_token_validity = 30

  token_validity_units {
    access_token = "seconds"
    id_token = "minutes"
    refresh_token = "days"
  }

  callback_urls = [var.cognito_callback_urls]

  logout_urls = [var.cognito_logout_urls]

}

# resource "aws_cognito_user_pool_domain" "main" {
#   domain = var.frontend_endpoint
#   certificate_arn = data.aws_acm_certificate.frontend_certificate.arn
#   user_pool_id    = aws_cognito_user_pool.user-pool.id
# }
