locals {
    filter = <<FILTER
    (costs.provider = 'aws' AND costs.service IN ('Amazon Elastic Compute Cloud - Compute', 'Savings Plans for AWS Compute usage'))
FILTER
}

resource "vantage_cost_report" "amortized_compute_breakdown" {
  filter       = local.filter
  title        = "Compute Costs w/ Savings Plans"
}