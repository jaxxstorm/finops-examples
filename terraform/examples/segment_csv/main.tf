locals {
  csv_content = file("${path.module}/business_units_example.csv")
  csv_data    = csvdecode(local.csv_content)

  # Grouping by business unit
  business_units = distinct([for row in local.csv_data : row.business_unit])

  # Grouping cost centers under each business unit and removing duplicates
  cost_centers = { for bu in local.business_units : 
                     bu => distinct([for row in local.csv_data : row.cost_center if row.business_unit == bu]) 
                 }

  # Flatten the structure for easy iteration
  cost_center_flat = flatten([
    for bu, ccs in local.cost_centers : [
      for cc in ccs : {
        business_unit = bu,
        cost_center   = cc
      }
    ]
  ])

  account_ids_per_cost_center = { 
    for row in local.csv_data : 
      "${row.business_unit}-${row.cost_center}" => row.account_id... 
  }

  # Making sure each list of account IDs is unique
  unique_account_ids_per_cost_center = {
    for key, ids in local.account_ids_per_cost_center :
    key => distinct(ids)
  }

}

resource "vantage_segment" "business_units" {
  title = "Business Units"
}

resource "vantage_segment" "business_unit" {
  for_each = toset(local.business_units)

  title    = each.value
  parent_segment_token = vantage_segment.business_units.token
  priority = 50
}

# Create a resource for each cost center under each business unit
resource "vantage_segment" "cost_center" {
  for_each = { for item in local.cost_center_flat : "${item.business_unit}-${item.cost_center}" => item }

  title    = each.value.cost_center
  priority = 50
  parent_segment_token = vantage_segment.business_unit[each.value.business_unit].token
  filter = format("costs.provider = 'aws' AND (%s)", join(" OR ", [for id in local.unique_account_ids_per_cost_center["${each.value.business_unit}-${each.value.cost_center}"] : "costs.account_id = '${id}'"]))
  
}
