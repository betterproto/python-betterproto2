# Google Protobuf Descriptors

Google's protoc plugin for Python generated DESCRIPTOR fields that enable reflection capabilities in many libraries (e.g. grpc, grpclib, mcap).

By default, betterproto2 doesn't generate these as it introduces a dependency on `protobuf`. If you're okay with this dependency and want to generate DESCRIPTORs, use the compiler option `python_betterproto2_opt=google_protobuf_descriptors`.
