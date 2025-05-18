def test_snake_case() -> None:
    from betterproto2_compiler.casing import snake_case

    # Simple renaming
    assert snake_case("methodName") == "method_name"
    assert snake_case("MethodName") == "method_name"

    # Don't break acronyms
    assert snake_case("HTTPRequest") == "http_request"
    assert snake_case("RequestHTTP") == "request_http"
    assert snake_case("HTTPRequest2") == "http_request_2"
    assert snake_case("RequestHTTP2") == "request_http_2"
    assert snake_case("GetAResponse") == "get_a_response"

    # Split digits
    assert snake_case("Get2025Results") == "get_2025_results"
    assert snake_case("Get10yResults") == "get_10y_results"

    # If the name already contains an underscore or is lowercase, don't change it at all.
    # There is a risk of breaking names otherwise.
    assert snake_case("aaa_123_bbb") == "aaa_123_bbb"
    assert snake_case("aaa_123bbb") == "aaa_123bbb"
    assert snake_case("aaa123_bbb") == "aaa123_bbb"
    assert snake_case("get_HTTP_response") == "get_HTTP_response"
    assert snake_case("_methodName") == "_methodName"
    assert snake_case("make_gRPC_request") == "make_gRPC_request"

    assert snake_case("value1") == "value1"
    assert snake_case("value1string") == "value1string"

    # It is difficult to cover all the cases with a simple algorithm...
    # "GetValueAsUInt32" -> "get_value_as_u_int_32"
