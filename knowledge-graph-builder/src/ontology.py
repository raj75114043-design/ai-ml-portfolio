NODE_TYPES = {"Site", "Activity", "Material", "Vendor"}
RELATIONSHIPS = {
    ("Site", "HAS_ACTIVITY", "Activity"),
    ("Activity", "USES_MATERIAL", "Material"),
    ("Material", "SUPPLIED_BY", "Vendor"),
}
