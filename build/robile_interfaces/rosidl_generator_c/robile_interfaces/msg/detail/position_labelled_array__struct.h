// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from robile_interfaces:msg/PositionLabelledArray.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__STRUCT_H_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'positions'
#include "robile_interfaces/msg/detail/position_labelled__struct.h"

/// Struct defined in msg/PositionLabelledArray in the package robile_interfaces.
typedef struct robile_interfaces__msg__PositionLabelledArray
{
  std_msgs__msg__Header header;
  robile_interfaces__msg__PositionLabelled__Sequence positions;
} robile_interfaces__msg__PositionLabelledArray;

// Struct for a sequence of robile_interfaces__msg__PositionLabelledArray.
typedef struct robile_interfaces__msg__PositionLabelledArray__Sequence
{
  robile_interfaces__msg__PositionLabelledArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} robile_interfaces__msg__PositionLabelledArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__STRUCT_H_
