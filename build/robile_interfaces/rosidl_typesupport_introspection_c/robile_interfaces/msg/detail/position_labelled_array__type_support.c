// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from robile_interfaces:msg/PositionLabelledArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "robile_interfaces/msg/detail/position_labelled_array__rosidl_typesupport_introspection_c.h"
#include "robile_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "robile_interfaces/msg/detail/position_labelled_array__functions.h"
#include "robile_interfaces/msg/detail/position_labelled_array__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `positions`
#include "robile_interfaces/msg/position_labelled.h"
// Member `positions`
#include "robile_interfaces/msg/detail/position_labelled__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  robile_interfaces__msg__PositionLabelledArray__init(message_memory);
}

void robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_fini_function(void * message_memory)
{
  robile_interfaces__msg__PositionLabelledArray__fini(message_memory);
}

size_t robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__size_function__PositionLabelledArray__positions(
  const void * untyped_member)
{
  const robile_interfaces__msg__PositionLabelled__Sequence * member =
    (const robile_interfaces__msg__PositionLabelled__Sequence *)(untyped_member);
  return member->size;
}

const void * robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__get_const_function__PositionLabelledArray__positions(
  const void * untyped_member, size_t index)
{
  const robile_interfaces__msg__PositionLabelled__Sequence * member =
    (const robile_interfaces__msg__PositionLabelled__Sequence *)(untyped_member);
  return &member->data[index];
}

void * robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__get_function__PositionLabelledArray__positions(
  void * untyped_member, size_t index)
{
  robile_interfaces__msg__PositionLabelled__Sequence * member =
    (robile_interfaces__msg__PositionLabelled__Sequence *)(untyped_member);
  return &member->data[index];
}

void robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__fetch_function__PositionLabelledArray__positions(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const robile_interfaces__msg__PositionLabelled * item =
    ((const robile_interfaces__msg__PositionLabelled *)
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__get_const_function__PositionLabelledArray__positions(untyped_member, index));
  robile_interfaces__msg__PositionLabelled * value =
    (robile_interfaces__msg__PositionLabelled *)(untyped_value);
  *value = *item;
}

void robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__assign_function__PositionLabelledArray__positions(
  void * untyped_member, size_t index, const void * untyped_value)
{
  robile_interfaces__msg__PositionLabelled * item =
    ((robile_interfaces__msg__PositionLabelled *)
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__get_function__PositionLabelledArray__positions(untyped_member, index));
  const robile_interfaces__msg__PositionLabelled * value =
    (const robile_interfaces__msg__PositionLabelled *)(untyped_value);
  *item = *value;
}

bool robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__resize_function__PositionLabelledArray__positions(
  void * untyped_member, size_t size)
{
  robile_interfaces__msg__PositionLabelled__Sequence * member =
    (robile_interfaces__msg__PositionLabelled__Sequence *)(untyped_member);
  robile_interfaces__msg__PositionLabelled__Sequence__fini(member);
  return robile_interfaces__msg__PositionLabelled__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robile_interfaces__msg__PositionLabelledArray, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "positions",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robile_interfaces__msg__PositionLabelledArray, positions),  // bytes offset in struct
    NULL,  // default value
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__size_function__PositionLabelledArray__positions,  // size() function pointer
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__get_const_function__PositionLabelledArray__positions,  // get_const(index) function pointer
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__get_function__PositionLabelledArray__positions,  // get(index) function pointer
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__fetch_function__PositionLabelledArray__positions,  // fetch(index, &value) function pointer
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__assign_function__PositionLabelledArray__positions,  // assign(index, value) function pointer
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__resize_function__PositionLabelledArray__positions  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_members = {
  "robile_interfaces__msg",  // message namespace
  "PositionLabelledArray",  // message name
  2,  // number of fields
  sizeof(robile_interfaces__msg__PositionLabelledArray),
  robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_member_array,  // message members
  robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_init_function,  // function to initialize message memory (memory has to be allocated)
  robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_type_support_handle = {
  0,
  &robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_robile_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, robile_interfaces, msg, PositionLabelledArray)() {
  robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, robile_interfaces, msg, PositionLabelled)();
  if (!robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_type_support_handle.typesupport_identifier) {
    robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &robile_interfaces__msg__PositionLabelledArray__rosidl_typesupport_introspection_c__PositionLabelledArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
