// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from robile_interfaces:msg/PositionLabelled.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "robile_interfaces/msg/detail/position_labelled__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace robile_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void PositionLabelled_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) robile_interfaces::msg::PositionLabelled(_init);
}

void PositionLabelled_fini_function(void * message_memory)
{
  auto typed_message = static_cast<robile_interfaces::msg::PositionLabelled *>(message_memory);
  typed_message->~PositionLabelled();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember PositionLabelled_message_member_array[2] = {
  {
    "name",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robile_interfaces::msg::PositionLabelled, name),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "position",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Point>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robile_interfaces::msg::PositionLabelled, position),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers PositionLabelled_message_members = {
  "robile_interfaces::msg",  // message namespace
  "PositionLabelled",  // message name
  2,  // number of fields
  sizeof(robile_interfaces::msg::PositionLabelled),
  PositionLabelled_message_member_array,  // message members
  PositionLabelled_init_function,  // function to initialize message memory (memory has to be allocated)
  PositionLabelled_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t PositionLabelled_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &PositionLabelled_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace robile_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<robile_interfaces::msg::PositionLabelled>()
{
  return &::robile_interfaces::msg::rosidl_typesupport_introspection_cpp::PositionLabelled_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, robile_interfaces, msg, PositionLabelled)() {
  return &::robile_interfaces::msg::rosidl_typesupport_introspection_cpp::PositionLabelled_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
