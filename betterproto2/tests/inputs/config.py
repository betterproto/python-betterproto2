# Test cases that are expected to fail, e.g. unimplemented features or bug-fixes.
# Remove from list when fixed.
xfail = {
    "namespace_keywords",  # 70
    "googletypes_struct",  # 9
    "googletypes_value",  # 9
}

services = {
    "googletypes_request",
    "googletypes_response",
    "googletypes_response_embedded",
    "service",
    "service_separate_packages",
    "import_service_input_message",
    "googletypes_service_returns_empty",
    "googletypes_service_returns_googletype",
    "example_service",
    "empty_service",
    "service_uppercase",
}
