// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from robile_interfaces:msg/PositionLabelledArray.idl
// generated code does not contain a copyright notice

#ifndef ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__BUILDER_HPP_
#define ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "robile_interfaces/msg/detail/position_labelled_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace robile_interfaces
{

namespace msg
{

namespace builder
{

class Init_PositionLabelledArray_positions
{
public:
  explicit Init_PositionLabelledArray_positions(::robile_interfaces::msg::PositionLabelledArray & msg)
  : msg_(msg)
  {}
  ::robile_interfaces::msg::PositionLabelledArray positions(::robile_interfaces::msg::PositionLabelledArray::_positions_type arg)
  {
    msg_.positions = std::move(arg);
    return std::move(msg_);
  }

private:
  ::robile_interfaces::msg::PositionLabelledArray msg_;
};

class Init_PositionLabelledArray_header
{
public:
  Init_PositionLabelledArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PositionLabelledArray_positions header(::robile_interfaces::msg::PositionLabelledArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_PositionLabelledArray_positions(msg_);
  }

private:
  ::robile_interfaces::msg::PositionLabelledArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::robile_interfaces::msg::PositionLabelledArray>()
{
  return robile_interfaces::msg::builder::Init_PositionLabelledArray_header();
}

}  // namespace robile_interfaces

#endif  // ROBILE_INTERFACES__MSG__DETAIL__POSITION_LABELLED_ARRAY__BUILDER_HPP_
