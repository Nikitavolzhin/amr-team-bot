// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from robile_interfaces:msg/PositionLabelledArray.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__FUNCTIONS_H_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "robile_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "robile_interfaces/msg/detail/position_labelled_array__struct.h"

/// Initialize msg/PositionLabelledArray message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * robile_interfaces__msg__PositionLabelledArray
 * )) before or use
 * robile_interfaces__msg__PositionLabelledArray__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
bool
robile_interfaces__msg__PositionLabelledArray__init(robile_interfaces__msg__PositionLabelledArray * msg);

/// Finalize msg/PositionLabelledArray message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
void
robile_interfaces__msg__PositionLabelledArray__fini(robile_interfaces__msg__PositionLabelledArray * msg);

/// Create msg/PositionLabelledArray message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * robile_interfaces__msg__PositionLabelledArray__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
robile_interfaces__msg__PositionLabelledArray *
robile_interfaces__msg__PositionLabelledArray__create();

/// Destroy msg/PositionLabelledArray message.
/**
 * It calls
 * robile_interfaces__msg__PositionLabelledArray__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
void
robile_interfaces__msg__PositionLabelledArray__destroy(robile_interfaces__msg__PositionLabelledArray * msg);

/// Check for msg/PositionLabelledArray message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
bool
robile_interfaces__msg__PositionLabelledArray__are_equal(const robile_interfaces__msg__PositionLabelledArray * lhs, const robile_interfaces__msg__PositionLabelledArray * rhs);

/// Copy a msg/PositionLabelledArray message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
bool
robile_interfaces__msg__PositionLabelledArray__copy(
  const robile_interfaces__msg__PositionLabelledArray * input,
  robile_interfaces__msg__PositionLabelledArray * output);

/// Initialize array of msg/PositionLabelledArray messages.
/**
 * It allocates the memory for the number of elements and calls
 * robile_interfaces__msg__PositionLabelledArray__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
bool
robile_interfaces__msg__PositionLabelledArray__Sequence__init(robile_interfaces__msg__PositionLabelledArray__Sequence * array, size_t size);

/// Finalize array of msg/PositionLabelledArray messages.
/**
 * It calls
 * robile_interfaces__msg__PositionLabelledArray__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
void
robile_interfaces__msg__PositionLabelledArray__Sequence__fini(robile_interfaces__msg__PositionLabelledArray__Sequence * array);

/// Create array of msg/PositionLabelledArray messages.
/**
 * It allocates the memory for the array and calls
 * robile_interfaces__msg__PositionLabelledArray__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
robile_interfaces__msg__PositionLabelledArray__Sequence *
robile_interfaces__msg__PositionLabelledArray__Sequence__create(size_t size);

/// Destroy array of msg/PositionLabelledArray messages.
/**
 * It calls
 * robile_interfaces__msg__PositionLabelledArray__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
void
robile_interfaces__msg__PositionLabelledArray__Sequence__destroy(robile_interfaces__msg__PositionLabelledArray__Sequence * array);

/// Check for msg/PositionLabelledArray message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
bool
robile_interfaces__msg__PositionLabelledArray__Sequence__are_equal(const robile_interfaces__msg__PositionLabelledArray__Sequence * lhs, const robile_interfaces__msg__PositionLabelledArray__Sequence * rhs);

/// Copy an array of msg/PositionLabelledArray messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_robile_interfaces
bool
robile_interfaces__msg__PositionLabelledArray__Sequence__copy(
  const robile_interfaces__msg__PositionLabelledArray__Sequence * input,
  robile_interfaces__msg__PositionLabelledArray__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__FUNCTIONS_H_
