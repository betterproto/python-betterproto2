# Google Protobuf Descriptors

Google's protoc plugin for Python generated DESCRIPTOR fields that enable reflection capabilities in many libraries (e.g. grpc, grpclib, mcap).

By default, betterproto2 doesn't generate these as it introduces a dependency on `protobuf`. If you're okay with this dependency and want to generate DESCRIPTORs, use the compiler option `python_betterproto2_opt=google_protobuf_descriptors`.


## grpclib Reflection

In order to properly use reflection right now, you will need to modify the `DescriptorPool` that is used by grpclib's `ServerReflection`. To do so, take a look at the use of `ServerReflection.extend` in the `test_grpclib_reflection` test in https://github.com/vmagamedov/grpclib/blob/master/tests/grpc/test_grpclib_reflection.py
 In the future, once https://github.com/vmagamedov/grpclib/pull/204 is merged, you will be able to pass the `default_google_proto_descriptor_pool` into the `ServerReflection.extend` class method.
