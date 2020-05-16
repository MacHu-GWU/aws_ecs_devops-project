output "lb_arn" {
  value = aws_lb.elb.arn
}

output "target_group_a_arn" {
  value = module.lbd_a.target_group_arn
}

output "target_group_b_arn" {
  value = module.lbd_b.target_group_arn
}

output "target_group_c_arn" {
  value = module.lbd_c.target_group_arn
}
