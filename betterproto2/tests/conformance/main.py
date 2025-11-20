import struct
import sys

import betterproto2
from tests.outputs.conformance.conformance import (
    ConformanceRequest,
    ConformanceResponse,
    TestCategory,
    WireFormat,
)
from tests.outputs.conformance.protobuf_test_messages.proto3 import TestAllTypesProto3

test_count = 0
verbose = False


class ProtocolError(Exception):
    pass


def do_test(request: ConformanceRequest) -> ConformanceResponse:
    response = ConformanceResponse()

    # is_json = betterproto2.which_one_of(request, "payload")[0] == "json_payload"

    if request.message_type != "protobuf_test_messages.proto3.TestAllTypesProto3":
        return ConformanceResponse(skipped="non proto3 tests not supported")

    try:
        if betterproto2.which_one_of(request, "payload")[0] == "protobuf_payload":
            try:
                test_message = TestAllTypesProto3.parse(request.protobuf_payload)
            except Exception as e:
                response.parse_error = str(e)
                return response

        elif betterproto2.which_one_of(request, "payload")[0] == "json_payload":
            try:
                ignore_unknown_fields = request.test_category == TestCategory.JSON_IGNORE_UNKNOWN_PARSING_TEST
                test_message = TestAllTypesProto3.from_json(
                    request.json_payload, ignore_unknown_fields=ignore_unknown_fields
                )
            except Exception as e:
                response.parse_error = str(e)
                return response

        elif betterproto2.which_one_of(request, "payload")[0] == "text_payload":
            return ConformanceResponse(skipped="text input not supported")

        else:
            raise ProtocolError("Request didn't have payload.")

        if request.requested_output_format == WireFormat.UNSPECIFIED:
            raise ProtocolError("Unspecified output format")

        elif request.requested_output_format == WireFormat.PROTOBUF:
            response.protobuf_payload = bytes(test_message)

        elif request.requested_output_format == WireFormat.JSON:
            try:
                response.json_payload = test_message.to_json()
            except Exception as e:
                response.serialize_error = str(e)
                return response

        elif request.requested_output_format == WireFormat.TEXT_FORMAT:
            return ConformanceResponse(skipped="text output not supported")
            # response.text_payload = text_format.MessageToString(
            #     test_message, print_unknown_fields=request.print_unknown_fields
            # )

    except Exception as e:
        response.runtime_error = str(e)

    return response


def do_test_io():
    length_bytes = sys.stdin.buffer.read(4)
    if len(length_bytes) == 0:
        return False  # EOF
    elif len(length_bytes) != 4:
        raise OSError("I/O error")

    length = struct.unpack("<I", length_bytes)[0]
    serialized_request = sys.stdin.buffer.read(length)
    if len(serialized_request) != length:
        raise OSError("I/O error")

    request = ConformanceRequest.parse(serialized_request)

    response = do_test(request)

    serialized_response = bytes(response)
    sys.stdout.buffer.write(struct.pack("<I", len(serialized_response)))
    sys.stdout.buffer.write(serialized_response)
    sys.stdout.buffer.flush()

    # if verbose:
    #   sys.stderr.write(
    #       "conformance_python: request=%s, response=%s\n"
    #       % (
    #           request.ShortDebugString().c_str(),
    #           response.ShortDebugString().c_str(),
    #       )
    #   )

    global test_count
    test_count += 1

    return True


while True:
    if not do_test_io():
        print("conformance_python: received EOF from test runner after", test_count, "tests, exiting\n", file=sys.stderr)
        sys.exit(0)
