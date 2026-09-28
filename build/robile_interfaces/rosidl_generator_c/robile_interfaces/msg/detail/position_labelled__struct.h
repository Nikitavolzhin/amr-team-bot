// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from robile_interfaces:msg/PositionLabelled.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__STRUCT_H_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'name'
#include "rosidl_runtime_c/string.h"
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/PositionLabelled in the package robile_interfaces.
typedef struct robile_interfaces__msg__PositionLabelled
{
  rosidl_runtime_c__String name;
  geometry_msgs__msg__Point position;
} robile_interfaces__msg__PositionLabelled;

// Struct for a sequence of robile_interfaces__msg__PositionLabelled.
typedef struct robile_interfaces__msg__PositionLabelled__Sequence
{
  robile_interfaces__msg__PositionLabelled * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} robile_interfaces__msg__PositionLabelled__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED__STRUCT_H_
