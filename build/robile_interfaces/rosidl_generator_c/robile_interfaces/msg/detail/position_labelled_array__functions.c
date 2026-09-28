// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from robile_interfaces:msg/PositionLabelledArray.idl
// generated code does not contain a copyright notice
#include "robile_interfaces/msg/detail/position_labelled_array__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `positions`
#include "robile_interfaces/msg/detail/position_labelled__functions.h"

bool
robile_interfaces__msg__PositionLabelledArray__init(robile_interfaces__msg__PositionLabelledArray * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    robile_interfaces__msg__PositionLabelledArray__fini(msg);
    return false;
  }
  // positions
  if (!robile_interfaces__msg__PositionLabelled__Sequence__init(&msg->positions, 0)) {
    robile_interfaces__msg__PositionLabelledArray__fini(msg);
    return false;
  }
  return true;
}

void
robile_interfaces__msg__PositionLabelledArray__fini(robile_interfaces__msg__PositionLabelledArray * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // positions
  robile_interfaces__msg__PositionLabelled__Sequence__fini(&msg->positions);
}

bool
robile_interfaces__msg__PositionLabelledArray__are_equal(const robile_interfaces__msg__PositionLabelledArray * lhs, const robile_interfaces__msg__PositionLabelledArray * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // positions
  if (!robile_interfaces__msg__PositionLabelled__Sequence__are_equal(
      &(lhs->positions), &(rhs->positions)))
  {
    return false;
  }
  return true;
}

bool
robile_interfaces__msg__PositionLabelledArray__copy(
  const robile_interfaces__msg__PositionLabelledArray * input,
  robile_interfaces__msg__PositionLabelledArray * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // positions
  if (!robile_interfaces__msg__PositionLabelled__Sequence__copy(
      &(input->positions), &(output->positions)))
  {
    return false;
  }
  return true;
}

robile_interfaces__msg__PositionLabelledArray *
robile_interfaces__msg__PositionLabelledArray__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  robile_interfaces__msg__PositionLabelledArray * msg = (robile_interfaces__msg__PositionLabelledArray *)allocator.allocate(sizeof(robile_interfaces__msg__PositionLabelledArray), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(robile_interfaces__msg__PositionLabelledArray));
  bool success = robile_interfaces__msg__PositionLabelledArray__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
robile_interfaces__msg__PositionLabelledArray__destroy(robile_interfaces__msg__PositionLabelledArray * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    robile_interfaces__msg__PositionLabelledArray__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
robile_interfaces__msg__PositionLabelledArray__Sequence__init(robile_interfaces__msg__PositionLabelledArray__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  robile_interfaces__msg__PositionLabelledArray * data = NULL;

  if (size) {
    data = (robile_interfaces__msg__PositionLabelledArray *)allocator.zero_allocate(size, sizeof(robile_interfaces__msg__PositionLabelledArray), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = robile_interfaces__msg__PositionLabelledArray__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        robile_interfaces__msg__PositionLabelledArray__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
robile_interfaces__msg__PositionLabelledArray__Sequence__fini(robile_interfaces__msg__PositionLabelledArray__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      robile_interfaces__msg__PositionLabelledArray__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

robile_interfaces__msg__PositionLabelledArray__Sequence *
robile_interfaces__msg__PositionLabelledArray__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  robile_interfaces__msg__PositionLabelledArray__Sequence * array = (robile_interfaces__msg__PositionLabelledArray__Sequence *)allocator.allocate(sizeof(robile_interfaces__msg__PositionLabelledArray__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = robile_interfaces__msg__PositionLabelledArray__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
robile_interfaces__msg__PositionLabelledArray__Sequence__destroy(robile_interfaces__msg__PositionLabelledArray__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    robile_interfaces__msg__PositionLabelledArray__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
robile_interfaces__msg__PositionLabelledArray__Sequence__are_equal(const robile_interfaces__msg__PositionLabelledArray__Sequence * lhs, const robile_interfaces__msg__PositionLabelledArray__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!robile_interfaces__msg__PositionLabelledArray__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
robile_interfaces__msg__PositionLabelledArray__Sequence__copy(
  const robile_interfaces__msg__PositionLabelledArray__Sequence * input,
  robile_interfaces__msg__PositionLabelledArray__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(robile_interfaces__msg__PositionLabelledArray);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    robile_interfaces__msg__PositionLabelledArray * data =
      (robile_interfaces__msg__PositionLabelledArray *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!robile_interfaces__msg__PositionLabelledArray__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          robile_interfaces__msg__PositionLabelledArray__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!robile_interfaces__msg__PositionLabelledArray__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
