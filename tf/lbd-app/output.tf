output "lb_arn" {
  value = aws_lb.elb.arn
}

output "target_group_a_arn" {
  value = module.lbd_a.target_group_arn
}
