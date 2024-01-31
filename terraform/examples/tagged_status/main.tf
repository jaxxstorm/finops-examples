resource "vantage_segment" "tagged_status" {
  title             = "Tagged Status"
  description       = "Shows the tagged status of AWS resources"
  priority          = 1
  track_unallocated = false
}

resource "vantage_segment" "aws_tagged" {
    title = "Tagged AWS Resources"
    description = "Segment containing all tagged resources"
    priority = 1
    parent_segment_token = vantage_segment.tagged_status.token
}

resource "vantage_segment" "aws_untagged" {
    title = "Untagged AWS Resources"
    description = "Segment containing all tagged resources"
    priority = 10
    filter = "(costs.provider = 'aws' AND tags.name = NULL)"
    parent_segment_token = vantage_segment.tagged_status.token
}


