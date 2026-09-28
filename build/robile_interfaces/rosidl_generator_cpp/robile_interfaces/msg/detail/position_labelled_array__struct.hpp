// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from robile_interfaces:msg/PositionLabelledArray.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__STRUCT_HPP_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'positions'
#include "robile_interfaces/msg/detail/position_labelled__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__robile_interfaces__msg__PositionLabelledArray __attribute__((deprecated))
#else
# define DEPRECATED__robile_interfaces__msg__PositionLabelledArray __declspec(deprecated)
#endif

namespace robile_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct PositionLabelledArray_
{
  using Type = PositionLabelledArray_<ContainerAllocator>;

  explicit PositionLabelledArray_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    (void)_init;
  }

  explicit PositionLabelledArray_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _positions_type =
    std::vector<robile_interfaces::msg::PositionLabelled_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<robile_interfaces::msg::PositionLabelled_<ContainerAllocator>>>;
  _positions_type positions;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__positions(
    const std::vector<robile_interfaces::msg::PositionLabelled_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<robile_interfaces::msg::PositionLabelled_<ContainerAllocator>>> & _arg)
  {
    this->positions = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator> *;
  using ConstRawPtr =
    const robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__robile_interfaces__msg__PositionLabelledArray
    std::shared_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__robile_interfaces__msg__PositionLabelledArray
    std::shared_ptr<robile_interfaces::msg::PositionLabelledArray_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PositionLabelledArray_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->positions != other.positions) {
      return false;
    }
    return true;
  }
  bool operator!=(const PositionLabelledArray_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PositionLabelledArray_

// alias to use template instance with default allocator
using PositionLabelledArray =
  robile_interfaces::msg::PositionLabelledArray_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace robile_interfaces

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__STRUCT_HPP_
