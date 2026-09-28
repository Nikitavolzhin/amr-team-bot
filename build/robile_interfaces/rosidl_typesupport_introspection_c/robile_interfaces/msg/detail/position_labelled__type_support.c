// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from robile_interfaces:msg/PositionLabelled.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "robile_interfaces/msg/detail/position_labelled__rosidl_typesupport_introspection_c.h"
#include "robile_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "robile_interfaces/msg/detail/position_labelled__functions.h"
#include "robile_interfaces/msg/detail/position_labelled__struct.h"


// Include directives for member types
// Member `name`
#include "rosidl_runtime_c/string_functions.h"
// Member `position`
#include "geometry_msgs/msg/point.h"
// Member `position`
#include "geometry_msgs/msg/detail/point__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  robile_interfaces__msg__PositionLabelled__init(message_memory);
}

void robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_fini_function(void * message_memory)
{
  robile_interfaces__msg__PositionLabelled__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_member_array[2] = {
  {
    "name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robile_interfaces__msg__PositionLabelled, name),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "position",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robile_interfaces__msg__PositionLabelled, position),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_members = {
  "robile_interfaces__msg",  // message namespace
  "PositionLabelled",  // message name
  2,  // number of fields
  sizeof(robile_interfaces__msg__PositionLabelled),
  robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_member_array,  // message members
  robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_init_function,  // function to initialize message memory (memory has to be allocated)
  robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_type_support_handle = {
  0,
  &robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_robile_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, robile_interfaces, msg, PositionLabelled)() {
  robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Point)();
  if (!robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_type_support_handle.typesupport_identifier) {
    robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &robile_interfaces__msg__PositionLabelled__rosidl_typesupport_introspection_c__PositionLabelled_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
