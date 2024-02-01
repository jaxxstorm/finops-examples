locals {
    svcs = yamldecode(file("${path.module}/services.yaml"))
}

# output "services" {
#     value = local.svcs
# }

# top level services segment
resource "vantage_segment" "services" {
  title = "Services"
  track_unallocated = true
}

resource "vantage_segment" "service" {
  for_each = local.svcs.services

  title = each.key
  parent_segment_token = vantage_segment.services.token
  filter = format("costs.provider = 'aws' AND (tags.name = 'Group' AND tags.value = '%s') AND (tags.name = 'Service' AND tags.value = '%s') AND (tags.name = 'Team' AND tags.value = '%s')", each.value.Group, each.value.Service, each.value.Team )
}

