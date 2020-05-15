resource "aws_lambda_function" "lbd" {
  filename = "${var.DEPLOYMENT_FILE}"
  function_name = "${var.ENVIRONMENT_NAME}-${var.LOGIC_ID}"
  role = "${var.IAM_ROLE_ARN}"
  handler = "handler.main"
  source_code_hash = "${filebase64sha256("${var.DEPLOYMENT_FILE}")}"
  runtime = "python3.6"
}

resource "aws_lb_target_group" "lbd" {
  name = "${var.ENVIRONMENT_NAME}-${var.LOGIC_ID}"
  target_type = "lambda"
}


resource "aws_lambda_permission" "lbd_with_lb" {
  statement_id  = "AllowExecutionFromlb"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lbd.function_name}"
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = "${aws_lb_target_group.lbd.arn}"
  depends_on       = [
    "aws_lambda_function.lbd",
    "aws_lb_target_group.lbd"
  ]
}

resource "aws_lb_target_group_attachment" "lbd" {
  target_group_arn = "${aws_lb_target_group.lbd.arn}"
  target_id        = "${aws_lambda_function.lbd.arn}"
  depends_on       = [
    "aws_lambda_permission.lbd_with_lb"
  ]
}
