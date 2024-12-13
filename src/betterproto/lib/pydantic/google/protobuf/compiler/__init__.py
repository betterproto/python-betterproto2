# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: google/protobuf/compiler/plugin.proto
# plugin: python-betterproto
# This file has been @generated

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass

from typing import List

import betterproto
import betterproto.lib.pydantic.google.protobuf as betterproto_lib_pydantic_google_protobuf


class CodeGeneratorResponseFeature(betterproto.Enum):
    """Sync with code_generator.h."""

    FEATURE_NONE = 0
    FEATURE_PROTO3_OPTIONAL = 1
    FEATURE_SUPPORTS_EDITIONS = 2


@dataclass(eq=False, repr=False)
class Version(betterproto.Message):
    """The version number of protocol compiler."""

    major: int = betterproto.int32_field(1)
    minor: int = betterproto.int32_field(2)
    patch: int = betterproto.int32_field(3)
    suffix: str = betterproto.string_field(4)
    """
    A suffix for alpha, beta or rc release, e.g., "alpha-1", "rc2". It should
     be empty for mainline stable releases.
    """


@dataclass(eq=False, repr=False)
class CodeGeneratorRequest(betterproto.Message):
    """An encoded CodeGeneratorRequest is written to the plugin's stdin."""

    file_to_generate: List[str] = betterproto.string_field(1)
    """
    The .proto files that were explicitly listed on the command-line.  The
     code generator should generate code only for these files.  Each file's
     descriptor will be included in proto_file, below.
    """

    parameter: str = betterproto.string_field(2)
    """The generator parameter passed on the command-line."""

    proto_file: List["betterproto_lib_pydantic_google_protobuf.FileDescriptorProto"] = betterproto.message_field(15)
    """
    FileDescriptorProtos for all files in files_to_generate and everything
     they import.  The files will appear in topological order, so each file
     appears before any file that imports it.
    
     Note: the files listed in files_to_generate will include runtime-retention
     options only, but all other files will include source-retention options.
     The source_file_descriptors field below is available in case you need
     source-retention options for files_to_generate.
    
     protoc guarantees that all proto_files will be written after
     the fields above, even though this is not technically guaranteed by the
     protobuf wire format.  This theoretically could allow a plugin to stream
     in the FileDescriptorProtos and handle them one by one rather than read
     the entire set into memory at once.  However, as of this writing, this
     is not similarly optimized on protoc's end -- it will store all fields in
     memory at once before sending them to the plugin.
    
     Type names of fields and extensions in the FileDescriptorProto are always
     fully qualified.
    """

    source_file_descriptors: List["betterproto_lib_pydantic_google_protobuf.FileDescriptorProto"] = (
        betterproto.message_field(17)
    )
    """
    File descriptors with all options, including source-retention options.
     These descriptors are only provided for the files listed in
     files_to_generate.
    """

    compiler_version: "Version" = betterproto.message_field(3)
    """The version number of protocol compiler."""


@dataclass(eq=False, repr=False)
class CodeGeneratorResponse(betterproto.Message):
    """The plugin writes an encoded CodeGeneratorResponse to stdout."""

    error: str = betterproto.string_field(1)
    """
    Error message.  If non-empty, code generation failed.  The plugin process
     should exit with status code zero even if it reports an error in this way.
    
     This should be used to indicate errors in .proto files which prevent the
     code generator from generating correct code.  Errors which indicate a
     problem in protoc itself -- such as the input CodeGeneratorRequest being
     unparseable -- should be reported by writing a message to stderr and
     exiting with a non-zero status code.
    """

    supported_features: int = betterproto.uint64_field(2)
    """
    A bitmask of supported features that the code generator supports.
     This is a bitwise "or" of values from the Feature enum.
    """

    minimum_edition: int = betterproto.int32_field(3)
    """
    The minimum edition this plugin supports.  This will be treated as an
     Edition enum, but we want to allow unknown values.  It should be specified
     according the edition enum value, *not* the edition number.  Only takes
     effect for plugins that have FEATURE_SUPPORTS_EDITIONS set.
    """

    maximum_edition: int = betterproto.int32_field(4)
    """
    The maximum edition this plugin supports.  This will be treated as an
     Edition enum, but we want to allow unknown values.  It should be specified
     according the edition enum value, *not* the edition number.  Only takes
     effect for plugins that have FEATURE_SUPPORTS_EDITIONS set.
    """

    file: List["CodeGeneratorResponseFile"] = betterproto.message_field(15)


@dataclass(eq=False, repr=False)
class CodeGeneratorResponseFile(betterproto.Message):
    """Represents a single generated file."""

    name: str = betterproto.string_field(1)
    """
    The file name, relative to the output directory.  The name must not
     contain "." or ".." components and must be relative, not be absolute (so,
     the file cannot lie outside the output directory).  "/" must be used as
     the path separator, not "\".
    
     If the name is omitted, the content will be appended to the previous
     file.  This allows the generator to break large files into small chunks,
     and allows the generated text to be streamed back to protoc so that large
     files need not reside completely in memory at one time.  Note that as of
     this writing protoc does not optimize for this -- it will read the entire
     CodeGeneratorResponse before writing files to disk.
    """

    insertion_point: str = betterproto.string_field(2)
    """
    If non-empty, indicates that the named file should already exist, and the
     content here is to be inserted into that file at a defined insertion
     point.  This feature allows a code generator to extend the output
     produced by another code generator.  The original generator may provide
     insertion points by placing special annotations in the file that look
     like:
       @@protoc_insertion_point(NAME)
     The annotation can have arbitrary text before and after it on the line,
     which allows it to be placed in a comment.  NAME should be replaced with
     an identifier naming the point -- this is what other generators will use
     as the insertion_point.  Code inserted at this point will be placed
     immediately above the line containing the insertion point (thus multiple
     insertions to the same point will come out in the order they were added).
     The double-@ is intended to make it unlikely that the generated code
     could contain things that look like insertion points by accident.
    
     For example, the C++ code generator places the following line in the
     .pb.h files that it generates:
       // @@protoc_insertion_point(namespace_scope)
     This line appears within the scope of the file's package namespace, but
     outside of any particular class.  Another plugin can then specify the
     insertion_point "namespace_scope" to generate additional classes or
     other declarations that should be placed in this scope.
    
     Note that if the line containing the insertion point begins with
     whitespace, the same whitespace will be added to every line of the
     inserted text.  This is useful for languages like Python, where
     indentation matters.  In these languages, the insertion point comment
     should be indented the same amount as any inserted code will need to be
     in order to work correctly in that context.
    
     The code generator that generates the initial file and the one which
     inserts into it must both run as part of a single invocation of protoc.
     Code generators are executed in the order in which they appear on the
     command line.
    
     If |insertion_point| is present, |name| must also be present.
    """

    content: str = betterproto.string_field(15)
    """The file contents."""

    generated_code_info: "betterproto_lib_pydantic_google_protobuf.GeneratedCodeInfo" = betterproto.message_field(16)
    """
    Information describing the file content being inserted. If an insertion
     point is used, this information will be appropriately offset and inserted
     into the code generation metadata for the generated files.
    """


CodeGeneratorRequest.__pydantic_model__.update_forward_refs()  # type: ignore
CodeGeneratorResponse.__pydantic_model__.update_forward_refs()  # type: ignore
CodeGeneratorResponseFile.__pydantic_model__.update_forward_refs()  # type: ignore
